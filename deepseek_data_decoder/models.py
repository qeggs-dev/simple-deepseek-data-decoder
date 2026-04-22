from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import datetime

class FragmentType(StrEnum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    THINK = "THINK"
    SEARCH = "SEARCH"
    READ_LINK = "READ_LINK"
    TOOL_SEARCH = "TOOL_SEARCH"
    TOOL_OPEN = "TOOL_OPEN"

class SearchResult(BaseModel):
    url: str = ""
    title: str = ""
    snippet: str = ""
    cite_index: int | None = 0
    published_at: float | None = 0.0
    site_name: str = ""
    site_icon: str = ""
    query_indexes: list[int] = Field(default_factory=list)
    is_hidden: bool = False

class Fragment(BaseModel):
    type: FragmentType = FragmentType.REQUEST
    content: str = ""
    results: list[SearchResult] = Field(default_factory=list)

class File(BaseModel):
    id: str = ""
    file_name: str = ""

class Message(BaseModel):
    files: list[File] = Field(default_factory=list)
    model: str = ""
    inserted_at: str = ""
    def inserted_time(self):
        return datetime.fromisoformat(self.inserted_at)
    fragments: list[Fragment] = Field(default_factory=list)

class Nodes(BaseModel):
    id: str = ""
    parent: str | None = None
    children: list[str] = Field(default_factory=list)
    message: Message | None = None

class Session(BaseModel):
    id: str = ""
    title: str = ""
    inserted_at: str = ""
    def inserted_time(self) -> datetime:
        return datetime.fromisoformat(self.inserted_at)
    updated_at: str = ""
    def updated_time(self) -> datetime:
        return datetime.fromisoformat(self.updated_at)
    mapping: dict[str, Nodes] = Field(default_factory=dict)