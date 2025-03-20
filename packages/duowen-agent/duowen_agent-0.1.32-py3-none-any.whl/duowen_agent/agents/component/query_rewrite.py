from typing import Literal, Optional, List

from pydantic import BaseModel, Field

from duowen_agent.llm import OpenAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder, practice_dir
from duowen_agent.utils.core_utils import json_observation


class QuestionCategories(BaseModel):
    conflict: Optional[str] = Field(
        default=None, description="当存在跨级特征时的矛盾点"
    )
    reason: str = Field(..., description="16字内核心依据")
    category_name: Literal["简单直接", "多步骤", "多主题"] = Field(
        description="Exactly the name of the category that matches"
    )


class QueryClassification:

    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction="""根据问题特征进行三层稳定性分类，采用正交判别法

# 核心规则（独立互斥）
1. **简单直接类**必须满足：
   - 执行路径唯一且标准化（查表/转换/计算）
   - 所需参数≤2个且无动态依赖（如天气无需实时数据）

2. **多步骤类**触发条件：
   - 存在显性逻辑链 (因果/比较/条件) 
   OR
   - 需要3+参数动态组合（如温度+风速+场合）

3. **多主题类**严格标准：
   - 涉及两个独立知识域（领域重叠度＜30%）
   - 需要调用不同框架进行解答""",
            step="""```mermaid
graph TD
    A[原始问题] --> B{包含'>1'个问号}
    B -->|是| C[领域离散检测]
    C -->|离散度>0.6| D[多主题]
    B -->|否| E{存在逻辑关键词}
    E -->|是| F[多步骤]
    E -->|否| G[参数复杂度分析]
    G -->|参数≥3| F
    G -->|参数<3| H[简单直接]
```""",
            output_format=QuestionCategories,
            sample="""
输入：孙悟空和钢铁侠谁更加厉害？
输出：
```json
{"conflict":"表面简单但涉及跨体系能力比较","reason":"跨作品战力需多维评估","category_name":"多步骤"}
```

输入：如何用python编写排序算法？
输出：
```json
{"reason":"标准算法单文档可覆盖","category_name":"简单直接"}
```
""",
            note="""- 置信度锚定：各分类初始置信度 ≠ 可重叠范围
- 最终决策树：任一节点判定后立即阻断下游判断
- 语义消毒：自动滤除修饰性副词与情感词汇""",
        ).export_yaml(practice_dir + "/query_classification.yaml")

    def run(
        self,
        question: str,
        **kwargs,
    ) -> QuestionCategories:
        _prompt = GeneralPromptBuilder.load("query_classification").get_instruction(
            question
        )

        _res = self.llm_instance.chat(_prompt)

        _res: QuestionCategories = json_observation(_res, QuestionCategories)

        return _res


class SubTopic(BaseModel):
    original_subtopic: str = Field(..., description="原始问题中识别出的子主题描述")
    rewritten_query: str = Field(..., description="改进后的具体查询语句")


class TopicCategories(BaseModel):
    splitting: List[SubTopic] = Field(
        ..., description="必须生成**2-5个**改写版本，每个查询语句不超过25个汉字"
    )


class TopicSpliter:
    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction="当用户输入的问题包含多个隐藏的子问题或涉及不同领域时，将其分解为独立的具体查询并生成改写版本。为每个子主题生成聚焦单一意图的查询，确保全面覆盖原始问题的各个维度。",
            step="""1. **识别隐藏子问题**：先分析用户问题的语义结构，识别出隐含的独立话题或追问方向
2. **语义解耦**：将这些复合话题拆解为2-5个彼此独立的核心查询要素
3. **针对性改写**：针对每个单点问题生成优化后的查询版本，要求：
   - 保持原问题关键信息
   - 使用领域相关术语
   - 包含明确的范围限定词""",
            output_format=TopicCategories,
            sample="""
输入："我应该去哪里学习AI又适合旅游？"
输出：
```json
{
    "splitting": [
        {
            "original_subtopic": "教育质量",
            "rewritten_query": "全球人工智能专业顶尖高校排名",
        },
        {
            "original_subtopic": "生活体验",
            "rewritten_query": "留学热门城市旅游景点推荐",
        },
    ]
}
```""",
            note="""- 当问题存在多维度交叉时（如"[海外购房与税务]"），需分别生成"海外购房流程指南"和"跨境资产税务申报规则"两个独立查询
- 智能处理模糊表达：对于"好的科技公司标准"应拆解为"科技公司估值模型"和"员工福利标杆企业案例"
- 禁用通用型查询：将"有什么新技术？"强化为"[年度突破性半导体技术创新]"
- 确保可独立检索性：每个改写后的查询应能在主流搜索引擎中获得直接答案""",
        ).export_yaml(practice_dir + "/topic_spliter.yaml")

    def run(
        self,
        question: str,
        **kwargs,
    ) -> TopicCategories:
        _prompt = GeneralPromptBuilder.load("topic_spliter").get_instruction(question)

        _res = self.llm_instance.chat(_prompt)

        _res: TopicCategories = json_observation(_res, TopicCategories)

        return _res


if __name__ == "__main__":
    QueryClassification.build_prompt()
    TopicSpliter.build_prompt()
