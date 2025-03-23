import typing as tp
import asyncio
import tempfile
import enum
from abc import ABC, abstractmethod
from pathlib import Path

import typing_extensions as tpe
from httpx import Client
from ._proxy import LazyProxy

# Standard headers for HTTP requests
HEADERS = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
	"Accept-Language": "en-US,en;q=0.9",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Connection": "keep-alive",
	"Upgrade-Insecure-Requests": "1",
}


class FileType(str, enum.Enum):
	"""Enumeration of supported file types with their extensions."""

	DOCX = ".docx"
	DOC = ".doc"
	PDF = ".pdf"
	PPTX = ".pptx"
	PPT = ".ppt"
	XLSX = ".xlsx"
	XLS = ".xls"
	TXT = ".txt"
	MD = ".md"
	HTML = ".html"
	CSS = ".css"
	JS = ".js"
	JSON = ".json"


# Type alias using the enum for better organization
FileSuffix: tpe.TypeAlias = tp.Literal[
	FileType.DOCX,
	FileType.PDF,
	FileType.PPTX,
	FileType.XLSX,
	FileType.XLS,
	FileType.DOC,
	FileType.PPT,
	FileType.TXT,
	FileType.MD,
	FileType.HTML,
	FileType.CSS,
	FileType.JS,
	FileType.JSON,
]


class _UploadFile:
	"""
	Base implementation of an uploaded file included as part of the request data.
	"""

	def __init__(
		self,
		file: tp.BinaryIO,
		*,
		size: tp.Optional[int] = None,
		filename: tp.Optional[str] = None,
		headers: tp.Optional[dict[str, str]] = None,
	) -> None:
		self.filename = filename
		self.file = file
		self.size = size
		self.headers = headers or {}

	@property
	def content_type(self) -> tp.Optional[str]:
		"""Get the content type from headers."""
		return self.headers.get("content-type")

	@property
	def _in_memory(self) -> bool:
		"""Check if the file is in memory or rolled to disk."""
		# check for SpooledTemporaryFile._rolled
		rolled_to_disk = getattr(self.file, "_rolled", True)
		return not rolled_to_disk

	async def write(self, data: bytes) -> None:
		"""Write data to the file, handling in-memory vs disk differences."""
		if self.size is not None:
			self.size += len(data)

		if self._in_memory:
			self.file.write(data)
		else:
			await asyncio.to_thread(self.file.write, data)

	async def read(self, size: int = -1) -> bytes:
		"""Read data from the file, handling in-memory vs disk differences."""
		if self._in_memory:
			return self.file.read(size)
		return await asyncio.to_thread(self.file.read, size)

	async def seek(self, offset: int) -> None:
		"""Seek to a position in the file, handling in-memory vs disk differences."""
		if self._in_memory:
			self.file.seek(offset)
		else:
			await asyncio.to_thread(self.file.seek, offset)

	async def close(self) -> None:
		"""Close the file, handling in-memory vs disk differences."""
		if self._in_memory:
			self.file.close()
		else:
			await asyncio.to_thread(self.file.close)

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__}(filename={self.filename!r}, size={self.size!r}, headers={self.headers!r})>"


class UploadFile(_UploadFile):
	"""
	A file uploaded in a request with enhanced type annotations and functionality.

	Define it as a *path operation function* (or dependency) parameter.

	If you are using a regular `def` function, you can use the `upload_file.file`
	attribute to access the raw standard Python file (blocking, not async), useful and
	needed for non-async code.
	"""

	file: tpe.Annotated[
		tp.BinaryIO,
		tpe.Doc("The standard Python file object (non-async)."),
	]
	filename: tpe.Annotated[tp.Optional[str], tpe.Doc("The original file name.")]
	size: tpe.Annotated[tp.Optional[int], tpe.Doc("The size of the file in bytes.")]
	headers: tpe.Annotated[dict[str, str], tpe.Doc("The headers of the request.")]
	content_type: tpe.Annotated[  # type: ignore
		tp.Optional[str], tpe.Doc("The content type of the request, from the headers.")
	]

	async def write(
		self,
		data: tpe.Annotated[
			bytes,
			tpe.Doc(
				"""
				The bytes to write to the file.
				"""
			),
		],
	) -> None:
		"""
		Write some bytes to the file.

		You normally wouldn't use this from a file you read in a request.

		To be awaitable, compatible with async, this is run in threadpool.
		"""
		return await super().write(data)

	async def read(
		self,
		size: tpe.Annotated[
			int,
			tpe.Doc(
				"""
				The number of bytes to read from the file.
				"""
			),
		] = -1,
	) -> bytes:
		"""
		Read some bytes from the file.

		To be awaitable, compatible with async, this is run in threadpool.
		"""
		return await super().read(size)

	async def seek(
		self,
		offset: tpe.Annotated[
			int,
			tpe.Doc(
				"""
				The position in bytes to seek to in the file.
				"""
			),
		],
	) -> None:
		"""
		Move to a position in the file.

		Any next read or write will be done from that position.

		To be awaitable, compatible with async, this is run in threadpool.
		"""
		return await super().seek(offset)

	async def close(self) -> None:
		"""
		Close the file.

		To be awaitable, compatible with async, this is run in threadpool.
		"""
		return await super().close()

	@classmethod
	def __get_validators__(
		cls: tp.Type["UploadFile"],
	) -> tp.Iterable[tp.Callable[..., tp.Any]]:
		yield cls.validate

	@classmethod
	def validate(cls: tp.Type["UploadFile"], v: tp.Any) -> tp.Any:
		if not isinstance(v, _UploadFile):
			raise ValueError(f"Expected UploadFile, received: {type(v)}")
		return v

	@classmethod
	def _validate(cls, __input_value: tp.Any, _: tp.Any) -> "UploadFile":
		if not isinstance(__input_value, _UploadFile):
			raise ValueError(f"Expected UploadFile, received: {type(__input_value)}")
		return tp.cast(UploadFile, __input_value)

	@property
	def suffix(self) -> str:
		"""
		Determine the file suffix based on filename or content type.

		Returns:
			A normalized file extension (includes the dot)

		Raises:
			ValueError: If file type cannot be determined
		"""
		if not self.filename and not self.content_type:
			raise ValueError("Cannot determine file type: no filename or content-type")

		# Check filename first if available
		if self.filename:
			# Use pathlib for robust extension extraction
			suffix = Path(self.filename).suffix.lower()
			if suffix:
				# Handle common document types
				if suffix in (".doc", ".docx"):
					return FileType.DOCX
				elif suffix == ".pdf":
					return FileType.PDF
				elif suffix in (".ppt", ".pptx"):
					return FileType.PPTX
				elif suffix in (".xls", ".xlsx"):
					return FileType.XLSX
				elif suffix in (".txt", ".md", ".html", ".css", ".js", ".json"):
					return suffix  # Return the actual suffix

		# Fall back to content type if needed
		if self.content_type:
			content_type = self.content_type.lower()
			if "presentation" in content_type:
				return FileType.PPTX
			elif "word" in content_type or "document" in content_type:
				return FileType.DOCX
			elif "pdf" in content_type:
				return FileType.PDF
			elif "spreadsheet" in content_type or "excel" in content_type:
				return FileType.XLSX
			elif "text/plain" in content_type:
				return FileType.TXT
			elif "text/html" in content_type:
				return FileType.HTML
			elif "text/css" in content_type:
				return FileType.CSS
			elif "application/javascript" in content_type:
				return FileType.JS
			elif "application/json" in content_type:
				return FileType.JSON

		# If we got here, we couldn't determine the type
		raise ValueError(
			f"Unsupported file type: filename={self.filename}, content-type={self.content_type}"
		)


class Artifact(LazyProxy[Client], ABC):
	"""
	Abstract base class for handling different types of artifacts.

	An artifact can be a URL, file path, or raw text content.
	"""

	ref: tpe.Annotated[
		str,
		tpe.Doc(
			"""
	This `ref` can represent one out of three things:

	- An HTTP URL.
	- A file path (temporary or not) within the local filesystem.
	- A text file content.
	"""
		),
	]

	def __load__(self) -> Client:
		"""Load and return an HTTP client with predefined headers."""
		return Client(headers=HEADERS)

	def retrieve(self) -> Path[str]:
		"""
		Retrieve the artifact and return a path to the local file.

		For URLs, downloads the content.
		For file paths, returns the path.
		For raw text content, creates a temporary file.

		Returns:
			Path to the file on the local filesystem
		"""
		# Handle HTTP URLs
		if self.ref.startswith(("http://", "https://")):
			with self.__load__() as session:
				content = session.get(self.ref).raise_for_status().content 
				with tempfile.NamedTemporaryFile(
					delete=False, suffix=self._detect_extension()
				) as file:
					file.write(content)
					return Path(file.name)

		# Handle file paths
		try:
			path = Path(self.ref)
			if path.exists() and path.is_file():
				return path
		except (TypeError, ValueError):
			raise ValueError
		except Exception:
		# Handle raw text content
			with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as file:
				file.write(self.ref.encode())
				return Path(file.name)
	def _detect_extension(self) -> str:
		"""
		Try to detect file extension from URL or content type.

		Returns:
			A file extension including the dot (e.g., ".pdf")
		"""
		try:
			path = Path(self.ref.split("?")[0])  # Remove query parameters
			if path.suffix:
				return path.suffix
		except (TypeError, ValueError):
			pass
		with tempfile.NamedTemporaryFile(delete=False) as f:
			f.write(self.ref.encode())
			path = Path(f.name)
			if path.suffix:
				return path.suffix
		return ".txt"

	@abstractmethod
	def extract_text(self) -> tp.Generator[str, None,None]:
		"""
		Extract text content from the artifact.

		Yields:
			Text chunks from the artifact
		"""
		raise NotImplementedError

	@abstractmethod
	def extract_images(self) -> tp.Generator[str, None,None]:
		"""
		Extract images from the artifact.

		Yields:
			Image data as bytes
		"""
		raise NotImplementedError
