import json
from typing import Any, Dict, List, Optional

from datasets import Features, Sequence, Value

from .artifact import Artifact
from .dict_utils import dict_get
from .operator import InstanceOperatorValidator

UNITXT_DATASET_SCHEMA = Features(
    {
        "source": Value("string"),
        "target": Value("string"),
        "references": Sequence(Value("string")),
        "metrics": Sequence(Value("string")),
        "groups": Sequence(Value("string")),
        "subset": Sequence(Value("string")),
        "postprocessors": Sequence(Value("string")),
        "task_data": Value(dtype="string"),
        "data_classification_policy": Sequence(Value("string")),
    }
)


class Finalize(InstanceOperatorValidator):
    group_by: List[List[str]]
    remove_unnecessary_fields: bool = True

    @staticmethod
    def artifact_to_jsonable(artifact):
        if artifact.__id__ is None:
            return artifact.to_dict()
        return artifact.__id__

    def process(
        self, instance: Dict[str, Any], stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        metadata = {
            "data_classification_policy": instance["data_classification_policy"],
            "template": self.artifact_to_jsonable(
                instance["recipe_metadata"]["template"]
            ),
            "num_demos": instance["recipe_metadata"]["num_demos"],
        }
        task_data = {
            **instance["input_fields"],
            **instance["reference_fields"],
            "metadata": metadata,
        }
        instance["task_data"] = json.dumps(task_data)

        if self.remove_unnecessary_fields:
            keys_to_delete = []

            for key in instance.keys():
                if key not in UNITXT_DATASET_SCHEMA:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del instance[key]

        data = {**task_data, **metadata}
        groups = []
        for group_attributes in self.group_by:
            group = {}
            if isinstance(group_attributes, str):
                group_attributes = [group_attributes]
            for attribute in group_attributes:
                group[attribute] = dict_get(data, attribute)
            groups.append(json.dumps(group))

        instance["groups"] = groups
        instance["subset"] = []

        instance["metrics"] = [
            metric.to_json() if isinstance(metric, Artifact) else metric
            for metric in instance["metrics"]
        ]
        instance["postprocessors"] = [
            processor.to_json() if isinstance(processor, Artifact) else processor
            for processor in instance["postprocessors"]
        ]

        return instance

    def validate(self, instance: Dict[str, Any], stream_name: Optional[str] = None):
        # verify the instance has the required schema
        assert instance is not None, "Instance is None"
        assert isinstance(
            instance, dict
        ), f"Instance should be a dict, got {type(instance)}"
        assert all(
            key in instance for key in UNITXT_DATASET_SCHEMA
        ), f"Instance should have the following keys: {UNITXT_DATASET_SCHEMA}. Instance is: {instance}"
        UNITXT_DATASET_SCHEMA.encode_example(instance)
