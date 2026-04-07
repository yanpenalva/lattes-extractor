import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import Publication, Researcher, ResearcherSummary, Statistic
from app.domain.repository import ResearcherRepository
from app.infrastructure.db.models import ItemModel, ResearcherModel, StatisticModel


class SqlAlchemyResearcherRepository(ResearcherRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_lattes_id(self, lattes_id: str) -> Optional[Researcher]:
        query = select(ResearcherModel).options(
            selectinload(ResearcherModel.items),
            selectinload(ResearcherModel.statistics)
        ).where(ResearcherModel.lattes_id == lattes_id)

        result = await self.db.execute(query)
        model = result.scalars().first()

        if not model:
            return None
        return self._to_entity(model)

    async def list_all(self, limit: int = 10, offset: int = 0) -> List[ResearcherSummary]:
        query = select(ResearcherModel).offset(offset).limit(limit)
        result = await self.db.execute(query)
        models = result.scalars().all()
        return [
            ResearcherSummary(
                lattes_id=m.lattes_id,
                name=m.name,
                last_updated=m.last_updated
            ) for m in models
        ]

    async def save(self, researcher: Researcher) -> Researcher:
        # 1. Upsert Researcher
        query = select(ResearcherModel).where(ResearcherModel.lattes_id == researcher.lattes_id)
        result = await self.db.execute(query)
        model = result.scalars().first()

        if model:
            model.name = researcher.name
            model.last_updated = datetime.utcnow()
            # Clear related
            await self.db.execute(delete(ItemModel).where(ItemModel.lattes_id == researcher.lattes_id))
            await self.db.execute(delete(StatisticModel).where(StatisticModel.lattes_id == researcher.lattes_id))
        else:
            model = ResearcherModel(
                lattes_id=researcher.lattes_id,
                name=researcher.name,
                last_updated=datetime.utcnow()
            )
            self.db.add(model)

        # 2. Add Items
        for item in researcher.publications:
            item_model = ItemModel(
                lattes_id=researcher.lattes_id,
                category=item.category,
                title=item.title,
                year=str(item.year),
                doi=item.doi,
                nature=item.nature,
                metadata_json=item.metadata
            )
            self.db.add(item_model)

        # 3. Add Statistics
        for stat in researcher.statistics:
            stat_model = StatisticModel(
                lattes_id=researcher.lattes_id,
                category=stat.category,
                subcategory=stat.subcategory,
                count=stat.count
            )
            self.db.add(stat_model)

        await self.db.commit()
        await self.db.refresh(model) # Might not refresh relations fully unless requested again

        # Ideally we return what we saved, but for simplicity:
        return researcher

    def _to_entity(self, model: ResearcherModel) -> Researcher:
        publications = [
            Publication(
                title=item.title,
                year=item.year,
                doi=item.doi,
                nature=item.nature,
                category=item.category,
                metadata=item.metadata_json or {}
            )
            for item in model.items
        ]

        statistics = [
            Statistic(
                category=stat.category,
                subcategory=stat.subcategory,
                count=stat.count
            )
            for stat in model.statistics
        ]

        return Researcher(
            lattes_id=model.lattes_id,
            name=model.name,
            last_updated=model.last_updated,
            publications=publications,
            statistics=statistics
        )
