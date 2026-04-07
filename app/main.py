import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.db.database import Base, engine
from app.interface.api import router
from app.interface.routers.health import router as health_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


description = """
API para gerenciamento de Currículos Lattes.

## Funcionalidades
* **Importar**: Processa e armazena dados do XML Lattes.
* **Pesquisadores**: Lista e recupera perfis de pesquisadores.
"""

tags_metadata = [
    {"name": "Researchers", "description": "Gerenciamento de dados de pesquisadores."},
    {"name": "health", "description": "Verificação de saúde dos serviços externos."},
]

app = FastAPI(
    title="API de Currículos Lattes",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Lattes API está funcionando"}
