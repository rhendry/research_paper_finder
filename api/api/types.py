from pydantic import BaseModel


class Paper(BaseModel):
    title: str
    summary: str
    url: str
    authors: list[str] | None = None
    publisher: str | None = None


class Search(BaseModel):
    query: str
    papers: list[Paper]


class Research(BaseModel):
    id: str
    prompt: str
    searches: list[Search]


class ResearchSnapshot(BaseModel):
    order: int
    research: Research
