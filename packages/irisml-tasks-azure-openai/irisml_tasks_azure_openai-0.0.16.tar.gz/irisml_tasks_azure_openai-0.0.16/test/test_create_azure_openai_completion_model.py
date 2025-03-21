import time
import unittest
import unittest.mock
import torch
from irisml.tasks.create_azure_openai_completion_model import Task, OpenAICompletionClient


class TestCreateAzureOpenaiCompletionModel(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config(endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key')).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            model_outputs = outputs.model((['test'], [[]]))
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/completions?api-version=example_version')
            self.assertEqual(model_outputs, ['test'])

    def test_multiple_responses(self):
        outputs = Task(Task.Config(endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key', num_responses=3)).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}, {'text': 'test2'}, {'text': 'test3'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            model_outputs = outputs.model((['test'], [[]]))
            mock_post.assert_called_once()
            self.assertEqual(model_outputs, ['test<|delimiter|>test2<|delimiter|>test3'])

    def test_no_wait_at_first_request(self):
        outputs = Task(Task.Config(
            endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key', requests_interval=60
        )).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            start_time = time.time()
            outputs.model((['test <|image|>'], [[]]))
            self.assertLess(time.time() - start_time, 1)

    def test_requests_interval(self):
        outputs = Task(Task.Config(
            endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key', requests_interval=1
        )).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            start_time = time.time()
            outputs.model((['test <|image|>'], [[]]))
            self.assertLess(time.time() - start_time, 1)

            # The second request has to wait for 1 second
            start_time = time.time()
            outputs.model((['test <|image|>'], [[]]))
            self.assertGreater(time.time() - start_time, 1)

    def test_content_filter_results(self):
        outputs = Task(Task.Config(
            endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key', include_content_filter_results=True
        )).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'choices': [{'text': 'test', 'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}],
                'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6},
                'prompt_filter_results': [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}]
            }
            model_outputs = outputs.model((['test'], [[]]))
            mock_post.assert_called_once()
            self.assertEqual(model_outputs, [{
                'text': 'test',
                'prompt_filter_results': [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}],
                'completion_filter_results': [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]
            }])

    def test_disable_auth(self):
        outputs = Task(Task.Config(endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key=None, disable_auth=True)).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            model_outputs = outputs.model((['test'], [[]]))
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/completions?api-version=example_version')
            self.assertEqual(mock_post.call_args.kwargs['headers'], {})
            self.assertEqual(model_outputs, ['test'])

    def test_disable_auth_with_api_key(self):
        with unittest.mock.patch('requests.post') as mock_post:
            with self.assertRaises(ValueError):
                outputs = Task(Task.Config(endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version', api_key='example_key',
                                           disable_auth=True)).execute(Task.Inputs())
                outputs.model((['test'], [[]]))
            mock_post.assert_not_called()
            mock_post.reset_mock()

    def test_extra_headers(self):
        outputs = Task(Task.Config(
            endpoint='https://example.com', deployment_name='example_deployment', api_version='example_version',
            disable_auth=True, extra_headers={'k1': 'v1', 'k2': 'v2'})).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            model_outputs = outputs.model((['test'], [[]]))
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.args[0], 'https://example.com/openai/deployments/example_deployment/completions?api-version=example_version')
            self.assertEqual(mock_post.call_args.kwargs['headers'], {'k1': 'v1', 'k2': 'v2'})
            self.assertEqual(model_outputs, ['test'])


class TestOpenAICompletionClient(unittest.TestCase):
    def test_simple(self):
        client = OpenAICompletionClient('https://example.com', 'example_deployment', 'example_version', 'example_key', 0., 100, 1, ',', 0.1)
        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'choices': [{'text': 'test'}], 'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = client.post('Hello world')
            mock_post.assert_called_once()
            self.assertEqual(text, 'test')
            self.assertEqual(prompt_tokens, 4)
            self.assertEqual(completion_tokens, 6)
            self.assertEqual(prompt_filter_results, [])
            self.assertEqual(completion_filter_results, [{}])

    def test_only_token_is_available(self):
        client = OpenAICompletionClient('https://example.com', 'example_deployment', 'example_version', 'example_key', 0., 100, 1, ',', 0.1)
        with unittest.mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'usage': {'total_tokens': 10, 'prompt_tokens': 4, 'completion_tokens': 6}}
            text, prompt_tokens, completion_tokens, prompt_filter_results, completion_filter_results = client.post('Hello world')
            mock_post.assert_called_once()
            self.assertEqual(text, '')
            self.assertEqual(prompt_tokens, 4)
            self.assertEqual(completion_tokens, 6)
            self.assertEqual(prompt_filter_results, [])
            self.assertEqual(completion_filter_results, [])
