import logging
import os
from typing import List

from openai import OpenAI

from duowen_agent.error import LLMError, LengthLimitExceededError, MaxTokenExceededError
from duowen_agent.llm.entity import (
    UserMessage,
    AssistantMessage,
    MessagesSet,
    Message,
)
from duowen_agent.llm.utils import format_messages


class OpenAIChat:
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.2,
        timeout: int = 120,
        token_limit: int = 4 * 1024,
        is_reasoning: bool = False,
        extra_headers: dict = None,
        **kwargs,
    ):
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", None)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "xxx")
        self.temperature = temperature
        self.model = model or kwargs.get("model_name", None) or "gpt-3.5-turbo"
        self.timeout = timeout
        self.token_limit = token_limit
        self.extra_headers = extra_headers
        self.is_reasoning = is_reasoning

        self.client = OpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    def _check_message(
        self, message: str | List[dict] | List[Message] | MessagesSet
    ) -> MessagesSet:
        return format_messages(message, self.is_reasoning)

    def _build_params(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        temperature: float = None,
        max_new_tokens: int = None,
        top_p: float = None,
        timeout: int = 30,
        forced_reasoning: bool = False,
        **kwargs,
    ):
        _message = self._check_message(messages)
        if self.is_reasoning:
            _message.remove_assistant_think()

        if self.is_reasoning and forced_reasoning and _message[-1].role == "user":
            _message.add_assistant("<think>\n")

        _params = {"messages": _message.get_messages(), "model": self.model}

        if temperature:
            _params["temperature"] = temperature
        elif self.temperature:
            _params["temperature"] = self.temperature
        else:
            if self.is_reasoning:
                _params["temperature"] = 0.6
            else:
                _params["temperature"] = 0.2

        if max_new_tokens:
            _params["max_tokens"] = max_new_tokens
        else:
            _params["max_tokens"] = 2000

        if top_p:
            _params["top_p"] = top_p
            # 如果用户调整 top_p 则删除 temperature 设置
            del _params["temperature"]

        if timeout:
            _params["timeout"] = timeout
        elif self.timeout:
            _params["timeout"] = self.timeout

        if self.extra_headers:
            _params["extra_headers"] = self.extra_headers

        if kwargs:
            for k, v in kwargs.items():
                _params[k] = v
        return _params

    def _chat_stream(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        temperature: float = None,
        max_new_tokens: int = None,
        top_p: float = None,
        timeout: int = 30,
        forced_reasoning=False,
        **kwargs,
    ):

        _params = self._build_params(
            messages,
            temperature,
            max_new_tokens,
            top_p,
            timeout,
            forced_reasoning,
            **kwargs,
        )
        _params["stream"] = True

        try:

            response = self.client.chat.completions.create(**_params)

            _full_message = ""
            _is_think_start = False
            _is_think_end = False

            for chunk in response:
                if chunk.choices:
                    if chunk.choices[0].finish_reason == "length":
                        raise LengthLimitExceededError(content=_full_message)
                    elif chunk.choices[0].finish_reason == "max_tokens":
                        raise MaxTokenExceededError(content=_full_message)

                    _content_msg = chunk.choices[0].delta.content or ""
                    _reasoning_content_msg = (
                        chunk.choices[0].delta.reasoning_content or ""
                        if hasattr(chunk.choices[0].delta, "reasoning_content")
                        else ""
                    )

                    if _reasoning_content_msg and _is_think_start is False:
                        _msg = f"<think>\n{_reasoning_content_msg}"
                        _is_think_start = True
                    elif (
                        _content_msg
                        and _is_think_start is True
                        and _is_think_end is False
                    ):
                        _msg = f"\n</think>\n\n{_content_msg}"
                        _is_think_end = True
                    elif _reasoning_content_msg and _is_think_end is False:
                        _msg = _reasoning_content_msg
                    else:
                        _msg = _content_msg

                    _full_message += _msg

                    if _msg:
                        yield _msg

            if not _full_message:  # 如果流式输出返回为空
                raise LLMError(
                    "语言模型流式输出无响应", self.base_url, self.model, messages
                )

        except (LengthLimitExceededError, MaxTokenExceededError) as e:
            raise e

        except Exception as e:
            raise LLMError(str(e), self.base_url, self.model, messages)

    def _chat(
        self,
        messages,
        temperature: float = None,
        max_new_tokens: int = None,
        top_p: float = None,
        timeout: int = 30,
        forced_reasoning: bool = False,
        **kwargs,
    ):

        _params = self._build_params(
            messages,
            temperature,
            max_new_tokens,
            top_p,
            timeout,
            forced_reasoning,
            **kwargs,
        )
        _params["stream"] = False

        try:
            response = self.client.chat.completions.create(**_params)

            if response.choices[0].finish_reason == "length":
                raise LengthLimitExceededError(
                    content=response.choices[0].message.content
                )
            elif response.choices[0].finish_reason == "max_tokens":
                raise MaxTokenExceededError(content=response.choices[0].message.content)
            else:
                _reasoning_content_msg = (
                    response.choices[0].message.reasoning_content
                    if hasattr(response.choices[0].message, "reasoning_content")
                    else ""
                )
                _content_msg = response.choices[0].message.content

                if _content_msg:
                    if _reasoning_content_msg:
                        return f"<think>\n{_reasoning_content_msg}</think>\n\n{_content_msg}"
                    return _content_msg
                else:
                    raise LLMError(
                        "语言模型无消息回复", self.base_url, self.model, messages
                    )
        except (LengthLimitExceededError, MaxTokenExceededError) as e:
            raise e

        except Exception as e:
            raise LLMError(str(e), self.base_url, self.model, messages)

    def chat_for_stream(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        timeout: int = 30,
        forced_reasoning: bool = False,
        _continue_cnt: int = 0,
        **kwargs,
    ):

        if _continue_cnt == 0 or self.is_reasoning:
            yield from self._chat_stream(
                messages,
                temperature,
                max_tokens,
                top_p,
                timeout,
                forced_reasoning,
                **kwargs,
            )
        else:

            _response_finished = False
            _full_message = ""
            _ori_messages = self._check_message(messages)
            _continue_cnt = _continue_cnt

            while 1:
                if _response_finished is True:
                    break

                if _continue_cnt < 0:
                    logging.warning(f"续写模式达到 {_continue_cnt} 次上限, 退出.")
                    break

                try:

                    if _full_message:
                        logging.info("触发LLM模型chat续写模式")
                        _messages = MessagesSet(
                            _ori_messages.message_list
                            + [AssistantMessage(_full_message)]
                            + [UserMessage("continue")]
                        )
                    else:
                        _messages = _ori_messages

                    for i in self._chat_stream(
                        _messages,
                        temperature,
                        max_tokens,
                        top_p,
                        timeout,
                        forced_reasoning,
                        **kwargs,
                    ):
                        _full_message += i
                        yield i
                    _response_finished = True
                except LengthLimitExceededError as e:
                    pass

    def chat(
        self,
        messages: str | List[dict] | List[Message] | MessagesSet,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        timeout: int = 30,
        continue_cnt: int = 0,
        forced_reasoning: bool = False,
        **kwargs,
    ):

        if continue_cnt == 0 or self.is_reasoning:
            return self._chat(
                messages,
                temperature,
                max_tokens,
                top_p,
                timeout,
                forced_reasoning,
                **kwargs,
            )

        _response_finished = False
        _full_message = ""
        _ori_messages = self._check_message(messages)
        _continue_cnt = continue_cnt

        while 1:
            if _response_finished is True:
                break

            if _continue_cnt < 0:
                logging.warning(f"续写模式达到 {continue_cnt} 次上限, 退出.")
                break

            try:
                if _full_message:
                    logging.info("触发LLM模型chat续写模式")
                    _messages = MessagesSet(
                        _ori_messages.message_list
                        + [AssistantMessage(_full_message)]
                        + [UserMessage("continue")]
                    )
                else:
                    _messages = _ori_messages
                _response_msg = self._chat(
                    _messages,
                    temperature,
                    max_tokens,
                    top_p,
                    timeout,
                    forced_reasoning,
                    **kwargs,
                )
                _full_message += _response_msg
                _response_finished = True
            except LengthLimitExceededError as e:
                _full_message += e.content
            finally:
                _continue_cnt -= 1
        return _full_message
