import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    """Extract results from Azure OpenAI response.

    Inputs:
        predictions (list[Any]): The list of predictions from the AOAI model.
            Each prediction is either a string, or a dictionary with "text", "prompt_filter_results", "completion_filter_results" fields.

    Outputs:
        texts (list[str]): The list of texts extracted from the "text" field of the input.
            The text would be an empty string if the prediction is a dict and the "text" field is not found.
        input_filter_results (list[list[dict]]): The list of content filter results extracted from "prompt_filter_results" field of the input.
            The list elements would be an empty list if the prediction is a string or if the prediction is dict and the "prompt_filter_results" field is not found.
        output_filter_results (list[list[dict]]): The list of content filter results extracted from "completion_filter_results" field of the input.
            The list elements would be an empty list if the prediction is a string or if the prediction is dict and the "completion_filter_results" field is not found.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        predictions: typing.List[typing.Any]

    @dataclasses.dataclass
    class Outputs:
        texts: typing.List[str]
        input_filter_results: typing.List[typing.List[typing.Dict[str, typing.Any]]]
        output_filter_results: typing.List[typing.List[typing.Dict[str, typing.Any]]]

    def execute(self, inputs):
        return self.Outputs(
            texts=[self._extract_field(prediction, "text", "") for prediction in inputs.predictions],
            input_filter_results=[self._extract_field(prediction, "prompt_filter_results", []) for prediction in inputs.predictions],
            output_filter_results=[self._extract_field(prediction, "completion_filter_results", []) for prediction in inputs.predictions],
        )

    def dry_run(self, inputs):
        return self.execute(inputs)

    @staticmethod
    def _extract_field(prediction, field_name, default_value):
        if isinstance(prediction, dict):
            return prediction.get(field_name, default_value)
        elif isinstance(prediction, str):
            if field_name == "text":
                return prediction
            else:
                return default_value
        else:
            raise ValueError(f"Unknown prediction type: {type(prediction)}")
