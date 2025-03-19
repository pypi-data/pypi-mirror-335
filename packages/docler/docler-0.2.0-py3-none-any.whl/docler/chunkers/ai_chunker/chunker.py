"""AI-based markdown chunking implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel, ConfigDict

from docler.chunkers.base import TextChunk, TextChunker


if TYPE_CHECKING:
    from llmling_agent.agent.agent import AgentType

    from docler.models import Document


class Chunk(BaseModel):
    """A chunk of text with semantic metadata."""

    start_row: int
    """Start line number (1-based)"""

    end_row: int
    """End line number (1-based)"""

    keywords: list[str]
    """Key terms and concepts in this chunk"""

    references: list[int]
    """Line numbers that this chunk references or depends on"""

    model_config = ConfigDict(use_attribute_docstrings=True)


class Chunks(BaseModel):
    """Collection of chunks with their metadata."""

    chunks: list[Chunk]
    """A list of chunks to extract from the document."""


SYS_PROMPT = """
You are an expert at dividing text into meaningful chunks while preserving context and relationships.

Analyze this text and split it into coherent chunks. For each chunk:
1. Define its start and end line numbers (1-based)
2. Extract key terms and concepts as keywords
3. Note any line numbers it references or depends on

Rules:
- Each chunk should be semantically complete
- Identify cross-references between different parts of the text
- Keywords should be specific and relevant
- Line numbers must be accurate

"""  # noqa: E501

CHUNKING_PROMPT = """
Here's the text with line numbers:

{numbered_text}

"""


class AIChunker(TextChunker):
    """LLM-based document chunker."""

    REQUIRED_PACKAGES: ClassVar = {"llmling-agent"}

    def __init__(
        self,
        model: str = "openrouter:openai/o3-mini",  # google/gemini-2.0-flash-lite-001
        provider: AgentType = "pydantic_ai",
        min_chunk_size: int = 200,
        max_chunk_size: int = 1500,
    ):
        """Initialize the AI chunker.

        Args:
            model: LLM model to use
            provider: LLM provider to use
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
        """
        self.model = model
        self.provider = provider
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _add_line_numbers(self, text: str) -> str:
        """Add line numbers to text."""
        lines = text.splitlines()
        return "\n".join(f"{i + 1:3d} | {line}" for i, line in enumerate(lines))

    async def _get_chunks(self, text: str) -> Chunks:
        """Get chunk definitions from LLM."""
        import llmling_agent

        numbered_text = self._add_line_numbers(text)
        agent: llmling_agent.StructuredAgent[None, Chunks] = llmling_agent.Agent(
            model=self.model,
            provider=self.provider,  # pyright: ignore
            system_prompt=SYS_PROMPT,
        ).to_structured(Chunks)
        prompt = CHUNKING_PROMPT.format(numbered_text=numbered_text)
        response = await agent.run(prompt)
        return response.content

    def _create_text_chunk(
        self,
        doc: Document,
        chunk: Chunk,
        chunk_idx: int,
        extra_metadata: dict[str, Any] | None = None,
    ) -> TextChunk:
        """Create a TextChunk from chunk definition."""
        lines = doc.content.splitlines()
        chunk_lines = lines[chunk.start_row - 1 : chunk.end_row]
        chunk_text = "\n".join(chunk_lines)
        base = extra_metadata or {}
        metadata = {**base, "keywords": chunk.keywords, "references": chunk.references}
        chunk_images = [i for i in doc.images if i.filename and i.filename in chunk_text]
        return TextChunk(
            text=chunk_text,
            source_doc_id=doc.source_path or "",
            chunk_index=chunk_idx,
            images=chunk_images,
            metadata=metadata,
        )

    async def split(
        self,
        doc: Document,
        extra_metadata: dict[str, Any] | None = None,
    ) -> list[TextChunk]:
        """Split document into chunks using LLM analysis."""
        # Get chunk definitions from LLM
        chunks = await self._get_chunks(doc.content)

        # Convert to TextChunks
        return [
            self._create_text_chunk(doc, chunk, i, extra_metadata)
            for i, chunk in enumerate(chunks.chunks)
        ]


if __name__ == "__main__":
    import asyncio

    from docler.models import Document

    async def main():
        # Example usage
        doc = Document(source_path="example.txt", content=SYS_PROMPT)
        chunker = AIChunker()
        chunks = await chunker.split(doc)
        print(chunks)

    asyncio.run(main())
