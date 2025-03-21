import unittest
from irisml.tasks.extract_azure_openai_predictions import Task


class TestGetItem(unittest.TestCase):
    def test_simple(self):
        prompt_filter_results = [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}]
        completion_filter_results = [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]

        inputs = Task.Inputs([{
            "text": "dummy",
            "prompt_filter_results": prompt_filter_results,
            "completion_filter_results": completion_filter_results,
        }])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual(["dummy"], outputs.texts)
        self.assertEqual([prompt_filter_results], outputs.input_filter_results)
        self.assertEqual([completion_filter_results], outputs.output_filter_results)

    def test_empty_result(self):
        inputs = Task.Inputs([])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual([], outputs.texts)
        self.assertEqual([], outputs.input_filter_results)
        self.assertEqual([], outputs.output_filter_results)

    def test_multiple_results(self):
        prompt_filter_results_1 = [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}]
        prompt_filter_results_2 = [{'prompt_index': 1, 'content_filter_results': {'indirect_attack': {'filtered': False, 'detected': False}}}]
        completion_filter_results_1 = [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]
        completion_filter_results_2 = [{'index': 1, 'content_filter_results': {'violence': {'filtered': False, 'severity': 'medium'}}}]

        inputs = Task.Inputs([
            {
                "text": "dummy",
                "prompt_filter_results": prompt_filter_results_1,
                "completion_filter_results": completion_filter_results_1,
            },
            {
                "text": "yet another dummy",
                "prompt_filter_results": prompt_filter_results_2,
                "completion_filter_results": completion_filter_results_2,
            },
        ])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual(["dummy", "yet another dummy"], outputs.texts)
        self.assertEqual([prompt_filter_results_1, prompt_filter_results_2], outputs.input_filter_results)
        self.assertEqual([completion_filter_results_1, completion_filter_results_2], outputs.output_filter_results)

    def test_no_text(self):
        prompt_filter_results = [{'prompt_index': 0, 'content_filter_results': {'jailbreak': {'filtered': False, 'detected': True}}}]
        completion_filter_results = [{'index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}}}]

        inputs = Task.Inputs([{
            "prompt_filter_results": prompt_filter_results,
            "completion_filter_results": completion_filter_results,
        }])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual([""], outputs.texts)
        self.assertEqual([prompt_filter_results], outputs.input_filter_results)
        self.assertEqual([completion_filter_results], outputs.output_filter_results)

    def test_no_content_filter_results(self):
        inputs = Task.Inputs([{
            "text": "dummy",
        }])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual(["dummy"], outputs.texts)
        self.assertEqual([[]], outputs.input_filter_results)
        self.assertEqual([[]], outputs.output_filter_results)

    def test_string_predictions(self):
        inputs = Task.Inputs(["dummy"])
        config = Task.Config()
        outputs = Task(config).execute(inputs)
        self.assertEqual(["dummy"], outputs.texts)
        self.assertEqual([[]], outputs.input_filter_results)
        self.assertEqual([[]], outputs.output_filter_results)

    def test_invalid_predictions(self):
        inputs = Task.Inputs([123])
        config = Task.Config()
        with self.assertRaises(ValueError):
            Task(config).execute(inputs)
