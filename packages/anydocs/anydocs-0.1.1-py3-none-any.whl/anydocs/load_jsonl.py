from dataclasses import dataclass

from ._base import Artifact


@dataclass
class JsonLoader(Artifact):
    def extract_text(self):
        with open(self.ref, "r") as f:
            for line in f.readlines():
                yield line

    def extract_image(self):
        for line in self.ref.splitlines():
            if isinstance(line, bytes):
                yield line
