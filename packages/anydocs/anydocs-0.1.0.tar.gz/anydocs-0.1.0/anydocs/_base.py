import typing as tp
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio

import typing_extensions as tpe

MimeType: tpe.TypeAlias = tp.Literal[
    "text/x-c",
    "text/x-c++",
    "text/x-csharp",
    "text/css",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/x-golang",
    "text/html",
    "text/x-java",
    "text/javascript",
    "application/json",
    "text/markdown",
    "application/pdf",
    "text/x-php",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/x-python",
    "text/x-script.python",
    "text/x-ruby",
    "application/x-sh",
    "text/x-tex",
    "application/typescript",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

FileSuffix: tpe.TypeAlias = tp.Literal[
    ".docx",
    ".pdf",
    ".pptx",
    ".xlsx",
    ".xls",
    ".doc",
    ".ppt",
    ".pptx",
    ".txt",
    ".md",
    ".html",
    ".css",
    ".js",
    ".json",
]



class UploadFile:
    """
    An uploaded file included as part of the request data.
    """

    def __init__(
        self,
        file: tp.BinaryIO,
        *,
        size: int | None = None,
        filename: str | None = None,
        headers: dict[str,str] | None = None,
    ) -> None:
        self.filename = filename
        self.file = file
        self.size = size
        self.headers = headers or {}

    @property
    def content_type(self) -> str | None:
        return self.headers.get("content-type", None)

    @property
    def _in_memory(self) -> bool:
        # check for SpooledTemporaryFile._rolled
        rolled_to_disk = getattr(self.file, "_rolled", True)
        return not rolled_to_disk

    async def write(self, data: bytes) -> None:
        if self.size is not None:
            self.size += len(data)

        if self._in_memory:
            self.file.write(data)
        else:
            await asyncio.to_thread(self.file.write, data)

    async def read(self, size: int = -1) -> bytes:
        if self._in_memory:
            return self.file.read(size)
        return await asyncio.to_thread(self.file.read, size)

    async def seek(self, offset: int) -> None:
        if self._in_memory:
            self.file.seek(offset)
        else:
            await asyncio.to_thread(self.file.seek, offset)

    async def close(self) -> None:
        if self._in_memory:
            self.file.close()
        else:
            await asyncio.to_thread(self.file.close)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r}, size={self.size!r}, headers={self.headers!r})"


def check_suffix(
    file: UploadFile,
) -> FileSuffix:
    if not file.filename and not file.content_type:
        raise ValueError("Invalid file")

    if file.filename:
        if "docx" in file.filename:
            return ".docx"
        if "doc" in file.filename:
            return ".docx"
        if "pdf" in file.filename:
            return ".pdf"
        if "ppt" in file.filename:
            return ".pptx"
        if "pptx" in file.filename:
            return ".pptx"
        if "xlsx" in file.filename:
            return ".xlsx"
        if "xls" in file.filename:
            return ".xlsx"
    if file.content_type:
        if "presentation" in file.content_type:
            return ".pptx"
        if "document" in file.content_type:
            return ".docx"
        if "pdf" in file.content_type:
            return ".pdf"
        if "spreadsheet" in file.content_type:
            return ".xlsx"
    raise ValueError("Invalid file")


@dataclass
class Artifact(ABC):
    file_path: str

    @abstractmethod
    def extract_text(self) -> tp.Generator[str, None, None]:
        pass

    @abstractmethod
    def extract_image(self) -> tp.Generator[str, None, None]:
        pass

