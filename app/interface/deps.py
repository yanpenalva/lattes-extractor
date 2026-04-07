import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.infrastructure.external.lattes_client import LattesClient
from app.infrastructure.external.zip_manager import ZipManager
from app.infrastructure.repositories.researcher_repository import (
    SqlAlchemyResearcherRepository,
)
from app.use_cases.get_researcher import GetResearcherUseCase
from app.use_cases.import_curriculum import ImportCurriculumUseCase
from app.use_cases.list_researchers import ListResearchersUseCase


async def get_repository(db: AsyncSession = Depends(get_db)):
    return SqlAlchemyResearcherRepository(db)


def get_lattes_client():
    wsdl_url = os.getenv(
        "CNPQ_WSDL_URL",
        "https://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl",
    )
    return LattesClient(wsdl_url=wsdl_url)


def get_zip_manager():
    return ZipManager()


async def get_import_use_case(
    repo: SqlAlchemyResearcherRepository = Depends(get_repository),
    client: LattesClient = Depends(get_lattes_client),
    zip_mgr: ZipManager = Depends(get_zip_manager),
):
    return ImportCurriculumUseCase(repo, client, zip_mgr)


async def get_list_use_case(
    repo: SqlAlchemyResearcherRepository = Depends(get_repository),
):
    return ListResearchersUseCase(repo)


async def get_researcher_use_case(
    repo: SqlAlchemyResearcherRepository = Depends(get_repository),
):
    return GetResearcherUseCase(repo)
