import dataclasses
import logging
import time
from typing import List, Optional, Tuple
from urllib.parse import urlencode, urlparse
import torch.utils.data
import irisml.core
from irisml.tasks.create_azure_openai_completion_model import OpenAIClientBase

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a model that generates text using Azure OpenAI completion API.

    This task calls Azure OpenAI Chat Completion API.
    https://docs.microsoft.com/en-us/azure/cognitive-services/openai-gpt/quickstart

    Currently this implementation supports a single system message and a single user message.

    The model interface is:
    - Input: (str, [])
    - Output: str | dict, depending on the value of config include_content_filter_results

    Config:
        endpoint (str): Azure endpoint
        deployment_name (str): Azure deployment name
        api_version (str): OpenAI API version, default is 2023-03-15-preview
        api_key (str): Azure API key
        temperature (float): Temperature parameter for text generation
        max_tokens (int): Maximum number of tokens to generate
        requests_interval (int): Interval between requests in seconds
        system_message (str): System message to be sent to the model
        num_responses (int): Number of responses to generate
        response_delimiter (str): Delimiter to join multiple responses
        include_content_filter_results (bool):
            If true, the model returns a dict, which contains "text", "prompt_filter_results", and "completion_filter_results" for each input.
            If false, the return value for each input is a str-typed text.
            Default is false.
        disable_auth (bool): Whether to disable authentication.
            If true, no api_key should be provided, and the endpoint will be called directly without attempting authentication.
            If false, either api_key will be used to authenticate if provided, or token bearer authentication will be used by default.
            Default is false.
        extra_headers (dict[str, str]): Additional headers to add to the REST API request.
    """
    VERSION = '0.2.8'

    @dataclasses.dataclass
    class Config:
        endpoint: str
        deployment_name: str
        api_version: str = '2023-03-15-preview'
        api_key: Optional[str] = None
        temperature: float = 0.0
        max_tokens: int = 100
        requests_interval: int = 0
        system_message: str = ''
        num_responses: int = 1
        response_delimiter: str = '<|delimiter|>'
        json_schema: Optional[dict] = None
        include_content_filter_results: bool = False
        disable_auth: bool = False
        extra_headers: Optional[dict] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        self._check_configs()
        model = OpenAITextChatModel(self.config.endpoint, self.config.deployment_name, self.config.api_version, self.config.api_key, self.config.temperature, self.config.max_tokens,
                                    self.config.requests_interval, self.config.num_responses, self.config.response_delimiter, self.config.system_message, self.config.json_schema,
                                    self.config.include_content_filter_results, self.config.disable_auth, self.config.extra_headers)

        return self.Outputs(model)

    def dry_run(self, inputs):
        self._check_configs()
        return self.Outputs(FakeModel())

    def _check_configs(self):
        if not self.config.endpoint:
            raise ValueError("Endpoint is not set")

        if not urlparse(self.config.endpoint).scheme in ('http', 'https'):
            raise ValueError("Endpoint must start with http:// or https://")

        if not self.config.deployment_name:
            raise ValueError("Deployment name is not set")


class OpenAIChatClient(OpenAIClientBase):
    def __init__(self, endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, system_message, json_schema=None, disable_auth=False, extra_headers=None):
        super().__init__(endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, json_schema, disable_auth=disable_auth, extra_headers=extra_headers)
        self._system_message = system_message

    def get_url(self):
        return '/chat/completions?' + urlencode({'api-version': self._api_version})

    def make_request_body(self, inputs):
        assert isinstance(inputs, str)
        messages = []
        if self._system_message:
            messages.append({'role': 'system', 'content': self._system_message})
        messages.append({'role': 'user', 'content': inputs})
        return {'messages': messages}

    def parse_response(self, response_json):
        texts = [r.get('message', {}).get('content', '').strip() for r in response_json['choices']]
        returned_text = self._delimiter.join(texts)
        prompt_tokens, completion_tokens = response_json['usage']['prompt_tokens'], response_json['usage']['completion_tokens']
        prompt_filter_results = response_json.get('prompt_filter_results', [])

        # This is to workaround an AOAI bug of incorrect promptFilterResults schema
        prompt_filter_results = [{f"{k}s" if k == 'content_filter_result' else k: v for k, v in result.items()} for result in prompt_filter_results]

        completion_filter_results = [{k: t[k] for k in t.keys() & {'index', 'content_filter_results'}} for t in response_json['choices']]
        return returned_text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results


class OpenAITextChatModel(torch.nn.Module):
    def __init__(
            self, endpoint, deployment_name, api_version, api_key, temperature, max_tokens,
            requests_interval, num_responses, delimiter, system_message, json_schema=None,
            include_content_filter_results=False, disable_auth=False, extra_headers=None):
        super().__init__()
        self._client = OpenAIChatClient(
            endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, system_message, json_schema,
            disable_auth=disable_auth, extra_headers=extra_headers)
        self._requests_interval = requests_interval
        self._last_request_timestamp = None
        self._include_content_filter_results = include_content_filter_results

    def forward(self, inputs: Tuple[List[str], List[List[torch.Tensor]]]) -> List[str]:
        results = []
        for prompt, prompt_images in zip(inputs[0], inputs[1]):
            if prompt_images:
                raise ValueError("This model does not support images")

            if self._last_request_timestamp:
                time.sleep(max(0, self._requests_interval - (time.time() - self._last_request_timestamp)))

            try:
                text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = self._client.post(prompt)
                self._last_request_timestamp = time.time()
            except Exception:
                logger.exception(f"Failed to generate text for prompt: {prompt}")
                text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = '', 0, 0, [], []
            if self._include_content_filter_results:
                results.append({
                    'text': text,
                    'prompt_filter_results': prompt_filter_results,
                    'completion_filter_results': completion_filter_results,
                })
            else:
                results.append(text)
            logger.info(f"Generated text: {repr(text)}, prompt tokens: {prompt_tokens}, completion_tokens: {completion_tokens}")
        return results

    def __getstate__(self):
        return {'client': self._client, 'requests_interval': self._requests_interval}

    def __setstate__(self, state):
        super().__init__()
        self._client = state['client']
        self._requests_interval = state['requests_interval']
        self._last_request_timestamp = None


class FakeModel(torch.nn.Module):
    def forward(self, inputs):
        return [''] * len(inputs)
