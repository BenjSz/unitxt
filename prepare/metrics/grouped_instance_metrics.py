import numpy as np

from src.unitxt import add_to_catalog
from src.unitxt.metrics import (
    MeanGroupedAccuracy,
    MeanGroupedAccuracyPDR,
    MeanGroupedStringContainment,
    MeanGroupedStringContainmentPDR,
    MeanGroupedTokenOverlap,
)
from src.unitxt.test_utils.metrics import test_metric

predictions = [
    "A B",
    "BC D",
    "C",
    "123",
    "BCD",
    10,
    "  BD",
    "AB",
    "I am a dog",
    "AB C",
    "AB 1",
    "GMA",
    0.123,
    "BD",
    "abc",
]

references = [
    ["B", "AB", "A"],
    ["A", "BC D", "BC DF"],
    ["c", " C"],
    [13, 23, 234],
    ["  ", " BD", " BDA"],
    [1, 10, 100],
    ["A", "B", "BD"],
    ["ABC", "ab", "BC"],
    ["I am a person", "I AM A DOG", "ABC"],
    ["AB CD", "AB", "ab"],
    ["AB 1", "AB1"],
    [" GMA 123", "GMA"],
    ["123", 0.12],
    ["BDE", "BCE", "bdefs"],
    [" abcdefg", "AB", "abcd"],
]

# possibly multi-column group identifier
additional_inputs = (
    [{"group": "grp1", "id": 0, "ignore": 1}] * 5
    + [{"group": "grp1", "id": 1, "ignore": 1}] * 5
    + [{"group": "grp2", "id": 0, "ignore": 1}] * 4
    + [{"group": "grp2", "id": 1, "ignore": 0}] * 1
)

group_by_fields = ["group", "id"]
# construct grouping_field by combining two other fields (and ignoring one); mimics what you would do in cards
for ai in additional_inputs:
    ai.update({"group_id": "_".join([str(ai[ff]) for ff in group_by_fields])})


instance_targets_string_containment = [
    {"score": 1.0
    },
    {
        "score": 1.0
    },
    {
        "score": 0.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 0.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 0.0,
    },
    {
        "score": 0.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 1.0,
    },
    {
        "score": 0.0,
    },
    {
        "score": 0.0,
    },
]

for instance in instance_targets_string_containment:
    instance.update({"string_containment": instance["score"], "score_name": "string_containment"})

instance_targets_accuracy = [
    {"score": 0.0},
    {"score": 1.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 1.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 1.0},
    {"score": 1.0},
    {"score": 0.0},
    {"score": 0.0},
    {"score": 0.0},
]

for instance in instance_targets_accuracy:
    instance.update({"accuracy": instance["score"], "score_name": "accuracy"})

metric = MeanGroupedAccuracy()
global_target = {
    "group_mean_accuracy": 0.23,
    "score": 0.23,
    "score_name": "group_mean_accuracy",
    "score_ci_low": 0.02,
    "score_ci_high": 0.44,
    "group_mean_accuracy_ci_low": 0.02,
    "group_mean_accuracy_ci_high": 0.44,
}


outputs = test_metric(
    metric=metric,
    predictions=predictions,
    references=references,
    instance_targets=instance_targets_accuracy,
    global_target=global_target,
    additional_inputs=additional_inputs,
)

add_to_catalog(metric, "metrics.group_mean_accuracy", overwrite=True)


metric = MeanGroupedStringContainment()
global_target = {
    "group_mean_string_containment": 0.49,
    "score": 0.49,
    "score_name": "group_mean_string_containment",
    "score_ci_low": 0.16,
    "score_ci_high": 0.71,
    "group_mean_string_containment_ci_low": 0.16,
    "group_mean_string_containment_ci_high": 0.71,
}


outputs = test_metric(
    metric=metric,
    predictions=predictions,
    references=references,
    instance_targets=instance_targets_string_containment,
    global_target=global_target,
    additional_inputs=additional_inputs,
)

add_to_catalog(metric, "metrics.group_mean_string_containment", overwrite=True)


# PDR
metric = MeanGroupedAccuracyPDR()
global_target = {
    "group_pdr_accuracy": 0.83,
    "score": 0.83,
    "score_name": "group_pdr_accuracy",
    "score_ci_low": np.nan,
    "score_ci_high": np.nan,
    "group_pdr_accuracy_ci_low": np.nan,
    "group_pdr_accuracy_ci_high": np.nan,
}


outputs = test_metric(
    metric=metric,
    predictions=predictions,
    references=references,
    instance_targets=instance_targets_accuracy,
    global_target=global_target,
    additional_inputs=additional_inputs,
)

add_to_catalog(metric, "metrics.group_pdr_accuracy", overwrite=True)


metric = MeanGroupedStringContainmentPDR()
global_target = {
    "group_pdr_string_containment": 0.44,
    "score": 0.44,
    "score_name": "group_pdr_string_containment",
    "score_ci_low": np.nan,
    "score_ci_high": np.nan,
    "group_pdr_string_containment_ci_low": np.nan,
    "group_pdr_string_containment_ci_high": np.nan,
}


outputs = test_metric(
    metric=metric,
    predictions=predictions,
    references=references,
    instance_targets=instance_targets_string_containment,
    global_target=global_target,
    additional_inputs=additional_inputs,
)

add_to_catalog(metric, "metrics.group_pdr_string_containment", overwrite=True)


# create references and predictions with only 3 unique values
short_predictions = [
    "A",
    "B",
    "B",
    "A",
    "B",
    "B",
    "A",
    "A",
    "B",
    "B",
    "A",
    "B",
    "A",
    "A",
    "B",
]

short_references = [
    ["A", "B"],
    ["A", "C"],
    ["B", "C", "A"],
    ["A"],
    ["B", "A"],
    ["C", "B"],
    ["A"],
    ["B", "C"],
    ["A", "B", "C"],
    ["A", "B"],
    ["B", "C"],
    ["C"],
    ["C", "B"],
    ["B", "A"],
    ["B"],
]
# f1_references = [[rr] for rr in f1_references]
instance_targets_f1 = [
    {"group_mean_f1_macro": 0.5, "score": 0.5, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.0, "score": 0.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.33, "score": 0.33, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 1.0, "score": 1.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.5, "score": 0.5, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.5, "score": 0.5, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 1.0, "score": 1.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.0, "score": 0.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.33, "score": 0.33, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.5, "score": 0.5, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.0, "score": 0.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.0, "score": 0.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.0, "score": 0.0, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 0.5, "score": 0.5, "score_name": "group_mean_f1_macro"},
    {"group_mean_f1_macro": 1.0, "score": 1.0, "score_name": "group_mean_f1_macro"},
]


global_target = {"group_mean_f1": 0.5,
                 "score": 0.5,
                 "score_name": "group_mean_f1",
                 "group_mean_f1_ci_low": 0.32,
                 "group_mean_f1_ci_high": 0.79,
                 "score_ci_low": 0.32,
                 "score_ci_high": 0.79,
                 "group_mean_precision": 0.5,
                 "group_mean_precision_ci_low": 0.32,
                 "group_mean_precision_ci_high": 0.79,
                 "group_mean_recall": 0.5,
                 "group_mean_recall_ci_low": 0.32,
                 "group_mean_recall_ci_high": 0.79}

instance_targets_token_overlap = [{"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 0, "recall": 0, "f1": 0, "score": 0, "score_name": "f1"},
                                  {"precision": 1.0,
                                   "recall": 1.0,
                                   "f1": 1.0,
                                   "score": 1.0,
                                   "score_name": "f1"}]



metric = MeanGroupedTokenOverlap()

outputs = test_metric(
    metric=metric,
    predictions=short_predictions,
    references=short_references,
    instance_targets=instance_targets_token_overlap,
    global_target=global_target,
    additional_inputs=additional_inputs,
)

add_to_catalog(metric, "metrics.group_mean_f1_macro_multilabel", overwrite=True)
