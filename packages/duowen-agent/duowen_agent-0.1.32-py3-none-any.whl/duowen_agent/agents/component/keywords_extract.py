from typing import List

from pydantic import BaseModel, Field

from duowen_agent.llm import OpenAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder, practice_dir
from duowen_agent.utils.core_utils import json_observation
from duowen_agent.utils.string_template import StringTemplate


class Keywords(BaseModel):
    keywords: List[str] = Field(description="提取的中/英文关键词列表")


class KeywordExtract:
    """
    关键词抽取，用于提升全文或向量检索的泛化能力
    """

    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction="根据问题内容提取中/英文关键词，结合资料库语言习惯扩展相关概念，用于文本匹配检索",
            step=StringTemplate(
                """1. 分析句子核心语义，识别关键实体、行为、属性和关联对象
2. 拆分复合词为独立语义单元（如环境污染控制→环境污染/控制）
3. 补充专业术语、同义词、具体实例等关联概念
4. 英文内容优先保留原词，必要情况增加缩写形式
5. 人工概念判断优先于机械分词，保留完整术语
6. 5-{{num}}个精准关键词（宁缺毋滥）""",
                template_format="jinja2",
            ),
            output_format=Keywords,
            sample="""输入：如何评估企业数字化转型对员工生产力的影响

输出:
```json
{
    "keywords": ["数字化转型","生产力分析","组织变革","办公效率","员工培训","数字化工具","KPI评估","远程办公","流程自动化","人机协作",...]
}
```

""",
            note="""- 名词词组控制在4字以内，动词词组3字以内
- 人名机构名保持完整（如世界卫生组织不拆分）
- 数字组合保留原格式（5G/30%减排）
- 排除助词、介词等非实义词
- 带注音专业词汇保持完整（CRISPR-Cas9/F22战机）
""",
        ).export_yaml(practice_dir + "/keyword_extract.yaml")

    def run(self, question: str, num: int = 10):

        _prompt = GeneralPromptBuilder.load("keyword_extract").get_instruction(
            user_input=f"输入: {question}",
            temp_vars={"num": num},
        )
        res = self.llm_instance.chat(_prompt)
        res: Keywords = json_observation(res, Keywords)
        return res.keywords


if __name__ == "__main__":
    KeywordExtract.build_prompt()
