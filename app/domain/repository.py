from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import Researcher, ResearcherSummary


class ResearcherRepository(ABC):
    @abstractmethod
    async def save(self, researcher: Researcher) -> Researcher:
        pass

    @abstractmethod
    async def get_by_lattes_id(self, lattes_id: str) -> Optional[Researcher]:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 10, offset: int = 0) -> List[ResearcherSummary]:
        pass
