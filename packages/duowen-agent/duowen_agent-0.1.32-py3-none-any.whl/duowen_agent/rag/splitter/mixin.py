from typing import Union, List

from duowen_agent.llm import tokenizer
from duowen_agent.rag.models import Document
from .markdown import MarkdownHeaderChunker
from .recursive import RecursiveChunker
from .separator import SeparatorChunker
from .token import TokenChunker


class FastMixinChunker:

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: Union[int, float] = 80,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = (
            chunk_overlap
            if isinstance(chunk_overlap, int)
            else int(chunk_overlap * chunk_size)
        )

    def chunk(self, text: str) -> List[Document]:
        """
        1. markdown切割
        2. 换行符切割
        3. 递归切割
        4. token切割（chunk_overlap 生效）
        """
        slices = []
        data1 = MarkdownHeaderChunker(chunk_size=self.chunk_size).chunk(text)
        for _d1 in data1:
            if _d1.metadata.get("token_count") > self.chunk_size:
                data2 = SeparatorChunker(
                    chunk_size=self.chunk_size, chunk_overlap=0
                ).chunk(_d1.page_content)
                for _d2 in data2:
                    if _d2.metadata.get("token_count") > self.chunk_size:
                        data3 = RecursiveChunker(chunk_size=self.chunk_size).chunk(
                            _d2.page_content
                        )
                        for _d3 in data3:
                            if _d3.metadata.get("token_count") > self.chunk_size:
                                data4 = TokenChunker(
                                    chunk_size=self.chunk_size,
                                    chunk_overlap=self.chunk_overlap,
                                ).chunk(_d3.page_content)
                                for _d4 in data4:
                                    _d4.metadata = {**_d1.metadata, **_d4.metadata}
                                    slices.append(_d4)
                            else:
                                _d3.metadata = {**_d1.metadata, **_d3.metadata}
                                slices.append(_d3)
                    else:
                        _d2.metadata = {**_d1.metadata, **_d2.metadata}
                        slices.append(_d2)
            else:
                slices.append(_d1)

        _slices = []
        for idx, part in enumerate(slices):
            part.metadata["chunk_index"] = idx
            part.metadata["token_count"] = tokenizer.emb_len(
                part.page_content + part.metadata.get("header_str", "")
            )
            _slices.append(part)

        return _slices

    def __repr__(self) -> str:
        return (
            f"FastMixinChunker("
            f"chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
