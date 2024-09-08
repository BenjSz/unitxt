from typing import Any, Dict, List, Optional

from .api import infer
from .artifact import fetch_artifact
from .dataclass import Field
from .formats import Format, SystemFormat
from .inference import InferenceEngine, OpenAiInferenceEngine
from .metrics import BulkInstanceMetric
from .operator import SequentialOperator
from .settings_utils import get_settings
from .system_prompts import EmptySystemPrompt, SystemPrompt
from .templates import Template

settings = get_settings()


class LLMAsJudgeTaskFormatter:
    task: str
    reduction_map_str: str
    infer_log_probs: bool = False

    def get_single_instance_for_judge_model(
        self, input_instance: str, prediction: str, reference: List
    ):
        pass

    def prediction_output_to_main_score(self, instance):
        pass

    def get_input_instances_by_prompt_source(
        self,
        task_data: List[Dict],
        strip_system_prompt_and_format_from_inputs: bool = False,
    ) -> List:
        if strip_system_prompt_and_format_from_inputs:
            instances = []
            for task_data_instance in task_data:
                template = task_data_instance["metadata"]["template"]
                template, _ = fetch_artifact(template)
                instance = SequentialOperator(
                    steps=[template, "formats.empty"]
                ).process_instance(
                    {
                        "input_fields": task_data_instance,
                        "reference_fields": task_data_instance,
                    }
                )
                instances.append(instance["source"])
                """
                We also have access to: instance["target"]
                                        instance["references"]
                """
            return instances

        return [t["source"] for t in task_data]


class LLMAsJudgeRatingTaskFormatter(LLMAsJudgeTaskFormatter):
    task = "tasks.response_assessment.rating.single_turn"
    reduction_map_str = "mean"

    def get_single_instance_for_judge_model(
        self, input_instance: str, prediction: str, reference: List
    ):
        return {
            "question": input_instance,
            "answer": prediction,
        }

    def prediction_output_to_main_score(self, instance):
        return instance["prediction"]

    def get_input_instances(
        self,
        task_data: List[Dict],
        strip_system_prompt_and_format_from_inputs: bool = False,
    ):
        return self.get_input_instances_by_prompt_source(
            task_data, strip_system_prompt_and_format_from_inputs
        )


class LLMAsJudgeRatingWithReferenceTaskFormatter(LLMAsJudgeRatingTaskFormatter):
    task = "tasks.response_assessment.rating.single_turn_with_reference"

    def get_single_instance_for_judge_model(
        self, input_instance: str, prediction: str, reference: List
    ):
        return {
            "question": input_instance,
            "answer": prediction,
            "reference_answer": reference[0],
        }


class LLMAsJudgeCompareTaskFormatter(LLMAsJudgeTaskFormatter):
    task = "tasks.response_assessment.pairwise_comparative_rating.single_turn"
    reduction_map_str = "weighted_win_rate"

    def get_single_instance_for_judge_model(
        self, input_instance: str, prediction: str, reference: List
    ):
        return {
            "question": input_instance,
            "answer_a": prediction,
            "answer_b": reference[0],
            "model_a": "input_model",
            "model_b": "baseline_model",
        }

    def prediction_output_to_main_score(self, instance):
        import json

        # seems like the task data sometimes comes as a string, not a dict
        # this fixes it
        task_data = (
            json.loads(instance["task_data"])
            if isinstance(instance["task_data"], str)
            else instance["task_data"]
        )

        is_model_b_the_baseline = task_data["model_b"] == "baseline_model"
        if is_model_b_the_baseline:
            model_a_preference_score = instance["prediction"]
        else:
            model_a_preference_score = instance["prediction"] * -1
        return model_a_preference_score

    def get_input_instances(
        self,
        task_data: List[Dict],
        strip_system_prompt_and_format_from_inputs: str = False,
    ):
        return self.get_input_instances_by_prompt_source(
            task_data, strip_system_prompt_and_format_from_inputs
        )


class LLMAsJudgeBinaryTaskFormatter(LLMAsJudgeTaskFormatter):
    task = "tasks.rag_eval.answer_correctness.binary"
    reduction_map_str = "mean"
    infer_log_probs = True

    def get_single_instance_for_judge_model(
        self, input_instance: str, prediction: str, reference: List
    ):
        return input_instance

    def prediction_output_to_main_score(self, instance):
        return instance["prediction"]

    def get_input_instances(
        self,
        task_data: List[Dict],
        strip_system_prompt_and_format_from_inputs: str = False,
    ):
        return task_data


def task_suffix_to_task_formatter(task):
    task_suffix_to_task_formatter = {
        "rating.single_turn": LLMAsJudgeRatingTaskFormatter,
        "rating.single_turn_with_reference": LLMAsJudgeRatingWithReferenceTaskFormatter,
        "pairwise_comparative_rating.single_turn": LLMAsJudgeCompareTaskFormatter,
    }
    task_formatter_class = task_suffix_to_task_formatter.get(task)
    if task_formatter_class:
        return task_formatter_class
    if "binary" in task:
        return LLMAsJudgeBinaryTaskFormatter
    raise ValueError(f"Unsupported task for LLMaJ : {task}")


class LLMAsJudge(BulkInstanceMetric):
    """LLM-as-judge-based metric class for evaluating correctness.

    Attributes:
        main_score (str): The main score label used for evaluation.
        task (Literal["rating.single_turn"]): The type of task the llm as judge runs. This defines the output and input
         format of the judge model.
        template (Template): The template used when generating inputs for the judge llm.
        format (Format): The format used when generating inputs for judge llm.
        system_prompt (SystemPrompt): The system prompt used when generating inputs for judge llm.
        strip_system_prompt_and_format_from_inputs (bool): Whether to strip the system prompt and formatting from the
         inputs that the models that is being judges received, when they are inserted to the llm-as-judge prompt.
        inference_model (InferenceEngine): The module that creates the inference of the judge llm.
        reduction_map (dict): A dictionary specifying the reduction method for the metric.
        batch_size (int): The size of the bulk.
    """

    main_score: str = "llm_as_judge"
    task: str
    template: Template
    system_prompt: SystemPrompt = Field(default_factory=EmptySystemPrompt)
    format: Format = Field(default_factory=SystemFormat)
    strip_system_prompt_and_format_from_inputs: bool = True
    inference_model: InferenceEngine
    reduction_map: Optional[Dict[str, List[str]]] = None
    batch_size: int = 32
    prediction_type = Any  # Because handled with multiple tasks

    def _get_instance_for_judge_model(
        self, input_instances: List[str], predictions: List, references: List
    ) -> List[Dict]:
        return [
            self.task_formatter.get_single_instance_for_judge_model(
                input_instance, prediction, reference
            )
            for input_instance, prediction, reference in zip(
                input_instances, predictions, references
            )
        ]

    def get_single_instance_for_judge_model(
        self, input_instance, prediction, reference
    ):
        raise NotImplementedError

    def prepare(self):
        super().prepare()
        task_formatter_class = task_suffix_to_task_formatter(self.task)
        self.task_formatter = task_formatter_class()
        self.reduction_map = {self.task_formatter.reduction_map_str: [self.main_score]}

    def verify(self):
        if not isinstance(self.template, Template):
            raise ValueError(
                f"Provided template argument to 'LLMAsJudge' metric is not of type Template, but {type(self.template)}"
            )
        if self.format and not isinstance(self.format, Format):
            raise ValueError(
                f"Provided format argument to 'LLMAsJudge' metric is not of type Format, but {type(self.format)}"
            )

        if self.system_prompt and not isinstance(self.system_prompt, SystemPrompt):
            raise ValueError(
                f"Provided system_prompt argument to 'LLMAsJudge' metric is not of type SystemPrompt, but {type(self.system_prompt)}"
            )

        if isinstance(self.inference_model, OpenAiInferenceEngine):
            if self.format and type(self.format) is not SystemFormat:
                raise ValueError(
                    "Error in 'LLMAsJudge' metric. Inference model 'OpenAiInferenceEngine' does "
                    "not support formatting. Please remove the format definition from the recipe"
                    " (OpenAi Chat API take care of the formatting automatically)."
                )
            if self.system_prompt and type(self.system_prompt) is not EmptySystemPrompt:
                raise ValueError(
                    "Error in 'LLMAsJudge' metric. Inference model 'OpenAiInferenceEngine' does "
                    "not support system prompt. Please remove the system_prompt definition from the recipe"
                    " (Current implementation of Unitxt does not support this."
                    " Support will be added in future updates)."
                )

    def compute(
        self,
        references: List[List[Any]],
        predictions: List[Any],
        task_data: List[Dict],
    ) -> List[Dict[str, Any]]:
        input_instances = self.task_formatter.get_input_instances(
            task_data, self.strip_system_prompt_and_format_from_inputs
        )
        instances = self._get_instance_for_judge_model(
            input_instances, predictions, references
        )
        outputs = self.infer_instances(instances)

        results = []
        for instance in outputs:
            result = {
                self.main_score: self.task_formatter.prediction_output_to_main_score(
                    instance
                ),
                "judge_raw_output": instance["raw_prediction"],
                "judge_raw_input": instance["source"],
            }
            results.append(result)

        return results

    def infer_instances(self, instances):
        return infer(
            instances,
            engine=self.inference_model,
            task=self.task_formatter.task,
            template=self.template,
            system_prompt=self.system_prompt,
            format=self.format,
            return_data=True,
            infer_log_probs=self.task_formatter.infer_log_probs,
        )
