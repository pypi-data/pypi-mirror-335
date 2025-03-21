import dataclasses
import logging
from typing import List, Dict, Literal
import tiktoken
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Compute the number of tokens consumed by text messages ny tiktoken.

    Inputs:
        messages (List[Dict[str, str]]): List of messages
    Config:
        model_name (str): model_name, only supports gpt-4, gpt-4o and gpt-4o-mini
    Returns:
        List of int: number of tokens consumed per message.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        messages: List[Dict[str, str]]

    @dataclasses.dataclass
    class Config:
        model_name: Literal['gpt-4', 'gpt-4o', 'gpt-4o-mini']

    @dataclasses.dataclass
    class Outputs:
        num_tokens: List[int]

    def execute(self, inputs):
        if self.config.model_name not in {'gpt-4', 'gpt-4o', 'gpt-4o-mini'}:
            raise ValueError(f'Unsupported model_name: {self.config.model_name}')

        calculator = OpenAITextTokenCalculator(self.config.model_name)
        return self.Outputs(calculator.compute(inputs.messages))

    def dry_run(self, inputs):
        return self.execute(inputs)


class OpenAITextTokenCalculator:
    """Compute the number of tokens consumed given model name and image detail parameter. https://cookbook.openai.com/examples/how_to_format_inputs_to_chatgpt_models#4-counting-tokens.
    This may not be accurate as tokens_per_name and tokens_per_message may vary by models.
    """

    tokens_per_name = 1
    tokens_per_message = 3
    token_per_content_separator = 1

    def __init__(self, model_name):
        self.encoder = tiktoken.encoding_for_model(model_name)

    def compute(self, messages):
        num_tokens = []
        for message in messages:
            n = self.tokens_per_message
            for key, value in message.items():
                if key == "name":
                    n += self.tokens_per_name
                    n += len(self.encoder.encode(value))
                elif key == 'role':
                    n += len(self.encoder.encode(value))
                elif key == 'content':
                    n += self.get_content_num_text_tokens(value)
            num_tokens.append(n)
        return num_tokens

    def get_content_num_text_tokens(self, content):
        if isinstance(content, str):
            return len(self.encoder.encode(content))
        elif isinstance(content, dict):
            return self.get_content_num_text_tokens(content['text']) if 'text' in content else 0
        elif isinstance(content, list):
            return sum(self.get_content_num_text_tokens(item) for item in content) + (len(content) - 1) * self.token_per_content_separator
