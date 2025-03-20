from enum import Enum
from typing import Optional, Type, Any, List

import fitz
import pymupdf4llm
from codemie_tools.base.codemie_tool import CodeMieTool
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
from pymupdf import Document
from codemie_tools.pdf.tool_vars import PDF_TOOL

class QueryType(str, Enum):
    TEXT = "Text"
    TEXT_WITH_METADATA = "Text_with_Metadata"
    TOTAL_PAGES = "Total_Pages"

class PDFToolInput(BaseModel):
    """
    Defines the schema for the arguments required by PDFTool.
    """
    pages: list[int] = Field(
        description=(
            "List of page numbers of a PDF document to process. "
            "Must be empty to process all pages in a single request. "
            "Page numbers are 1-based."
        ),
    )
    query: QueryType = Field(
        ...,
        description=(
            "'Text' if the tool must return the text representation of the PDF pages. "
            "'Text_with_Metadata' if the tool must return the text representation of the "
            "PDF pages with metadata. "
            "'Total_Pages' if the tool must return the total number of pages in the PDF "
            "document."
        ),
    )


class PDFTool(CodeMieTool):
    """
    A tool for processing PDF documents, such as extracting the text from specific pages.
    """

    # The Pydantic model that describes the shape of arguments this tool takes.
    args_schema: Type[BaseModel] = PDFToolInput

    name: str = PDF_TOOL.name
    label: str = PDF_TOOL.label
    description: str = PDF_TOOL.description

    # High value to support large PDF files.
    tokens_size_limit: int = 100_000

    pdf_document: Optional[Document] = None

    # This may be used if you want to store or inject a chat model in the future.
    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)

    def __init__(self, pdf_bytes: bytes, **kwargs: Any) -> None:
        """
        Initialize the PDFTool with a PDF as bytes.

        Args:
            pdf_bytes (bytes): The raw bytes of the PDF file.
            **kwargs: Additional keyword arguments to pass along to the super class.
        """
        super().__init__(**kwargs)
        self.pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    def execute(self, pages: List[int], query: QueryType) -> str | dict[str, Any]:
        """
        Process the PDF document based on the provided query and pages.

        Args:
            pages (List[int]): A list of 1-based page numbers to process.
                               If empty, the entire document is processed.
            query (str): The query or action to perform:
                - "Total_Pages" to return the total number of pages.
                - "Text" to return the text representation of the PDF.
                - "Text_with_Metadata" to return the text along with metadata.

        Returns:
            str: A string representation of the requested data.
        """
        if not self.pdf_document:
            raise ValueError("No PDF document is loaded. Please provide a valid PDF.")

        if query == "Total_Pages":
            return str(self.pdf_document.page_count)
        elif query.lower().startswith("text"):
            # Convert 1-based page indices to 0-based for PyMuPDF.
            zero_based_pages = [p - 1 for p in pages] if pages else None

            page_chunks = (query == "Text_with_Metadata")
            markdown = pymupdf4llm.to_markdown(
                doc=self.pdf_document,
                pages=zero_based_pages,
                page_chunks=page_chunks
            )
            return markdown
        else:
            raise ValueError(
                f"Unknown query '{query}'. Expected one of "
                "['Total_Pages', 'Text', 'Text_with_Metadata']."
            )
