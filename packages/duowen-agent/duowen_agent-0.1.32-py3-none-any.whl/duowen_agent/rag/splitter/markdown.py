import re
from typing import TypedDict, List

from duowen_agent.llm import tokenizer
from duowen_agent.rag.models import Document


class MarkdownProcessor:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text
        self.code_block_pattern = re.compile(r"```.*?```", re.DOTALL)  # 匹配代码块
        self.atx_heading_pattern = re.compile(
            r"^(#{1,6})\s+(.+)$", re.MULTILINE
        )  # # 格式标题
        self.setext_heading_pattern = re.compile(
            r"^(.+)\n=+$|^(.+)\n-+$", re.MULTILINE
        )  # = 和 - 格式标题

    def _is_in_code_block(self, position):
        """检查某个位置是否在代码块中"""
        for match in self.code_block_pattern.finditer(self.markdown_text):
            if match.start() <= position < match.end():
                return True
        return False

    def _is_valid_setext_heading(self, match):
        """检查 = 和 - 格式的标题是否合法"""
        heading_text = match.group(1) or match.group(2)  # 获取标题文本
        underline_line = match.group(0).split("\n")[1]  # 获取 = 或 - 行
        # 检查 = 或 - 的长度是否至少与标题文本长度相同
        return len(underline_line) >= len(heading_text.strip())

    def convert_underline_headings(self):
        """
        将 Markdown 中的 `=` 和 `-` 格式的标题转换为 `#` 格式的标题。
        - `=` 替换为 `#`
        - `-` 替换为 `##`
        - 排除代码块中的内容。
        """

        def replace_heading(match):
            if self._is_in_code_block(match.start()):
                return match.group(0)  # 如果在代码块中，直接返回原内容
            if not self._is_valid_setext_heading(match):
                return match.group(0)  # 如果标题不合法，直接返回原内容
            heading_text = match.group(1) or match.group(2)
            if match.group(0).endswith("="):
                return f"# {heading_text.strip()}"  # 一级标题
            else:
                return f"## {heading_text.strip()}"  # 二级标题

        self.markdown_text = self.setext_heading_pattern.sub(
            replace_heading, self.markdown_text
        )
        return self.markdown_text

    def count_headings(self):
        """统计 Markdown 文档中的标题数量"""
        # 移除代码块
        text_without_code_blocks = self.code_block_pattern.sub("", self.markdown_text)

        # 查找所有匹配的标题（# 格式）
        atx_headings = [
            match.group(0)
            for match in self.atx_heading_pattern.finditer(text_without_code_blocks)
            if not self._is_in_code_block(match.start())
        ]

        # 查找所有匹配的标题（= 和 - 格式），并排除代码块中的内容
        setext_headings = [
            match.group(0)
            for match in self.setext_heading_pattern.finditer(text_without_code_blocks)
            if not self._is_in_code_block(match.start())
            and self._is_valid_setext_heading(match)
        ]

        return len(atx_headings) + len(setext_headings)

    def get_top_level_heading(self):
        """
        获取 Markdown 文档中最顶级的目录是几级标签。
        - 返回最顶级标题的级别（1 表示一级标题，2 表示二级标题，依此类推）。
        - 如果没有标题，返回 None。
        """
        # 移除代码块
        text_without_code_blocks = self.code_block_pattern.sub("", self.markdown_text)

        # 存储所有标题的级别
        heading_levels = []

        # 查找所有匹配的标题（# 格式）
        for match in self.atx_heading_pattern.finditer(text_without_code_blocks):
            if not self._is_in_code_block(match.start()):
                level = len(match.group(1))  # # 的数量
                heading_levels.append(level)

        # 查找所有匹配的标题（= 和 - 格式），并排除代码块中的内容
        for match in self.setext_heading_pattern.finditer(text_without_code_blocks):
            if not self._is_in_code_block(
                match.start()
            ) and self._is_valid_setext_heading(match):
                level = 1 if match.group(0).endswith("=") else 2  # = 为一级，- 为二级
                heading_levels.append(level)

        return min(heading_levels) if heading_levels else None


class LineType(TypedDict):
    """Line type as typed dict."""

    metadata: dict[str, str]
    content: str


class HeaderType(TypedDict):
    """Header type as typed dict."""

    level: int
    name: str
    data: str


class MarkdownHeaderChunker:
    """Splitting markdown files based on specified headers."""

    def __init__(
        self,
        return_each_line: bool = False,
        chunk_size: int = 0,  # 如果为0 则 不开启合并
    ):
        """Create a new MarkdownHeaderTextSplitter.

        Args:
            return_each_line: Return each line w/ associated headers
        """
        # Output line-by-line or aggregated into chunks w/ common headers
        self.return_each_line = return_each_line

        self.headers_to_split_on = [("#" * i, "#" * i) for i in range(1, 7)]

        self.chunk_size = chunk_size

        self._split_header_chr = chr(1) + "|" + chr(1)

    @staticmethod
    def aggregate_lines_to_chunks(lines: list[LineType]) -> list[Document]:
        """Combine lines with common metadata into chunks
        Args:
            lines: Line of text / associated header metadata
        """
        aggregated_chunks: list[LineType] = []

        for line in lines:
            if (
                aggregated_chunks
                and aggregated_chunks[-1]["metadata"] == line["metadata"]
            ):
                # If the last line in the aggregated list
                # has the same metadata as the current line,
                # append the current content to the last lines's content
                aggregated_chunks[-1]["content"] += "  \n" + line["content"]
            else:
                # Otherwise, append the current line to the aggregated list
                aggregated_chunks.append(line)

        return [
            Document(
                page_content=chunk["content"], metadata={"header": chunk["metadata"]}
            )
            for chunk in aggregated_chunks
        ]

    def chunk(self, text: str) -> list[Document]:
        """Split markdown file
        Args:
            text: Markdown file"""

        # Split the input text by newline character ("\n").

        if MarkdownProcessor(text).count_headings() > 1:
            text = MarkdownProcessor(text).convert_underline_headings()
            if not text.strip().startswith("#"):
                text = (
                    f"{MarkdownProcessor(text).get_top_level_heading()*'#'} Introduction\n\n"
                    + text
                )
        else:
            return [
                Document(
                    page_content=text,
                    metadata=dict(token_count=tokenizer.emb_len(text), chunk_index=0),
                )
            ]

        lines = text.split("\n")
        # Final output
        lines_with_metadata: list[LineType] = []
        # Content and metadata of the chunk currently being processed
        current_content: list[str] = []
        current_metadata: dict[str, str] = {}
        # Keep track of the nested header structure
        # header_stack: List[Dict[str, Union[int, str]]] = []
        header_stack: list[HeaderType] = []
        initial_metadata: dict[str, str] = {}

        for line in lines:
            stripped_line = line.strip()
            # Check each line against each of the header types (e.g., #, ##)
            for sep, name in self.headers_to_split_on:
                # Check if line starts with a header that we intend to split on
                if stripped_line.startswith(
                    sep
                ) and (  # Header with no text OR header is followed by space
                    # Both are valid conditions that sep is being used a header
                    len(stripped_line) == len(sep)
                    or stripped_line[len(sep)] == " "
                ):
                    # Ensure we are tracking the header as metadata
                    if name is not None:
                        # Get the current header level
                        current_header_level = sep.count("#")

                        # Pop out headers of lower or same level from the stack
                        while (
                            header_stack
                            and header_stack[-1]["level"] >= current_header_level
                        ):
                            # We have encountered a new header
                            # at the same or higher level
                            popped_header = header_stack.pop()
                            # Clear the metadata for the
                            # popped header in initial_metadata
                            if popped_header["name"] in initial_metadata:
                                initial_metadata.pop(popped_header["name"])

                        # Push the current header to the stack
                        header: HeaderType = {
                            "level": current_header_level,
                            "name": name,
                            "data": stripped_line[len(sep) :].strip(),
                        }
                        header_stack.append(header)
                        # Update initial_metadata with the current header
                        initial_metadata[name] = header["data"]

                    # Add the previous line to the lines_with_metadata
                    # only if current_content is not empty
                    if current_content:
                        lines_with_metadata.append(
                            {
                                "content": "\n".join(current_content),
                                "metadata": current_metadata.copy(),
                            }
                        )
                        current_content.clear()

                    break
            else:
                if stripped_line:
                    current_content.append(stripped_line)
                elif current_content:
                    lines_with_metadata.append(
                        {
                            "content": "\n".join(current_content),
                            "metadata": current_metadata.copy(),
                        }
                    )
                    current_content.clear()

            current_metadata = initial_metadata.copy()

        if current_content:
            lines_with_metadata.append(
                {"content": "\n".join(current_content), "metadata": current_metadata}
            )

        # 不是markdown文档，无法将文档进行切割，原文返回
        if len(lines_with_metadata) == 1:
            return [
                Document(
                    page_content=text,
                    metadata=dict(token_count=tokenizer.emb_len(text), chunk_index=0),
                )
            ]

        # 不是markdown文档，无法将文档进行切割，原文返回
        for i in lines_with_metadata:
            if not i["metadata"]:
                return [
                    Document(
                        page_content=text,
                        metadata=dict(
                            token_count=tokenizer.emb_len(text), chunk_index=0
                        ),
                    )
                ]

        # lines_with_metadata has each line with associated header metadata
        # aggregate these into chunks based on common metadata
        if not self.return_each_line:
            return self.merge_documents(
                self.aggregate_lines_to_chunks(lines_with_metadata)
            )
        else:
            return self.merge_documents(
                [
                    Document(
                        page_content=chunk["content"],
                        metadata={"header": chunk["metadata"]},
                    )
                    for chunk in lines_with_metadata
                ]
            )

    def get_level_with_documents(self, documents: list[Document], level: int):
        _data = {}
        for document in documents:
            if level * "#" in document.metadata["header"]:
                _merge_header = self._split_header_chr.join(
                    [
                        f"{k} {v}"
                        for k, v in document.metadata["header"].items()
                        if len(k) <= level
                    ]
                )
                if _merge_header in _data:
                    _data[_merge_header].append(document)
                else:
                    _data[_merge_header] = [document]
        return _data

    @staticmethod
    def fix_headers(item):
        # 修复每条数据的标题层级
        header_order = ["#" * i for i in range(1, 7)]
        fixed_item = {}
        current_level = 0
        for level in header_order:
            if level in item:
                fixed_item[header_order[current_level]] = item[level]
                current_level += 1
        return fixed_item

    def merge_documents(self, documents: list[Document]) -> list[Document]:

        if self.chunk_size == 0:
            return documents

        # 修复 markdown header
        for i in documents:
            i.metadata["header"] = self.fix_headers(i.metadata["header"])

        def _doc_emb_len(documents: list[Document]) -> int:
            return tokenizer.emb_len("\n\n".join([i.page_content for i in documents]))

        def _merge_documents(
            documents: list[Document],
            level=1,
        ) -> List[List[Document]]:

            if len(documents) == 1:
                return [[documents[0]]]

            _data = []
            _current_data = []
            for k, v in self.get_level_with_documents(documents, level).items():
                if _doc_emb_len(v) > self.chunk_size:
                    _data.extend(_merge_documents(v, level + 1))
                else:
                    if _doc_emb_len(_current_data + v) <= self.chunk_size:
                        _current_data.extend(v)
                    else:
                        _data.append(_current_data)
                        _current_data = v

            if _current_data:
                _data.append(_current_data)

            return _data

        _res = _merge_documents(documents)

        _content_buffer = []
        for i in _res:

            if len(i) == 1:
                _max_level = len(max([max(j.metadata["header"].keys()) for j in i]))
                _header_key = ["#" * i for i in range(1, _max_level)]
                _header = {_h: i[0].metadata["header"][_h] for _h in _header_key}
                _header[_max_level * "#"] = i[0].metadata["header"][_max_level * "#"]
                _header_str = "\n".join([f"{k} {v}" for k, v in _header.items()])

                _content = i[0].page_content
            else:
                _content = "\n\n".join(
                    [
                        " ".join(
                            [f"{_k+' '+ _v}" for _k, _v in j.metadata["header"].items()]
                        )
                        + "\n"
                        + j.page_content
                        for j in i
                    ]
                )
                # _cur_level = None
                # for j in i:
                #     _level = ' '.join([f"{_k*'#' _v}" for _k,_v in j.metadata["header"].item()])

                _header_str = ""
                _header = None

            _content_buffer.append(
                Document(
                    page_content=_content,
                    metadata=dict(
                        token_count=tokenizer.emb_len(_header_str + "\n\n" + _content),
                        header_str=_header_str,
                        header=_header,
                    ),
                )
            )

        # 添加下标
        for idx, i in enumerate(_content_buffer):
            i.metadata["chunk_index"] = idx

        return _content_buffer
