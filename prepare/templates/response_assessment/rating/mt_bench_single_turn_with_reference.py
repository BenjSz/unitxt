from unitxt.catalog import add_to_catalog
from unitxt.templates import InputOutputTemplate

add_to_catalog(
    InputOutputTemplate(
        instruction="Please act as an impartial judge and evaluate the quality of the response provided"
        " by an AI assistant to the user question displayed below. Your evaluation should consider"
        " correctness and helpfulness. You will be given a reference answer and the assistant's answer."
        " Begin your evaluation by comparing the assistant's answer with the reference answer."
        " Identify and correct any mistakes. Be as objective as possible. After providing your explanation,"
        " you must rate the response on a scale of 1 to 10 by strictly following this format:"
        ' "[[rating]]", for example: "Rating: [[5]]".\n\n',
        input_format="[Question]\n{question}\n\n"
        "[The Start of Reference Answer]\n{reference_answer}\n[The End of Reference Answer]\n\n"
        "[The Start of Assistant's Answer]\n{answer}\n[The End of Assistant's Answer]",
        output_format="[[{rating}]]",
        postprocessors=[
            r"processors.extract_mt_bench_rating_judgment",
        ],
    ),
    "templates.response_assessment.rating.mt_bench_single_turn_with_reference",
    overwrite=True,
)

add_to_catalog(
    InputOutputTemplate(
        instruction="Please act as an impartial judge and evaluate the quality of the response provided"
        " by an AI assistant to the user question displayed below. Your evaluation should consider"
        " relevance, accuracy, and strict adherence to the given instructions."
        " Begin your evaluation by providing a short explanation. Be as"
        " objective as possible. After providing your explanation, you must rate the response"
        ' on a scale of 1 to 10 by strictly following this format: "[[rating]]", for example:'
        ' "Rating: [[5]]".\n\n',
        input_format="[Question]\n{question}\n\n"
        "[The Start of Reference Answer]\n{reference_answer}\n[The End of Reference Answer]\n\n"
        "[The Start of Assistant's Answer]\n{answer}\n[The End of Assistant's Answer]",
        output_format="[[{rating}]]",
        postprocessors=[
            r"processors.extract_mt_bench_rating_judgment",
        ],
    ),
    "templates.response_assessment.rating.mt_bench_single_turn_strict_with_reference",
    overwrite=True,
)

