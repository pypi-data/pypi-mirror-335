from typing import List

from pydantic import BaseModel, Field

from duowen_agent.llm import Message, MessagesSet
from duowen_agent.llm.chat_model import OpenAIChat
from duowen_agent.llm.utils import format_messages
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder, practice_dir
from duowen_agent.utils.core_utils import json_observation
from duowen_agent.utils.string_template import StringTemplate


class AnalysisResult(BaseModel):
    theme_switch_points: List[str] = Field(
        ..., description="对话中的主题切换点，通常是一些关键的对话片段"
    )
    filtered_content: str = Field(..., description="经过筛选后与新问题相关的内容")


class AnalysisOutput(BaseModel):
    analysis_result: AnalysisResult = Field(
        ..., description="分析结果，包含主题切换点和筛选内容"
    )
    new_question: str = Field(..., description="基于筛选内容生成的逻辑连贯的新问题")


class MergeContexts:
    def __init__(self, llm_instance: OpenAIChat):
        self.llm_instance = llm_instance

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction="""根据对话转录文本，构建一个新的问题。
  
分析对话转录文本，识别主题切换的关键点，并选择与构建新问题相关的对话内容，确保保留与主题紧密相关的部分。利用筛选后的对话内容生成逻辑连贯、语义一致的新问题，确保新问题涵盖所有关键信息且不遗漏原始对话的重要细节。

## 具体要求

- **理解任务目标**：
1. 识别对话中主题切换的关键点。
2. 筛选与生成新问题紧密相关的对话内容。
3. 构建能够总结筛选内容的高质量问题。

- **保留用户内容**：忠实保留用户提供的指令，不进行不必要的改动。
- **推理先于结论**：在新问题生成前，首先明确筛选过程及理由，再构建新问题。
- **输出清晰简洁**：去除冗余说明，仅输出分析结果和新问题。
- **格式化**：提供结构化的输出，避免信息混乱。""",
            step="""1. **主题切换分析**：
 - 检查对话转录文本，定位对话中话题的显著转变点。
 - 记录与新问题构建相关的关键对话内容。

2. **筛选相关内容**：
 - 去除与主题无关的内容。
 - 保留必要的上下文信息以确保新问题的语义完整性。

3. **构建新问题**：
 - 根据筛选的内容，生成逻辑清晰、语义连贯的新问题。
 - 确保问题能够独立理解，无需依赖原始对话内容。""",
            output_format=AnalysisOutput,
            sample='''## 示例1
  
**输入示例**

历史对话内容:
```
user：我们需要讨论季度预算问题。
assistant：好的，请问具体有哪些方面需要考虑？
user：除了人员成本，还要评估市场推广费用。
assistant：明白了，这部分费用是否有上限？
```

最新消息:
```
用户：暂时没有明确，但希望尽可能优化。
```

**输出示例**

```json
{
"analysis_result": {
  "theme_switch_points": ["用户提到市场推广费用", "助手询问费用是否有上限"],
  "filtered_content": "用户提到市场推广费用需要优化，但目前没有明确上限。"
},
"new_question": "季度预算中，市场推广费用如何在没有明确上限的情况下进行优化？"
}
```

## 示例2

**输入示例**

历史对话内容:
```
用户：我需要一个函数来检查一个数字是否是素数。
助手：好的，函数需要使用哪种语言编写？
用户：用 Python 吧，而且需要返回一个布尔值。
助手：明白了，这是一个简单的实现：
```

```python
def is_prime(n):
  """检查一个数字是否为素数"""
  if n <= 1:
      return False
  for i in range(2, int(n**0.5) + 1):
      if n % i == 0:
          return False
  return True
```
```

最新消息:
```
用户：代码实现得很清晰，但能否逐行解释一下这段代码的逻辑和作用？
```

**输出示例**

```json
{
"analysis_result": {
  "theme_switch_points": [
    "用户提出素数检查函数需求",
    "用户请求对输出代码的逐行逻辑进行解释"
  ],
  "filtered_content": "用户需要一个用 Python 编写的函数来检查数字是否为素数，并请求对以下代码逐行解释：

def is_prime(n):
  """检查一个数字是否为素数"""
  if n <= 1:
      return False
  for i in range(2, int(n**0.5) + 1):
      if n % i == 0:
          return False
  return True"
},
"new_question": "如何逐行解释以下代码，使其逻辑和作用对非技术背景的用户易于理解？

def is_prime(n):
  """检查一个数字是否为素数"""
  if n <= 1:
      return False
  for i in range(2, int(n**0.5) + 1):
      if n % i == 0:
          return False
  return True",
}
```''',
            note="""- **语义一致性**：确保生成问题的逻辑顺畅，避免信息矛盾。
- **问题独立性**：新问题应具备完整的上下文，无需依赖原始对话理解。
- **筛选精确性**：仅保留对问题生成具有决定性意义的对话内容。""",
        ).export_yaml(practice_dir + "/merge_contexts.yaml")

    def run(self, question: List[dict] | List[Message] | MessagesSet):
        _question = format_messages(question)
        _history = [i.to_dict() for i in _question.message_list[:-1]]
        _history_content = "\n\n".join(
            [f'{i["role"]}:\n{i["content"]}' for i in _history]
        )
        _new = _question.message_list[-1]
        _prompt = GeneralPromptBuilder.load("merge_contexts").get_instruction(
            user_input=f"- 历史对话内容:\n```\n{_history_content}\n```\n\n- 最新消息:\n```\n{_new.content}\n```"
        )

        res = self.llm_instance.chat(_prompt)
        res: AnalysisOutput = json_observation(res, AnalysisOutput)
        return res.new_question


class Continued(BaseModel):
    is_continued: bool = Field(description="存在话题延续性为true否则为false")


class TopicContinues:

    def __init__(self, llm_instance: OpenAIChat):
        self.llm_instance = llm_instance

    @staticmethod
    def build_prompt():
        GeneralPromptBuilder(
            instruction=StringTemplate(
                template="分析用户最新消息与之前{num}轮对话内容，判断是否存在话题延续性。",
            ),
            step=StringTemplate(
                template="""1. **追溯对话历史**：
   - 提取最近{num}轮对话内容（包括用户当前消息）
   - 重点标记用户当前消息
2. **识别关键要素**：
   - 操作指令词库匹配（请/帮我/需要...）
   - 社交寒暄模式识别（问候/感谢/客套话）
   - 代词指代消解（这/那/它等上下文绑定）
   - 包含任务参数延续（时间/地点/数量的渐进调整）
3. **排除非延续情况**：
   - 纯社交性表达（类似"谢谢"_"您好"_"麻烦了"等）
   - 跳转至完全无关话题领域
4. **逻辑链验证**：
   - 检查当前消息是否服务于同一任务目标
   - 确认存在观点延伸/条件补充/细节深挖等延续特征
   - 辨别是否出现逆向推理链（质疑反驳/否定前提）""",
            ),
            output_format=Continued,
            note="""1. 特别注意"这/那+量词"结构的隐性指代（如"那个方案"_"这份文件"）
2. 关注时间序列关联（"上次"_"之前"_"刚才"_"接下来"）
3. 警惕伪装延续场景（表面相似但语义断裂的情况）
3. 当出现复合意图时（如闲聊中带请求），需要特别评估请求是否存在延续性
4. 对于模糊指代需通过上下文验证真实指涉对象""",
        ).export_yaml(practice_dir + "/topic_continues_check.yaml")

    def run(self, question: List[dict] | List[Message] | MessagesSet, num: int = 3):
        _question = format_messages(question)
        _history = [i.to_dict() for i in _question.message_list[:-1]]
        _history_content = "\n\n".join(
            [f'消息_{e+1} {i["role"]}:\n{i["content"]}' for e, i in enumerate(_history)]
        )
        _new = _question.message_list[-1]
        _prompt = GeneralPromptBuilder.load("topic_continues_check").get_instruction(
            user_input=f"- 历史对话内容:\n```\n{_history_content}\n```\n\n- 最新消息:\n```\n{_new.content}\n```",
            temp_vars={"num": num},
        )
        res = self.llm_instance.chat(_prompt)
        res: Continued = json_observation(res, Continued)
        return res.is_continued


class DetectionMergeContexts:
    def __init__(self, llm_instance: OpenAIChat, **kwargs):
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    def run(
        self, question: List[dict] | List[Message] | MessagesSet, num: int = 3
    ) -> str:
        _question = format_messages(question)

        res = TopicContinues(self.llm_instance).run(_question, num)

        if res:
            return MergeContexts(llm_instance=self.llm_instance).run(question)

        return _question.message_list[-1].content


if __name__ == "__main__":
    TopicContinues.build_prompt()
    MergeContexts.build_prompt()
