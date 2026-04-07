from typing import Optional

from app.domain.entities import Researcher
from app.domain.repository import ResearcherRepository


class GetResearcherUseCase:
    def __init__(self, repository: ResearcherRepository):
        self.repository = repository

    async def execute(self, lattes_id: str) -> Optional[Researcher]:
        return await self.repository.get_by_lattes_id(lattes_id)
