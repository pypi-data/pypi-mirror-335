from typing import List

from pydantic import BaseModel, Field

from duowen_agent.llm import OpenAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder, practice_dir
from duowen_agent.utils.core_utils import json_observation


class Abstract(BaseModel):
    title: str = Field(..., description="文章标题")
    keywords: List[str] = Field(
        ..., description='["关键词1", "关键词2", "同义词1", "相关短语1",...]'
    )
    entity: List[str] = Field(
        ...,
        description='["人名","组织名","地点","时间表达式","产品","事件",...]',
    )
    abstract: str = Field(..., description="150-200字的摘要，逻辑清晰，简明扼要")


class SeoSummary:
    """
    面向搜索引擎的文章摘要
    """

    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction="编写面向搜索引擎的文章摘要，对文章进行摘要编写，以提高其在搜索引擎中的检索率。",
            step="""1. 主题分析： 阅读文章，确定主题和核心信息，将其总结为一句简洁描述。
2. 关键词提取： 仔细阅读文章，提取最重要的关键词。
3. 实体提取: 仔细阅读文章，提取最重要的关键实体，如人名、组织名、地点、时间表达式、产品、事件等。
4. 初稿编写： 基于关键词、实体和核心信息，编写150-200字的初稿摘要。
5. 关键词和实体融入： 确保摘要包含所有重要关键词和实体，保持自然流畅，避免堆砌。
6. 语义扩展： 使用同义词或相关短语替代部分关键词，提升语义覆盖面。""",
            output_format=Abstract,
            note="""- the selection must be singular .
- Respond with JSON code only without any explanations and comments. -- just the JSON code.""",
        ).export_yaml(practice_dir + "/seo_summary.yaml")

    def run(
        self,
        question: str,
        **kwargs,
    ) -> Abstract:
        _prompt = GeneralPromptBuilder.load("seo_summary").get_instruction(question)

        _res = self.llm_instance.chat(_prompt)

        _res: Abstract = json_observation(_res, Abstract)

        return _res


if __name__ == "__main__":
    SeoSummary.build_prompt()
