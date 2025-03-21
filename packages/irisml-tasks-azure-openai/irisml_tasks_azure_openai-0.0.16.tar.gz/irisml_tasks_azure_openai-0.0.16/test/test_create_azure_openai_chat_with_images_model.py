import contextlib
import time
import unittest
import unittest.mock
import torch
from irisml.tasks.create_azure_openai_chat_with_images_model import Task


class TestCreateAzureOpenaiCompletionWithImagesModel(unittest.TestCase):
    def test_simple(self):
        with self._model_with_mock_post(api_key='example_key') as (model, mock_post):
            model_outputs = model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/chat/completions?api-version=example_version')
            self.assertEqual(model_outputs, ['test'])
            mock_post.reset_mock()

            # Without image
            model_outputs = model([['test'], [[]]])
            mock_post.assert_called_once()
            self.assertEqual(model_outputs, ['test'])

    def test_simple_mutliple_endpoints(self):
        with self._model_with_mock_post(endpoint="https://example1.com;https://example2.com",
                                        deployment_name="example_deployment1;example_deployment2",
                                        api_key="example_key1;example_key2") as (model, mock_post):
            model_outputs = model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            mock_post.assert_called_once()
            self.assertTrue(mock_post.call_args.args[0] in [
                'https://example1.com/openai/deployments/example_deployment1/chat/completions?api-version=example_version',
                'https://example2.com/openai/deployments/example_deployment2/chat/completions?api-version=example_version'])
            self.assertEqual(model_outputs, ['test'])
            mock_post.reset_mock()

            # Without image
            model_outputs = model([['test'], [[]]])
            mock_post.assert_called_once()
            self.assertEqual(model_outputs, ['test'])

    def test_prompt_new_lines(self):
        with self._model_with_mock_post(api_key='example_key') as (model, mock_post):
            model([['line1\nline2\nline3 <|image|> line4'], torch.zeros(1, 3, 32, 32)])
            json_request_body = mock_post.call_args.kwargs['json']
            content = json_request_body['messages'][0]['content']
            self.assertEqual(len(content), 5)
            self.assertEqual(content[0], {'type': 'text', 'text': 'line1'})
            self.assertEqual(content[1], {'type': 'text', 'text': 'line2'})
            self.assertEqual(content[2], {'type': 'text', 'text': 'line3'})
            self.assertIn('image_url', content[3])
            self.assertEqual(content[4], {'type': 'text', 'text': 'line4'})
            mock_post.assert_called_once()

    def test_fail_if_mismatched_image(self):
        with self._model_with_mock_post(api_key='example_key') as (model, mock_post):
            with self.assertRaises(ValueError):
                model([['test <|image|>'], [[]]])  # 1 image placeholder, no image.
            mock_post.assert_not_called()

            with self.assertRaises(ValueError):
                model([['test'], [torch.zeros(3, 16, 16)]])  # no image placeholder, 1 image.
            mock_post.assert_not_called()

            with self.assertRaises(ValueError):
                model([['test <|image|> <|image|>'], [torch.zeros(3, 16, 16)]])  # 2 image placeholders, 1 image.
            mock_post.assert_not_called()

    def test_no_wait_at_first_request(self):
        with self._model_with_mock_post(api_key='example_key', requests_interval=60) as (model, mock_post):
            start_time = time.time()
            model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            self.assertLess(time.time() - start_time, 1)
            mock_post.assert_called_once()

    def test_requests_interval(self):
        with self._model_with_mock_post(api_key='example_key', requests_interval=1) as (model, _):
            start_time = time.time()
            model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            self.assertLess(time.time() - start_time, 1)

            # The second request has to wait for 1 second
            start_time = time.time()
            model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            self.assertGreater(time.time() - start_time, 1)

    def test_json_schema(self):
        schema = {
            "name": "example_schema",
            "description": "Example schema.",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "example": {
                        "type": "string",
                        "description": "Example value."
                    }
                },
                "additionalProperties": False,
                "required": [
                    "example"
                ]
            }
        }
        outputs = Task(Task.Config(endpoint='https://example.com/', deployment_name='example_deployment', api_key='example_key', json_schema=schema)).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)
        self.assertEqual(outputs.model._client._json_schema, schema)

    def test_content_filter_results(self):
        with self._model_with_mock_post(api_key='example_key', include_content_filter_results=True) as (model, mock_post):
            model_outputs = model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            mock_post.assert_called_once()
            mock_post.reset_mock()
            self.assertEqual(model_outputs, [{
                'text': 'test',
                'prompt_filter_results': [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}],
                'completion_filter_results': [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]
            }])

            # Without image
            model_outputs = model([['test'], [[]]])
            mock_post.assert_called_once()
            self.assertEqual(model_outputs, [{
                'text': 'test',
                'prompt_filter_results': [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}],
                'completion_filter_results': [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]
            }])

    def test_disable_auth(self):
        with self._model_with_mock_post(api_key=None, disable_auth=True) as (model, mock_post):
            model_outputs = model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/chat/completions?api-version=example_version')
            self.assertEqual(mock_post.call_args.kwargs['headers'], {})
            self.assertEqual(model_outputs, ['test'])
            mock_post.reset_mock()

    def test_disable_auth_with_api_key(self):
        with self.assertRaises(ValueError):
            with self._model_with_mock_post(api_key='example_key', disable_auth=True) as (model, mock_post):
                model([['test <|image|>'], [torch.zeros(1, 3, 32, 32)]])
                mock_post.assert_not_called()
                mock_post.reset_mock()

    def test_extra_headers(self):
        with self._model_with_mock_post(api_key=None, disable_auth=True, extra_headers={'k': 'v'}) as (model, mock_post):
            model_outputs = model([['test <|image|>'], torch.zeros(1, 3, 32, 32)])
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/chat/completions?api-version=example_version')
            self.assertEqual(mock_post.call_args.kwargs['headers'], {'k': 'v'})
            self.assertEqual(model_outputs, ['test'])

    @contextlib.contextmanager
    def _model_with_mock_post(self, endpoint='https://example.com', deployment_name='example_deployment', api_key=None, **kwargs):
        outputs = Task(Task.Config(endpoint=endpoint, deployment_name=deployment_name, api_key=api_key, api_version='example_version', **kwargs)).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'choices': [{'message': {'role': 'assistant', 'content': 'test'}, 'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}],
                'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6},
                'prompt_filter_results': [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}]
            }
            yield outputs.model, mock_post
