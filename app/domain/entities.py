from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Publication(BaseModel):
    title: str
    year: str | int | None = None
    doi: Optional[str] = None
    nature: Optional[str] = None
    category: str  # articles, books, chapters, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Statistic(BaseModel):
    category: str
    subcategory: str
    count: int


class Researcher(BaseModel):
    lattes_id: str
    name: str
    last_updated: datetime = Field(default_factory=datetime.now)

    publications: List[Publication] = Field(default_factory=list)
    statistics: List[Statistic] = Field(default_factory=list)

    # Specific lists for convenience (computed or stored)
    # in domain object we might just keep them generic or separate


class ResearcherSummary(BaseModel):
    lattes_id: str
    name: str
    last_updated: datetime


class Titulation(BaseModel):
    specialization: int = 0
    masters: int = 0
    doctorate: int = 0


class TeacherSummary(BaseModel):
    lattes_id: str
    name: str
    type: str = "teacher"
    data: dict
