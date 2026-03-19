import os
import zipfile

from pathlib import Path
from .format_pkg import FormatPackage

def load_format_package(path: str | os.PathLike, encoding: str = "utf-8") -> FormatPackage:
    with zipfile.ZipFile(path, "r") as zip_file:
        format_package = FormatPackage(
            session = zip_file.read("session.md").decode(encoding),
            node = zip_file.read("node.md").decode(encoding),
            message = zip_file.read("message.md").decode(encoding),
            file = zip_file.read("file.md").decode(encoding),
            user_input = zip_file.read("user_input.md").decode(encoding),
            read_link = zip_file.read("read_link.md").decode(encoding),
            search = zip_file.read("search.md").decode(encoding),
            search_unit = zip_file.read("search_unit.md").decode(encoding),
            ai_answer = zip_file.read("ai_answer.md").decode(encoding),
            thinking = zip_file.read("thinking.md").decode(encoding),
        )
    return format_package