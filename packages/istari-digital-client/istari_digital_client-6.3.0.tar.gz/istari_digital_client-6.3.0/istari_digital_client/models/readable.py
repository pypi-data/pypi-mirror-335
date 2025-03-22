import abc
import json
import os
from pathlib import Path
from typing import TypeAlias, Union

from istari_digital_client.models.properties import PropertiesHaving


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
PathLike = Union[str, os.PathLike, Path]


class Readable(PropertiesHaving, abc.ABC):
    @abc.abstractmethod
    def read_bytes(self: "Readable") -> bytes: ...

    def read_text(self: "Readable", encoding: str = "utf-8") -> str:
        return self.read_bytes().decode(encoding)

    def copy_to(self: "Readable", dest: PathLike) -> Path:
        dest_path = Path(str(dest))
        dest_path.write_bytes(self.read_bytes())
        return dest_path

    def read_json(self: "Readable", encoding: str = "utf-8") -> JSON:
        return json.loads(self.read_text(encoding=encoding))
