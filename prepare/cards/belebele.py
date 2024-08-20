from unitxt.blocks import LoadHF
from unitxt.card import TaskCard
from unitxt.catalog import add_to_catalog
from unitxt.operators import (
    AddConstant,
    CastFields,
    ListFieldValues,
    RenameFields,
    Set,
)
from unitxt.test_utils.card import test_card

language_codes = [
    "acm_Arab",
    "arz_Arab",
    "ceb_Latn",
    "fin_Latn",
    "hin_Deva",
    "ita_Latn",
    "khm_Khmr",
    "lvs_Latn",
    "npi_Deva",
    "pol_Latn",
    "slv_Latn",
    "swe_Latn",
    "tso_Latn",
    "xho_Latn",
    "afr_Latn",
    "asm_Beng",
    "ces_Latn",
    "fra_Latn",
    "hin_Latn",
    "jav_Latn",
    "kin_Latn",
    "mal_Mlym",
    "npi_Latn",
    "por_Latn",
    "sna_Latn",
    "swh_Latn",
    "tur_Latn",
    "yor_Latn",
    "als_Latn",
    "azj_Latn",
    "ckb_Arab",
    "fuv_Latn",
    "hrv_Latn",
    "jpn_Jpan",
    "kir_Cyrl",
    "mar_Deva",
    "nso_Latn",
    "snd_Arab",
    "tam_Taml",
    "ukr_Cyrl",
    "zho_Hans",
    "amh_Ethi",
    "bam_Latn",
    "dan_Latn",
    "gaz_Latn",
    "hun_Latn",
    "kac_Latn",
    "kor_Hang",
    "mkd_Cyrl",
    "nya_Latn",
    "ron_Latn",
    "som_Latn",
    "tel_Telu",
    "urd_Arab",
    "zho_Hant",
    "apc_Arab",
    "ben_Beng",
    "deu_Latn",
    "grn_Latn",
    "hye_Armn",
    "kan_Knda",
    "lao_Laoo",
    "mlt_Latn",
    "ory_Orya",
    "rus_Cyrl",
    "sot_Latn",
    "tgk_Cyrl",
    "urd_Latn",
    "zsm_Latn",
    "arb_Arab",
    "ben_Latn",
    "ell_Grek",
    "guj_Gujr",
    "ibo_Latn",
    "kat_Geor",
    "lin_Latn",
    "mri_Latn",
    "pan_Guru",
    "shn_Mymr",
    "spa_Latn",
    "tgl_Latn",
    "uzn_Latn",
    "zul_Latn",
    "arb_Latn",
    "bod_Tibt",
    "eng_Latn",
    "hat_Latn",
    "ilo_Latn",
    "kaz_Cyrl",
    "lit_Latn",
    "mya_Mymr",
    "pbt_Arab",
    "sin_Latn",
    "srp_Cyrl",
    "tha_Thai",
    "vie_Latn",
    "ars_Arab",
    "bul_Cyrl",
    "est_Latn",
    "hau_Latn",
    "ind_Latn",
    "kea_Latn",
    "lug_Latn",
    "nld_Latn",
    "pes_Arab",
    "sin_Sinh",
    "ssw_Latn",
    "tir_Ethi",
    "war_Latn",
    "ary_Arab",
    "cat_Latn",
    "eus_Latn",
    "heb_Hebr",
    "isl_Latn",
    "khk_Cyrl",
    "luo_Latn",
    "nob_Latn",
    "plt_Latn",
    "slk_Latn",
    "sun_Latn",
    "tsn_Latn",
    "wol_Latn",
]

for lang in language_codes:
    card = TaskCard(
        loader=LoadHF(path="facebook/belebele", name=lang),
        preprocess_steps=[
            ListFieldValues(
                fields=["mc_answer1", "mc_answer2", "mc_answer3", "mc_answer4"],
                to_field="choices",
            ),
            RenameFields(
                field_to_field={
                    "correct_answer_num": "answer",
                    "flores_passage": "context",
                }
            ),
            CastFields(fields={"answer": "int"}),
            AddConstant(field="answer", add=-1),
            Set({"context_type": "passage"}),
        ],
        task="tasks.qa.multiple_choice.with_context",
        templates="templates.qa.multiple_choice.with_context.no_intro.all",
        __tags__={
            "arxiv": "2308.16884",
            "language": [
                "af",
                "am",
                "ar",
                "az",
                "as",
                "bm",
                "bn",
                "bo",
                "bg",
                "ca",
                "cs",
                "ku",
                "da",
                "de",
                "el",
                "en",
                "es",
                "et",
                "eu",
                "fi",
                "fr",
                "ff",
                "om",
                "gu",
                "gn",
                "ht",
                "ha",
                "he",
                "hi",
                "hr",
                "hu",
                "hy",
                "ig",
                "id",
                "it",
                "is",
                "jv",
                "ja",
                "ka",
                "kn",
                "kk",
                "mn",
                "km",
                "rw",
                "ky",
                "ko",
                "lo",
                "ln",
                "lt",
                "lg",
                "lv",
                "ml",
                "mr",
                "mk",
                "mt",
                "mi",
                "my",
                "nl",
                "no",
                "ne",
                "ny",
                "or",
                "pa",
                "ps",
                "fa",
                "mg",
                "pl",
                "pt",
                "ro",
                "ru",
                "sn",
                "si",
                "sl",
                "sv",
                "sk",
                "sd",
                "sw",
                "ta",
                "te",
                "tg",
                "tl",
                "th",
                "ti",
                "tn",
                "ts",
                "tr",
                "uk",
                "ur",
                "uz",
                "vi",
                "wo",
                "xh",
                "yo",
                "zh",
                "ms",
                "zu",
            ],
            "license": "cc-by-sa-4.0",
            "region": "us",
            "size_categories": "100K<n<1M",
            "task_categories": [
                "question-answering",
                "zero-shot-classification",
                "text-classification",
                "multiple-choice",
            ],
        },
        __description__=(
            "Belebele is a multiple-choice machine reading comprehension (MRC) dataset spanning 122 language variants. This dataset enables the evaluation of mono- and multi-lingual models in high-, medium-, and low-resource languages. Each question has four multiple-choice answers and is linked to a short passage from the FLORES-200 dataset. The human annotation procedure was carefully curated to create questions that… See the full description on the dataset page: https://huggingface.co/datasets/facebook/belebele."
        ),
    )

    if lang == language_codes[0]:
        test_card(card, demos_taken_from="test", strict=False)
    add_to_catalog(card, f"cards.belebele.{lang.lower()}", overwrite=True)
