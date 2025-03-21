import base64
import dataclasses
import io
import json
import logging
import random
import time
from typing import List, Optional, Tuple, Literal
from urllib.parse import urlencode, urlparse
import torch.utils.data
import torchvision.transforms
import irisml.core
from irisml.tasks.create_azure_openai_chat_model import OpenAIChatClient
from irisml.tasks.compute_image_token_number import OpenAIImageTokenCalculator
from irisml.tasks.compute_text_token_number import OpenAITextTokenCalculator

IMAGE_PLACEHOLDER = '<|image|>'
logger = logging.getLogger(__name__)


class ModelCollection(torch.nn.Module):
    def __init__(self, models: List[torch.nn.Module], rnd_seed: Optional[int] = None):
        super(ModelCollection, self).__init__()
        self.models = torch.nn.ModuleList(models)
        self.rng = random.Random(rnd_seed)

    def forward(self, input):
        """Randomly pick a model and run the forward pass."""
        model = self.rng.choice(self.models)
        return model(input)


class Task(irisml.core.TaskBase):
    """Create a model that generates text using Azure OpenAI chat API with images.

    This task calls the Azure OpenAI GPT-V chat API. Multiple endpoint and deployment pairs can be provided, and traffic will be distributed among them.

    Currently this implementation supports a single system message and a single user message.

    The model input is (prompts_batch, images_batch) where:
    - prompts_batch is a list of prompts, each prompt is a string with one or more IMAGE_PLACEHOLDER
    - images_batch is one of the following:
        - A list of lists of images, where each image is a tensor of shape (3, H, W).
        - A list of images, where each image is a tensor of shape (3, H, W).
        - A tensor of shape (N, 3, H, W) where N is the number of prompts and H, W are the image dimensions.

    The model output is a list of generated texts or dicts (depending on include_content_filter_results), one for each prompt.

    Config:
        endpoint (str): Azure endpoint. Multiple endpoints could be provided together with deployment_name and api_key, separated by semicolons
        deployment_name (str): Azure deployment name. Multiple deployment names could be provided together with endpoint and api_key, separated by semicolons
        api_version (str): OpenAI API version, default is 2024-08-01-preview
        api_key (str): Azure API key. Multiple API keys could be provided together with endpoint and deployment_name, separated by semicolons
        temperature (float): Temperature parameter for text generation
        max_tokens (int): Maximum number of tokens to generate, default is None (no limit)
        requests_interval (int): Interval between requests in seconds
        system_message (str): System message to be sent to the model
        num_responses (int): Number of responses to generate
        response_delimiter (str): Delimiter to join multiple responses
        json_schema: Optional JSON schema for the model output, format: https://platform.openai.com/docs/guides/structured-outputs/introduction
        image_detail (str): Image detail level. One of 'auto', 'low', 'high'
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
    VERSION = '0.2.0'
    _SEP = ";"

    @dataclasses.dataclass
    class Config:
        endpoint: str
        deployment_name: str
        api_version: str = '2024-08-01-preview'
        api_key: Optional[str] = None
        temperature: float = 0.0
        max_tokens: Optional[int] = None
        requests_interval: int = 0
        system_message: str = ''
        num_responses: int = 1
        response_delimiter: str = '<|delimiter|>'
        json_schema: Optional[dict] = None
        include_content_filter_results: bool = False
        image_detail: Literal['auto', 'low', 'high'] = 'auto'
        disable_auth: bool = False
        extra_headers: Optional[dict] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        self._check_configs()

        if self._SEP in self.config.endpoint and self._SEP in self.config.deployment_name:
            endpoints = self.config.endpoint.split(self._SEP)
            deployment_names = self.config.deployment_name.split(self._SEP)
            api_keys = self.config.api_key.split(self._SEP) if self.config.api_key else None

            logger.info(f"Using multiple endpoints: {endpoints} and deployment names: {deployment_names}")

            if len(endpoints) != len(deployment_names) or (api_keys and len(api_keys) != len(deployment_names)):
                raise ValueError("Number of endpoints, deployment names, and api keys (if provided) must be equal,"
                                 f" but got {len(endpoints)}, {len(deployment_names)}, {len(api_keys) if api_keys else 'None'}")

            clients = [self._create_client(endpoints[i], deployment_names[i], api_keys[i] if api_keys else None) for i in range(len(endpoints))]
            models = [OpenAITextGenerationWithImagesModel(client, self.config.requests_interval, self.config.include_content_filter_results) for client in clients]
            model = ModelCollection(models)
        else:
            client = self._create_client(self.config.endpoint, self.config.deployment_name, self.config.api_key)
            model = OpenAITextGenerationWithImagesModel(client, self.config.requests_interval, self.config.include_content_filter_results)
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

    def _create_client(self, endpoint, deployment_name, api_key):
        return OpenAIChatWithImagesClient(endpoint, deployment_name, self.config.api_version, api_key, self.config.temperature,
                                          self.config.max_tokens, self.config.num_responses, self.config.response_delimiter,
                                          self.config.system_message, self.config.json_schema,
                                          self.config.image_detail, self.config.disable_auth, self.config.extra_headers)


class OpenAIChatWithImagesClient(OpenAIChatClient):
    def __init__(self, endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, system_message, json_schema=None,
                 image_detail='auto', disable_auth=False, extra_headers=None):
        self.image_detail = image_detail
        model_name = 'gpt-4o-mini' if 'mini' in deployment_name else 'gpt-4o'  # TODO: a better way to get model_name without calling the API
        self.image_token_calculator = OpenAIImageTokenCalculator(model_name=model_name, image_detail=image_detail)
        self.text_token_calculator = OpenAITextTokenCalculator(model_name)
        # Estimate consumed tokens for JSON schema, this will not be needed when the token calculation is fixed from the API side.
        self.num_tokens_schema = self.text_token_calculator.compute([{'content': json.dumps(json_schema, indent=2)}]) if json_schema is not None else [0]
        super().__init__(
            endpoint, deployment_name, api_version, api_key, temperature, max_tokens, num_responses, delimiter, system_message, json_schema,
            disable_auth=disable_auth, extra_headers=extra_headers)

    def get_url(self):
        return '/chat/completions?' + urlencode({'api-version': self._api_version})

    def make_request_body(self, inputs: Tuple[str, List[bytes]]):
        assert isinstance(inputs, tuple) and len(inputs) == 2 and isinstance(inputs[0], str) and isinstance(inputs[1], list)
        prompt, prompt_images = inputs
        prompt_parts = prompt.split(IMAGE_PLACEHOLDER)
        assert len(prompt_parts) == len(prompt_images) + 1

        content = []
        for text, image_bytes in zip(prompt_parts, prompt_images):
            for t in text.splitlines():
                content.append({'type': 'text', 'text': t.strip()})
            content.append({'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + base64.b64encode(image_bytes).decode('ascii'),
                                                               'detail': self.image_detail}})

        if prompt_after_last_image := prompt_parts[-1].strip():
            content.append({'type': 'text', 'text': prompt_after_last_image})

        messages = []
        if self._system_message:
            messages.append({'role': 'system', 'content': self._system_message})
        messages.append({'role': 'user', 'content': content})

        # Estimate consumed tokens for input messages, this will not be needed when the token calculation is fixed from the API side.
        num_tokens_input_text = self.text_token_calculator.compute(messages) + self.num_tokens_schema
        logger.info(f"Number of estimated input text tokens: {sum(num_tokens_input_text)}")

        return {'messages': messages}

    def compute_image_tokens(self, images: List[torch.Tensor]):
        return self.image_token_calculator.compute(images)


class OpenAITextGenerationWithImagesModel(torch.nn.Module):
    def __init__(self, client, requests_interval, include_content_filter_results=False):
        super().__init__()
        self._client = client
        self._requests_interval = requests_interval
        self._last_request_timestamp = None
        self._include_content_filter_results = include_content_filter_results

    def forward(self, inputs):
        if isinstance(inputs[1], torch.Tensor):
            assert len(inputs[1].shape) == 4
            images_batch = [[image] for image in inputs[1]]
        else:
            assert isinstance(inputs[1], list)
            if isinstance(inputs[1][0], torch.Tensor) and len(inputs[1][0].shape) == 3:
                images_batch = [[image] for image in inputs[1]]
            else:
                images_batch = inputs[1]

        results = []
        for prompt, prompt_images in zip(inputs[0], images_batch):
            if prompt.count(IMAGE_PLACEHOLDER) != len(prompt_images):
                raise ValueError(f"Number of images ({len(prompt_images)}) does not match the number of placeholders ({prompt.count(IMAGE_PLACEHOLDER)})")

            image_bytes = [self._tensor_to_image_bytes(image) for image in prompt_images]
            if self._last_request_timestamp:
                time.sleep(max(0, self._requests_interval - (time.time() - self._last_request_timestamp)))

            try:
                text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = self._client.post((prompt, image_bytes))
                image_tokens = sum(self._client.compute_image_tokens(prompt_images))
                self._last_request_timestamp = time.time()
            except Exception:
                logger.exception(f"Failed to generate text for prompt: {prompt}")
                text, prompt_tokens, completion_tokens, image_tokens, prompt_filter_results, completion_filter_results = '', 0, 0, 0, [], []
            if self._include_content_filter_results:
                results.append({
                    'text': text,
                    'prompt_filter_results': prompt_filter_results,
                    'completion_filter_results': completion_filter_results,
                })
            else:
                results.append(text)
            logger.info(f"Generated text: {repr(text)}, completion tokens: {completion_tokens}, total prompt tokens: {prompt_tokens}, image tokens: {image_tokens}")
        return results

    @staticmethod
    def _tensor_to_image_bytes(image: torch.Tensor) -> bytes:
        pil_image = torchvision.transforms.ToPILImage()(image)
        bytes_io = io.BytesIO()
        pil_image.save(bytes_io, format='PNG')
        return bytes_io.getvalue()

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
