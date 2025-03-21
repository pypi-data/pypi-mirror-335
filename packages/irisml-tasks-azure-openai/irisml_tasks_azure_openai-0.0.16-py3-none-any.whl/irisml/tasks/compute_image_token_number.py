import dataclasses
import logging
import math
from typing import List, Literal
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Compute the number of tokens consumed by an image for Azure OpenAI APIs according to https://platform.openai.com/docs/guides/vision.

    Config:
        model_name (str): model_name, only supports gpt-4o or gpt-4o-mini
        image_detail (str): image detail, auto/high/low
    Inputs:
        images (List[torch.Tensor]): List of torch.Tensor with shape (..., H, W)
    Returns:
        List of int: number of tokens consumed per image
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Inputs:
        images: List[torch.Tensor]

    @dataclasses.dataclass
    class Config:
        model_name: Literal['gpt-4o', 'gpt-4o-mini']
        image_detail: Literal['auto', 'high', 'low']

    @dataclasses.dataclass
    class Outputs:
        num_tokens: List[int]

    def execute(self, inputs):
        if self.config.model_name not in {'gpt-4o', 'gpt-4o-mini'}:
            raise ValueError(f'Unsupported model_name: {self.config.model_name}')
        if self.config.image_detail not in {'auto', 'high', 'low'}:
            raise ValueError(f'Unsupported image_detail: {self.config.image_detail}')

        calculator = OpenAIImageTokenCalculator(self.config.model_name, self.config.image_detail)
        return self.Outputs(calculator.compute(inputs.images))

    def dry_run(self, inputs):
        return self.execute(inputs)


class OpenAIImageTokenCalculator:
    # Compute the number of tokens consumed given model name and image detail parameter.

    MODEL_TO_BASE_TOKENS = {'gpt-4o-mini': 2833, 'gpt-4o': 85}
    MODEL_TO_TILE_TOKENS = {'gpt-4o-mini': 5667, 'gpt-4o': 170}
    MAX_LENGTH = 2048
    SHORT_LENGTH = 768
    PATCH_LENGTH = 512

    def __init__(self, model_name, image_detail):
        self.model = model_name
        self.image_detail = image_detail

    def compute_tiles(self, w: int, h: int):
        # Resize to fit MAX_LENGTH x MAX_LENGTH while keeping aspect ratio.
        if w > self.MAX_LENGTH or h > self.MAX_LENGTH:
            w, h = (self.MAX_LENGTH, round(h * self.MAX_LENGTH // w)) if w > h else (round(w * self.MAX_LENGTH // h), self.MAX_LENGTH)
        # Resize so that the shorter side is SHORT_LENGTH while keeping aspect ratio.
        if min(w, h) > self.SHORT_LENGTH:
            w, h = (self.SHORT_LENGTH, round(h * self.SHORT_LENGTH // w)) if w < h else (round(w * self.SHORT_LENGTH // h), self.SHORT_LENGTH)
        n_tiles = math.ceil(w / self.PATCH_LENGTH) * math.ceil(h / self.PATCH_LENGTH)
        return n_tiles

    def decide_image_detail(self, w: int, h: int):
        if self.image_detail == 'auto':
            if max(w, h) > self.PATCH_LENGTH:
                image_detail = 'high'
            else:
                image_detail = 'low'
        else:
            image_detail = self.image_detail
        return image_detail

    def compute(self, images: List[torch.Tensor]):
        '''Count consumed tokens per image according to https://platform.openai.com/docs/guides/vision. The result should align with https://openai.com/api/pricing/.
        Input:
            images: List of torch.Tensor with shape (C, H, W)
        Output:
            List of int, number of tokens consumed per image
        '''
        n_tokens = []
        for image in images:
            n_token = self.MODEL_TO_BASE_TOKENS[self.model]
            h, w = image.shape[-2:]
            image_detail = self.decide_image_detail(w, h)
            if image_detail == 'high':
                n_tiles = self.compute_tiles(w, h)
                n_token += n_tiles * self.MODEL_TO_TILE_TOKENS[self.model]

            n_tokens.append(n_token)
        return n_tokens
