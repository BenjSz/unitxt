from unitxt import add_to_catalog
from unitxt.metrics import (
    GenerativeBinaryJudgeBAM,
    GenerativeBinaryJudgeOpenAi,
    GenerativeBinaryJudgeWML,
    MetricPipeline,
)
from unitxt.operators import Copy, Set

rag_fields = {"ground_truths", "answer", "contexts", "question"}

metric_type_to_template = {
    "faithfulness": {
        "q_c_a": "judge_with_question_simplified_logprobs",
        "c_a": "judge_with_question_simplified_logprobs",
    },
    "context_relevance": {"q_c": "judge_context_relevance_ares_logprobs"},
    "correctness_holistic": {"q_c_a": "judge_correctness_simple_logprobs"},  # qca
    "answer_correctness": {
        "q_c_a_gt": "judge_simplified_with_context_logprobs",
        "q_a_gt": "judge_loose_match_no_context_logprobs",
        "q_a_gt_strict": "judge_simplified_format_logprobs",
    },
    "answer_relevance": {"q_a": "judge_answer_relevance_logprobs"},
}

model_names_to_metric_classes = {
    "meta-llama/llama-3-1-70b-instruct": [GenerativeBinaryJudgeWML],
    "meta-llama/llama-3-70b-instruct": [GenerativeBinaryJudgeBAM],
    "gpt-4-turbo": [GenerativeBinaryJudgeOpenAi],
    "mistralai/mixtral-8x7b-instruct-v01": [
        GenerativeBinaryJudgeWML,
        GenerativeBinaryJudgeBAM,
    ],
    "meta-llama/llama-3-1-405b-instruct-fp8": [GenerativeBinaryJudgeBAM],
}


def add_judge_metrics():
    for judge_model_name, judge_metric_classes in model_names_to_metric_classes.items():
        for judge_metric_class in judge_metric_classes:
            template_format = (
                "formats.llama3_instruct"
                if "llama" in judge_model_name
                else "formats.empty"
            )
            for (
                metric_type,
                input_fields_to_template_name,
            ) in metric_type_to_template.items():
                for (
                    input_fields_str,
                    template_name,
                ) in input_fields_to_template_name.items():
                    metric_name = f"""{metric_type}_{input_fields_str}_judge_{judge_model_name.split("/")[-1].replace("-","_")}"""

                    if judge_metric_class == GenerativeBinaryJudgeBAM:
                        metric_name += "_bam"
                    metric = judge_metric_class(
                        main_score=metric_name,
                        model_name=judge_model_name,
                        task_name=f"tasks.rag_eval.{metric_type}.binary",
                        template_name=f"templates.rag_eval.{metric_type}.{template_name}",
                        model_format_name=template_format,
                    )

                    metric_pipeline = MetricPipeline(
                        main_score=metric_name,
                        metric=metric,
                        preprocess_steps=[
                            Copy(
                                field_to_field={
                                    field: f"task_data/{field}"
                                    for field in sorted(rag_fields)
                                },
                                not_exist_ok=True,
                            ),
                            Copy(
                                field_to_field={
                                    "data_classification_policy": "task_data/data_classification_policy"
                                },
                                not_exist_ok=True,
                                get_default=["public"],
                            ),
                            Set(
                                fields={
                                    "prediction": 0.0,  # these are not used by the metric
                                    "references": [0.0],
                                }
                            ),
                        ],
                    )

                    add_to_catalog(
                        metric_pipeline,
                        name=f"metrics.rag.{metric_type}.{metric_name}",
                        overwrite=True,
                    )


add_judge_metrics()
