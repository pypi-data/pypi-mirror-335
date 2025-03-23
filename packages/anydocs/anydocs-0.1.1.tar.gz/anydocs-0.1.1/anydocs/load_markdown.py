import re
from dataclasses import dataclass

import base64c as base64  # type: ignore

from ._base import Artifact


@dataclass
class MarkdownLoader(Artifact):
    ref:str

    def extract_text(self):
        yield self.retrieve().read_text()  # retrive() return Path type

    def extract_images(self):
        content = self.retrieve().read_text()
        pattern = r"!\[.*?\]\((.*?)\)"
        for match in re.findall(pattern, content):
            yield match
