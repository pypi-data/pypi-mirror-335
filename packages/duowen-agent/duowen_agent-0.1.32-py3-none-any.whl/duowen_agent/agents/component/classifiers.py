from typing import List, Tuple

from pydantic import BaseModel, Field

from duowen_agent.error import ObserverException
from duowen_agent.llm import OpenAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder, practice_dir
from duowen_agent.utils.core_utils import json_observation
from duowen_agent.utils.string_template import StringTemplate


class CategoriesOne(BaseModel):
    category_name: str = Field(
        description="Exactly the name of the category that matches"
    )


class CategoriesMulti(BaseModel):
    category_names: List[str] = Field(
        description="Select one or more applicable categories"
    )


class ClassifiersOne:
    """
    单选分类器
    """

    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction=StringTemplate(
                """Your task is to assign one categories ONLY to the input text and only one category may be assigned returned in the output.

The categories are:
{% for key, value in categories.items() %}
- {{key}}: {{value}}
{% endfor %}""",
                "jinja2",
            ),
            output_format=CategoriesOne,
            note="""- the selection must be singular .
- Respond with JSON code only without any explanations and comments. -- just the JSON code.""",
        ).export_yaml(practice_dir + "/classifiers_one.yaml")

    def run(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ):
        _prompt = GeneralPromptBuilder.load("classifiers_one")
        if sample:
            _sample = []
            for i in sample:
                _q = i[0]
                _a = f"```json\n{CategoriesOne(category_name=i[1]).model_dump(mode='json')}\n```\n"
                _sample.append((_q, _a))

            _prompt.sample = "\n".join(
                [
                    f"## sample_{i+1}\ninput:\n{d[0]}\n\noutput:\n{d[1]}"
                    for i, d in enumerate(_sample)
                ]
            )

        _prompt = _prompt.get_instruction(
            user_input=question,
            temp_vars={
                "categories": categories,
            },
        )

        _res = self.llm_instance.chat(_prompt)
        _res: CategoriesOne = json_observation(_res, CategoriesOne)
        if _res.category_name in categories:
            return _res.category_name
        else:
            raise ObserverException(
                predict_value=_res.category_name,
                expect_value=str(categories.keys()),
                err_msg="observation error values",
            )


class ClassifiersMulti:
    """
    多选分类器
    """

    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction=StringTemplate(
                """Your task is to assign one or more categories to the input text and the output may include one or more categories.

The categories are:
{% for key, value in categories.items() %}
- {{key}}: {{value}}
{% endfor %}""",
                "jinja2",
            ),
            output_format=CategoriesMulti,
            note="""Respond with JSON code only without any explanations and comments. -- just the JSON code.""",
        ).export_yaml(practice_dir + "/classifiers_multi.yaml")

    def run(
        self,
        question: str,
        categories: dict[str:str],
        sample: List[Tuple] = None,
        **kwargs,
    ):
        _prompt = GeneralPromptBuilder.load("classifiers_multi")
        if sample:
            _sample = []
            for i in sample:
                _q = i[0]
                _a = f"```json\n{CategoriesMulti(category_names=[i[1]] if isinstance(i[1],str) else i[1]).model_dump(mode='json')}\n```\n"
                _sample.append((_q, _a))

            _prompt.sample = "\n".join(
                [
                    f"## sample_{i + 1}\ninput:\n{d[0]}\n\noutput:\n{d[1]}"
                    for i, d in enumerate(_sample)
                ]
            )

        _prompt = _prompt.get_instruction(
            user_input=question,
            temp_vars={
                "categories": categories,
            },
        )

        _res = self.llm_instance.chat(_prompt)

        _res: CategoriesMulti = json_observation(_res, CategoriesMulti)

        for i in _res.category_names:
            if i not in categories:
                raise ObserverException(
                    predict_value=i,
                    expect_value=str(categories.keys()),
                    err_msg="observation error values",
                )
        return _res.category_names


if __name__ == "__main__":
    ClassifiersOne.build_prompt()
    ClassifiersMulti.build_prompt()
