import dataclasses
import logging
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse
from azure.identity import DefaultAzureCredential
import requests
import tenacity
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a model that generates text using Azure OpenAI completion API.

    This task calls Azure OpenAI completion API.
    https://docs.microsoft.com/en-us/azure/cognitive-services/openai-gpt/quickstart

    The model interface is:
    - Input: (str, [])
    - Output: str | dict, depending on the value of config include_content_filter_results

    Config:
        endpoint (str): Azure endpoint
        deployment_name (str): Azure deployment name
        api_version (str): OpenAI API version, default is 2023-03-15-preview
        api_key (str): Azure API key
        temperature (float): Temperature parameter for text generation
        top_p (float): Top p parameter for text generation
        max_tokens (int): Maximum number of tokens to generate
        requests_interval (int): Interval between requests in seconds
        num_responses (int): Number of responses to generate
        response_delimiter (str): Delimiter between responses. Used only if num_responses > 1
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
    VERSION = '0.2.7'

    @dataclasses.dataclass
    class Config:
        endpoint: str
        deployment_name: str
        api_version: str = '2023-03-15-preview'
        api_key: Optional[str] = None
        temperature: float = 0.0
        top_p: float = 1.0
        max_tokens: int = 100
        requests_interval: int = 0
        num_responses: int = 1
        response_delimiter: str = '<|delimiter|>'
        include_content_filter_results: bool = False
        disable_auth: bool = False
        extra_headers: Optional[dict] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        self._check_configs()
        model = OpenAITextCompletionModel(self.config.endpoint, self.config.deployment_name, self.config.api_version, self.config.api_key, self.config.temperature, self.config.top_p,
                                          self.config.max_tokens, self.config.requests_interval, self.config.num_responses, self.config.response_delimiter,
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


def _should_retry(exception):
    if isinstance(exception, requests.exceptions.RequestException):
        response = getattr(exception, 'response', None)
        if response is not None and (response.status_code == 429 or response.status_code >= 500):
            return True
        if isinstance(exception, requests.exceptions.ConnectionError):
            return True
    return False


class SerializableCredential:
    def __init__(self):
        self._credential = DefaultAzureCredential()

    def get_token(self, *args, **kwargs):
        return self._credential.get_token(*args, **kwargs)

    def __getstate__(self):
        return {}

    def __setstate__(self, _):
        self.__init__()


class OpenAIClientBase:
    def __init__(self, endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, json_schema=None, disable_auth=False, extra_headers=None):
        self._api_version = api_version
        self._url = f'{endpoint}/openai/deployments/{deployment_name}' + self.get_url()
        self._api_key = api_key
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._num_responses = num_responses
        self._delimiter = delimiter
        self._credential = None if self._api_key else SerializableCredential()
        self._auth_token_cache = None
        self._json_schema = json_schema
        if disable_auth and api_key:
            raise ValueError("When disable_auth is True, no api_key should be provided.")
        self._disable_auth = disable_auth
        self._extra_headers = extra_headers

    def get_url(self) -> str:
        raise NotImplementedError

    def make_request_body(self, inputs) -> Dict:
        raise NotImplementedError

    def parse_response(self, response_json) -> Tuple[str, int, List[object], List[object]]:
        raise NotImplementedError

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=2, min=30, max=128), stop=tenacity.stop_after_attempt(20), retry=tenacity.retry_if_exception(_should_retry))
    def post(self, inputs):
        response = None
        response_json = None
        request_body = self.make_request_body(inputs)
        request_body['temperature'] = self._temperature
        request_body['max_tokens'] = self._max_tokens
        request_body['n'] = self._num_responses
        if self._json_schema:
            request_body['response_format'] = {'type': 'json_schema', 'json_schema': self._json_schema}
        try:
            # Use a long timeout because the API can take a long time to respond
            headers = {}
            if self._api_key:
                headers = {'api-key': self._api_key}
            elif not self._disable_auth:
                headers = {'Authorization': f'Bearer {self._get_auth_token()}'}
            if self._extra_headers:
                headers = {**headers, **self._extra_headers}
            response = requests.post(self._url, headers=headers, json=request_body, timeout=120)
            response.raise_for_status()
            response_json = response.json()
            returned_text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = self.parse_response(response_json)
            return returned_text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results
        except Exception as e:
            if response is not None:
                logger.error(f"Failed to POST to {self._url}: {response.status_code} {response.content} {repr(e)}")
            else:
                logger.exception(f"Failed to POST to {self._url}")

            if response_json:
                logger.error(f"Response JSON: {response_json}")
                try:
                    prompt_tokens, completion_tokens = response_json['usage']['prompt_tokens'], response_json['usage']['completion_tokens']
                    prompt_filter_results = response_json.get('prompt_filter_results', [])
                    completion_filter_results = [{k: t[k] for k in t.keys() & {'index', 'content_filter_results'}} for t in response_json.get('choices', [])]
                    return '', prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results
                except Exception as e:
                    logger.error(f"Failed to parse total tokens: {repr(e)}")
            raise

    def _get_auth_token(self):
        if not self._auth_token_cache or time.time() > self._auth_token_cache.expires_on:
            self._auth_token_cache = self._credential.get_token('https://cognitiveservices.azure.com/.default')
        return self._auth_token_cache.token


class OpenAICompletionClient(OpenAIClientBase):
    def __init__(self, endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, top_p, disable_auth=False, extra_headers=None):
        super().__init__(endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, disable_auth=disable_auth, extra_headers=extra_headers)
        self._top_p = top_p

    def get_url(self):
        return '/completions?' + urlencode({'api-version': self._api_version})

    def make_request_body(self, inputs):
        assert isinstance(inputs, str)
        return {'prompt': inputs, 'top_p': self._top_p}

    def parse_response(self, response_body):
        texts = [t['text'].strip() for t in response_body['choices']]
        text = self._delimiter.join(texts)
        prompt_tokens, completion_tokens = response_body['usage']['prompt_tokens'], response_body['usage']['completion_tokens']
        prompt_filter_results = response_body.get('prompt_filter_results', [])
        completion_filter_results = [{k: t[k] for k in t.keys() & {'index', 'content_filter_results'}} for t in response_body['choices']]
        return text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results


class OpenAITextCompletionModel(torch.nn.Module):
    def __init__(self, endpoint, deployment_name, api_version, api_key, temperature, top_p, max_tokens, requests_interval, num_responses, delimiter,
                 include_content_filter_results=False, disable_auth=False, extra_headers=None):
        super().__init__()
        self._client = OpenAICompletionClient(
            endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter,
            top_p=top_p, disable_auth=disable_auth, extra_headers=extra_headers)
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
                logger.exception(f"Failed to generate text for prompt: {repr(prompt)}")
                text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = '', 0, [], []
            if self._include_content_filter_results:
                results.append({
                    'text': text,
                    'prompt_filter_results': prompt_filter_results,
                    'completion_filter_results': completion_filter_results,
                })
            else:
                results.append(text)
            logger.info(f"Generated text: {repr(text)}, completion tokens: {completion_tokens}, total prompt tokens: {prompt_tokens}")
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
