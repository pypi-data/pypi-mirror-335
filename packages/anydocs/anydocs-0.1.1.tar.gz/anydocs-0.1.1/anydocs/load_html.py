import typing as tp

from dataclasses import dataclass

from bs4 import BeautifulSoup, CData
from bs4.element import NavigableString
import base64c as base64  # type: ignore

from ._base import Artifact




@dataclass
class HTMLoader(Artifact):
    def extract_text(self):
        response = self.__load__().get(self.ref)
        soup = BeautifulSoup(response.text, "lxml")
        for paragraph in soup.get_text(
            separator="\n", strip=True, types=(NavigableString, CData)
        ):
            yield paragraph

    def _extract_image(self):
        if self.ref.startswith("http"):
            with self.__load__() as session:
                try:
                    response = session.get(self.ref)
                    soup = BeautifulSoup(response.text, "lxml")
                    for image in soup.find_all("img",src=True):
                        src = tp.cast(str,image.get("src")) # type: ignore
                        if src and src.startswith("data:"):
                            yield src
                        elif src and src.startswith("http"):
                            content = session.get(src).content
                            yield base64.b64encode(content).decode("utf-8")
                        else:
                            with open(self.ref, "rb") as file:
                                yield base64.b64encode(file.read()).decode("utf-8")
                except Exception as e:
                    raise e
                finally:
                    session.close()
        else:
            with open(self.ref, "rb") as file:
                yield base64.b64encode(file.read()).decode("utf-8")
