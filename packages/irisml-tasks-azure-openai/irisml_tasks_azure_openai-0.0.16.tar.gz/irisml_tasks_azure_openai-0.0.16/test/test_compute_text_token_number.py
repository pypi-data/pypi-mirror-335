import unittest
import unittest.mock
from irisml.tasks.compute_text_token_number import Task


class TestComputeTextTokenNumber(unittest.TestCase):
    def test_simple(self):
        messages = [
            {
                "role": "system",
                "content": "You are a helpful, pattern-following assistant that translates corporate jargon into plain English.",
            },
            {
                "role": "system",
                "name": "example_user",
                "content": "New synergies will help drive top-line growth.",
            },
            {
                "role": "system",
                "name": "example_user",
                "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage.",
            },
            {
                "role": "user",
                "content": "This late pivot means we don't have time to boil the ocean for the client deliverable.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "This late pivot means we don't have time to boil the ocean for the client deliverable."},
                    {"type": "image", "image_url": ""},
                    {"type": "text", "text": "New synergies will help drive top-line growth."}
                ]
            }
        ]

        num_tokens = Task(Task.Config(model_name='gpt-4')).execute(Task.Inputs(messages)).num_tokens
        self.assertEqual(num_tokens, [22, 17, 25, 23, 35])

        num_tokens = Task(Task.Config(model_name='gpt-4o')).execute(Task.Inputs(messages)).num_tokens
        self.assertEqual(num_tokens, [21, 17, 24, 22, 34])

        num_tokens = Task(Task.Config(model_name='gpt-4o-mini')).execute(Task.Inputs(messages)).num_tokens
        self.assertEqual(num_tokens, [21, 17, 24, 22, 34])

    def test_invalid_model(self):
        with self.assertRaises(ValueError):
            Task(Task.Config(model_name='gpt-4-001')).execute(Task.Inputs([{"role": "user", "content": "This late pivot means we don't have time to boil the ocean for the client deliverable."}]))
