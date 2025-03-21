import unittest
import unittest.mock
import torch
from irisml.tasks.compute_image_token_number import Task


class TestComputeImageTokenNumber(unittest.TestCase):
    def test_simple(self):
        images = [torch.zeros(3, 200, 200), torch.zeros(3, 512, 512), torch.zeros(3, 512, 513), torch.zeros(1, 1024, 1024), torch.zeros(3, 1024, 2048), torch.zeros(1, 2048, 4096)]
        name = 'gpt-4o'
        num_tokens = Task(Task.Config(model_name=name, image_detail='low')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [85] * len(images))

        num_tokens = Task(Task.Config(model_name=name, image_detail='high')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [255, 255, 425, 765, 1105, 1105])

        num_tokens = Task(Task.Config(model_name=name, image_detail='auto')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [85, 85, 425, 765, 1105, 1105])

        name = 'gpt-4o-mini'
        num_tokens = Task(Task.Config(model_name=name, image_detail='low')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [2833] * len(images))

        num_tokens = Task(Task.Config(model_name=name, image_detail='high')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [8500, 8500, 14167, 25501, 36835, 36835])

        num_tokens = Task(Task.Config(model_name=name, image_detail='auto')).execute(Task.Inputs(images)).num_tokens
        self.assertEqual(num_tokens, [2833, 2833, 14167, 25501, 36835, 36835])

    def test_invalid_names(self):
        with self.assertRaises(ValueError):
            Task(Task.Config(model_name='gpt-4o-001', image_detail='auto')).execute(Task.Inputs([torch.zeros(3, 200, 200)]))
        with self.assertRaises(ValueError):
            Task(Task.Config(model_name='gpt-4o', image_detail='medium')).execute(Task.Inputs([torch.zeros(3, 200, 200)]))
