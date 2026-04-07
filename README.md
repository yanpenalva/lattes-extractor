# Lattes Extractor

REST API for downloading, processing, and exposing data from Lattes curricula, built with **FastAPI**, **PostgreSQL**, and **Docker**, following **Clean Architecture** principles.

## Features

- **Clean Architecture**: strict separation between domain, use cases, infrastructure, and interface layers.
- **FastAPI**: async API optimized for I/O-bound operations.
- **PostgreSQL**: relational persistence for imported curricula.
- **Dockerized**: consistent execution across development and production.
- **CNPq Integration**: consumes the official Lattes curriculum service via SOAP.
- **Quantitative endpoints**: consolidated summaries for teacher and student profiles.
- **Health check**: verifies availability of the CNPq external service.

> ⚠️ This API has no built-in authentication. If exposed publicly, authentication and authorization must be introduced before deployment.

---

## Requirements

- Docker and Docker Compose
- Python 3.12
- PostgreSQL
- Network access to the CNPq service from the application environment
- **Prior IP authorization from CNPq** (see [CNPq Access](#cnpq-access))

---

## CNPq Access

The CNPq Lattes SOAP service (**Extrator Lattes**) requires **prior institutional authorization**. Access is not open — the CNPq whitelist only allows requests from a pre-registered fixed IP address.

To request access: https://www.gov.br/pt-br/servicos/obter-acesso-ao-extrator-da-plataforma-lattes

The authorization process requires:
- An institutional representative registered in CNPq's Institutional Directory (DI).
- A fixed IP address from which all requests will originate.
- A completed *Formulário de Habilitação* and signed *Termo de Responsabilidade*.

**This is why the API has no built-in authentication layer.** The CNPq service itself enforces access control at the network level via IP whitelist. Since the API only reads and exposes public curriculum data — it never writes to CNPq — the IP restriction is the sole access gate.

> ⚠️ If the IP of your environment changes, access must be re-requested from CNPq.

---

## Quick Start

### 1. Configuration

Copy `.env.example` and adjust as needed.

```ini
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=lattes_db

# CNPq (optional — defaults to the official WSDL)
CNPQ_WSDL_URL=https://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl
```

### 2. Run with Docker

```bash
docker compose up --build
```

### 3. Interactive docs

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Project Structure

```text
app/
├── domain/           # Entities and contracts
├── use_cases/        # Application use cases
├── infrastructure/   # Database, external integrations, repositories
├── interface/        # Routes, dependencies, HTTP layer
└── main.py           # Entry point
```

- `domain/`: entities such as `Researcher` and `ResearcherSummary`.
- `use_cases/`: application rules — import, list, and retrieve researchers.
- `infrastructure/`: database access, Lattes client, XML parsing, utilities.
- `interface/`: route definitions and dependency injection.

---

## Endpoints

### Health

#### `GET /health`

Checks connectivity with the CNPq service.

**Response 200**

```json
{
    "status": "healthy",
    "lattes": {
        "reachable": true,
        "message": "Serviço Lattes acessível e respondendo normalmente."
    }
}
```

**Response 503**

```json
{
    "status": "degraded",
    "lattes": {
        "reachable": false,
        "message": "O serviço Lattes não respondeu em 5 segundos. O host pode estar sobrecarregado ou inacessível."
    }
}
```

---

### Researchers

#### `POST /researchers/import/{lattes_id}`

Downloads the curriculum from CNPq, processes the XML, and persists the data.

**Route parameters**

- `lattes_id`: Lattes curriculum identifier.

**Response 200**
Returns the imported researcher in the `Researcher` entity format.

**Response 400**

```json
{
    "detail": "Falha ao importar o pesquisador"
}
```

---

#### `GET /researchers/raw/{lattes_id}`

Fetches the curriculum from CNPq, extracts the XML, and returns the full content converted to JSON.

**Route parameters**

- `lattes_id`: Lattes curriculum identifier.

**Response 200**

```json
{
    "lattes_id": "1234567890123456",
    "raw": {
        "CURRICULO-VITAE": {}
    }
}
```

**Errors**

- `404`: currículo não encontrado no CNPq.
- `500`: falha ao processar o XML.
- `502`: falha ao buscar o currículo ZIP no CNPq.

---

#### `GET /researchers/summary/teacher/{lattes_id}`

Returns a quantitative summary of the curriculum for a teacher profile.

**Route parameters**

- `lattes_id`: Lattes curriculum identifier.

**Response 200**
Retorna um JSON condensado com nome, `lattes_id` e os quantitativos extraídos do currículo.

**Errors**

- `404`: currículo não encontrado no CNPq.
- `500`: falha ao processar o XML.
- `502`: falha ao buscar o currículo ZIP no CNPq.

---

#### `GET /researchers/summary/student/{lattes_id}`

Returns a quantitative summary of the curriculum for a student profile.

**Route parameters**

- `lattes_id`: Lattes curriculum identifier.

**Response 200**
Retorna um JSON condensado com nome, `lattes_id` e os quantitativos extraídos do currículo.

**Errors**

- `404`: currículo não encontrado no CNPq.
- `500`: falha ao processar o XML.
- `502`: falha ao buscar o currículo ZIP no CNPq.

---

#### `GET /researchers`

Lists researchers already persisted in the database.

**Query params**

- `limit`: number of records per page. Default: `10`.
- `offset`: pagination offset. Default: `0`.

**Response 200**
Retorna uma lista de `ResearcherSummary`.

```json
[
    {
        "lattes_id": "1234567890123456",
        "name": "Fulano de Tal"
    }
]
```

---

#### `GET /researchers/{lattes_id}`

Retrieves a persisted researcher by `lattes_id`.

**Route parameters**

- `lattes_id`: Lattes curriculum identifier.

**Response 200**
Retorna a entidade `Researcher`.

**Response 404**

```json
{
    "detail": "Pesquisador não encontrado"
}
```

---

## Processing Flow

### Import and curriculum reading

1. API receives a `lattes_id`.
2. `LattesClient` queries the CNPq SOAP service.
3. Curriculum is returned as a ZIP file.
4. `ZipManager` extracts the XML.
5. XML is parsed.
6. Content is persisted or returned as a response depending on the endpoint.

### Quantitative summaries

Summary endpoints process the XML returned directly from CNPq, extracting profile-specific quantitative data without relying on database reads.

---

## CNPq Integration

Integration is handled via a SOAP client built on `zeep`.

- Consumes the official curriculum WSDL.
- Uses a custom `requests.Session` for compatibility with the legacy endpoint.
- Disables certificate verification for compatibility with the external service.
- Applies SSL adjustments required by the CNPq endpoint.
- Automatic retry with exponential backoff on all CNPq calls.

### Retry policy

- Up to 3 attempts.
- Exponential backoff.
- Minimum interval: 2 seconds.
- Maximum interval: 10 seconds.

---

## Local Development

### Install `uv`

```bash
pip install uv
```

### Install dependencies

```bash
uv pip install --system -e .[dev]
```

### Run application

```bash
uvicorn app.main:app --reload
```

> ⚠️ The database may be exposed locally on port `5433` to avoid conflicts with local PostgreSQL instances on `5432`.

---

## Tests

```bash
PYTHONPATH=/app pytest -q
```

---

## Security

This API has no built-in authentication layer. Access control is enforced externally by CNPq's IP whitelist — only the registered IP can reach the SOAP service. The API is read-only by design; it never writes data to CNPq.

> ⚠️ If exposed beyond a private network, authentication and authorization must be implemented before deployment.

---

## Architecture Decisions

### Clean Architecture
Business logic remains decoupled from the web framework, database, and infrastructure details — reducing coupling and improving testability and maintainability.

### No JWT
Authentication was omitted intentionally. The CNPq service enforces access at the network level via IP whitelist, and the API is strictly read-only. Adding JWT would introduce operational complexity without proportional security gain in this access model.

### `uv` over `pip`
Adopted for faster dependency resolution and builds, with no runtime impact.

### `asyncpg` + SQLAlchemy async
The application is I/O-bound and benefits from async concurrency both in database access and API orchestration.

### Quantitative summaries from XML
Summary endpoints operate directly on XML returned by CNPq, avoiding premature over-modeling for data that is inherently consolidated.

---

## Known Limitations

- **CNPq dependency**: `servicosweb.cnpq.br` has no publicly documented SLA.
- **External instability**: outages and maintenance windows may produce `502` or `503` responses.
- **IP whitelist**: new environments require prior IP authorization from CNPq.
- **Legacy SSL**: the CNPq endpoint requires HTTP client compatibility adjustments.
- **No built-in authentication**: access control depends entirely on CNPq's IP restriction and network isolation.
