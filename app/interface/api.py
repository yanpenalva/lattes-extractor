import os
from typing import Annotated, List
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities import Researcher, ResearcherSummary
from app.infrastructure.external.lattes_client import (
    LattesClient,
    LattesIdNotFoundError,
)
from app.infrastructure.external.student_extractor import extract_student_summary
from app.infrastructure.external.teacher_extractor import extract_teacher_summary
from app.infrastructure.external.xml_to_json import element_to_dict
from app.infrastructure.external.zip_manager import ZipManager
from app.interface.deps import (
    get_import_use_case,
    get_lattes_client,
    get_list_use_case,
    get_researcher_use_case,
    get_zip_manager,
)
from app.use_cases.get_researcher import GetResearcherUseCase
from app.use_cases.import_curriculum import ImportCurriculumUseCase
from app.use_cases.list_researchers import ListResearchersUseCase

router = APIRouter()

_ERR_CNPq_FETCH = "Falha ao buscar o currículo ZIP no CNPq"
_ERR_XML_PARSE = "Falha ao processar o XML do currículo"
_ERR_IMPORT = "Falha ao importar o pesquisador"
_ERR_NOT_FOUND = "Pesquisador não encontrado"
_ERR_LATTES_NOT_FOUND = "Currículo não encontrado no CNPq para o ID informado"

_RESPONSES_XML = {
    500: {"description": _ERR_XML_PARSE},
    502: {"description": _ERR_CNPq_FETCH},
}

_RESPONSES_IMPORT = {
    400: {"description": _ERR_IMPORT},
}

_RESPONSES_NOT_FOUND = {
    404: {"description": _ERR_NOT_FOUND},
}

_RESPONSES_LATTES_NOT_FOUND = {
    404: {"description": _ERR_LATTES_NOT_FOUND},
}


def _parse_xml_from_zip(zip_bytes: bytes, zip_mgr: ZipManager) -> ET.Element:
    xml_path = zip_mgr.extract_xml(zip_bytes)
    try:
        return ET.parse(xml_path).getroot()
    except Exception as e:
        raise HTTPException(status_code=500, detail=_ERR_XML_PARSE) from e
    finally:
        if os.path.exists(xml_path):
            os.remove(xml_path)


def _fetch_zip(lattes_id: str, client: LattesClient) -> bytes:
    try:
        return client.get_curriculum_zip(lattes_id)
    except LattesIdNotFoundError:
        raise HTTPException(status_code=404, detail=_ERR_LATTES_NOT_FOUND)
    except Exception as e:
        raise HTTPException(status_code=502, detail=_ERR_CNPq_FETCH) from e


@router.post("/researchers/import/{lattes_id}", response_model=Researcher, responses=_RESPONSES_IMPORT)
async def import_researcher(
    lattes_id: str,
    use_case: Annotated[ImportCurriculumUseCase, Depends(get_import_use_case)],
):
    try:
        return await use_case.execute(lattes_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_ERR_IMPORT) from e


@router.get("/researchers/raw/{lattes_id}", responses={**_RESPONSES_XML, **_RESPONSES_LATTES_NOT_FOUND})
async def get_raw_curriculum(
    lattes_id: str,
    client: Annotated[LattesClient, Depends(get_lattes_client)],
    zip_mgr: Annotated[ZipManager, Depends(get_zip_manager)],
):
    zip_bytes = _fetch_zip(lattes_id, client)
    root = _parse_xml_from_zip(zip_bytes, zip_mgr)
    return {"lattes_id": lattes_id, "raw": element_to_dict(root)}


@router.get("/researchers/summary/teacher/{lattes_id}", responses={**_RESPONSES_XML, **_RESPONSES_LATTES_NOT_FOUND})
async def get_teacher_summary(
    lattes_id: str,
    client: Annotated[LattesClient, Depends(get_lattes_client)],
    zip_mgr: Annotated[ZipManager, Depends(get_zip_manager)],
):
    zip_bytes = _fetch_zip(lattes_id, client)
    root = _parse_xml_from_zip(zip_bytes, zip_mgr)
    return extract_teacher_summary(root, lattes_id)


@router.get("/researchers/summary/student/{lattes_id}", responses={**_RESPONSES_XML, **_RESPONSES_LATTES_NOT_FOUND})
async def get_student_summary(
    lattes_id: str,
    client: Annotated[LattesClient, Depends(get_lattes_client)],
    zip_mgr: Annotated[ZipManager, Depends(get_zip_manager)],
):
    zip_bytes = _fetch_zip(lattes_id, client)
    root = _parse_xml_from_zip(zip_bytes, zip_mgr)
    return extract_student_summary(root, lattes_id)


@router.get("/researchers", response_model=List[ResearcherSummary])
async def list_researchers(
    use_case: Annotated[ListResearchersUseCase, Depends(get_list_use_case)],
    limit: int = 10,
    offset: int = 0,
):
    return await use_case.execute(limit, offset)


@router.get("/researchers/{lattes_id}", response_model=Researcher, responses=_RESPONSES_NOT_FOUND)
async def get_researcher(
    use_case: Annotated[GetResearcherUseCase, Depends(get_researcher_use_case)],
    lattes_id: str,
):
    researcher = await use_case.execute(lattes_id)
    if not researcher:
        raise HTTPException(status_code=404, detail=_ERR_NOT_FOUND)
    return researcher
