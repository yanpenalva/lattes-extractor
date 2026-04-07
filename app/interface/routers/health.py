import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.infrastructure.external.lattes_client import LattesClient
from app.interface.deps import get_lattes_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(client: LattesClient = Depends(get_lattes_client)) -> JSONResponse:
    lattes = await asyncio.to_thread(client.probe)
    status_code = 200 if lattes["reachable"] else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if lattes["reachable"] else "degraded",
            "lattes": lattes,
        },
    )
