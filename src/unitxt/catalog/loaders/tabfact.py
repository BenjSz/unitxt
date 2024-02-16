# Copyright 2020 The HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TabFact: A Large-scale Dataset for Table-based Fact Verification."""


import json
import os

import datasets

_CITATION = """\
@inproceedings{2019TabFactA,
  title={TabFact : A Large-scale Dataset for Table-based Fact Verification},
  author={Wenhu Chen, Hongmin Wang, Jianshu Chen, Yunkai Zhang, Hong Wang, Shiyang Li, Xiyou Zhou and William Yang Wang},
  booktitle = {International Conference on Learning Representations (ICLR)},
  address = {Addis Ababa, Ethiopia},
  month = {April},
  year = {2020}
}
"""

_DESCRIPTION = """\
The problem of verifying whether a textual hypothesis holds the truth based on the given evidence, \
also known as fact verification, plays an important role in the study of natural language \
understanding and semantic representation. However, existing studies are restricted to \
dealing with unstructured textual evidence (e.g., sentences and passages, a pool of passages), \
while verification using structured forms of evidence, such as tables, graphs, and databases, remains unexplored. \
TABFACT is large scale dataset with 16k Wikipedia tables as evidence for 118k human annotated statements \
designed for fact verification with semi-structured evidence. \
The statements are labeled as either ENTAILED or REFUTED. \
TABFACT is challenging since it involves both soft linguistic reasoning and hard symbolic reasoning.
"""

_HOMEPAGE = "https://tabfact.github.io/"

_GIT_ARCHIVE_URL = "https://github.com/wenhuchen/Table-Fact-Checking/archive/948b5560e2f7f8c9139bd91c7f093346a2bb56a8.zip"


class TabFact(datasets.GeneratorBasedBuilder):
    """TabFact: A Large-scale Dataset for Table-based Fact Verification."""

    VERSION = datasets.Version("1.0.0")

    def _info(self):
        features = {
            "id": datasets.Value("int32"),
            "table": {
                "id": datasets.Value("string"),
                "header": datasets.features.Sequence(datasets.Value("string")),
                "rows": datasets.features.Sequence(
                    datasets.features.Sequence(datasets.Value("string"))
                ),
                "caption": datasets.Value("string"),
            },
            "statement": datasets.Value("string"),
            "label": datasets.Value("int32"),
        }

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(features),
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        extracted_path = dl_manager.download_and_extract(_GIT_ARCHIVE_URL)

        repo_path = os.path.join(
            extracted_path,
            "Table-Fact-Checking-948b5560e2f7f8c9139bd91c7f093346a2bb56a8",  # pragma: allowlist secret
        )
        all_csv_path = os.path.join(repo_path, "data", "all_csv")

        train_statements_file = os.path.join(
            repo_path, "tokenized_data", "train_examples.json"
        )
        val_statements_file = os.path.join(
            repo_path, "tokenized_data", "val_examples.json"
        )
        test_statements_file = os.path.join(
            repo_path, "tokenized_data", "test_examples.json"
        )

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "statements_file": train_statements_file,
                    "all_csv_path": all_csv_path,
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "statements_file": val_statements_file,
                    "all_csv_path": all_csv_path,
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "statements_file": test_statements_file,
                    "all_csv_path": all_csv_path,
                },
            ),
        ]

    def _generate_examples(self, statements_file, all_csv_path):
        def convert_to_table_structure(table_str):
            header = table_str.split("\n")[0].split("#")
            rows = [row.split("#") for row in table_str.strip().split("\n")[1:]]
            return {"header": header, "rows": rows}

        with open(statements_file, encoding="utf-8") as f:
            examples = json.load(f)

        for i, (table_id, example) in enumerate(examples.items()):
            table_file_path = os.path.join(all_csv_path, table_id)
            with open(table_file_path, encoding="utf-8") as f:
                table_text = f.read()

            statements, labels, caption = example

            for statement_idx, (statement, label) in enumerate(zip(statements, labels)):
                table = convert_to_table_structure(table_text)
                yield (
                    f"{i}_{statement_idx}",
                    {
                        "id": i,
                        "table": {
                            "id": table_id,
                            "header": table["header"],
                            "rows": table["rows"],
                            "caption": caption,
                        },
                        "statement": statement,
                        "label": label,
                    },
                )
