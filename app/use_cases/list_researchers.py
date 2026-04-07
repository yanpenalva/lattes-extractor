from typing import List

from app.domain.entities import Researcher, ResearcherSummary
from app.domain.repository import ResearcherRepository


class ListResearchersUseCase:
    def __init__(self, repository: ResearcherRepository):
        self.repository = repository

    async def execute(self, limit: int = 10, offset: int = 0) -> List[ResearcherSummary]:
        return await self.repository.list_all(limit, offset)
