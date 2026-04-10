import unicodedata
import xml.etree.ElementTree as ET
from datetime import date

_SCHOLARSHIP_KEYWORDS = ("PIBEX", "PIBID", "PET", "RESIDENCIA")

_PARTICIPATION_TAGS = [
    "PARTICIPACAO-EM-CONGRESSO",
    "PARTICIPACAO-EM-SEMINARIO",
    "PARTICIPACAO-EM-ENCONTRO",
    "PARTICIPACAO-EM-SIMPOSIO",
    "PARTICIPACAO-EM-WORKSHOP",
    "PARTICIPACAO-EM-OFICINA",
    "PARTICIPACAO-EM-EXPOSICAO",
    "PARTICIPACAO-EM-FEIRA",
    "PARTICIPACAO-EM-FESTIVAL",
    "OUTRA-PARTICIPACAO-EM-EVENTO-ARTISTICO-CULTURAL",
    "OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS",
]

_MIN_DURATION_MONTHS = 6


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").upper()


def _calc_duration_months(vinculo: ET.Element) -> int:
    current_year = date.today().year
    current_month = date.today().month
    try:
        start_year = int(vinculo.attrib.get("ANO-INICIO", 0))
        start_month = int(vinculo.attrib.get("MES-INICIO", 1) or 1)
        end_year_raw = vinculo.attrib.get("ANO-FIM", "")
        end_month_raw = vinculo.attrib.get("MES-FIM", "")
        end_year = int(end_year_raw) if end_year_raw else current_year
        end_month = int(end_month_raw) if end_month_raw else current_month
        return (end_year - start_year) * 12 + (end_month - start_month) if start_year else 0
    except (ValueError, TypeError):
        return 0


def _extract_extension(root: ET.Element) -> dict:
    scholarship_count = 0
    other_scholarships = 0
    volunteer_count = 0

    for vinculo in root.findall(".//VINCULOS"):
        link_type = _normalize(vinculo.attrib.get(
            "OUTRO-VINCULO-INFORMADO", ""))
        extra_info = _normalize(vinculo.attrib.get("OUTRAS-INFORMACOES", ""))
        functional = _normalize(vinculo.attrib.get(
            "OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO", ""))
        duration = _calc_duration_months(vinculo)

        if "BOLSISTA" in link_type:
            if duration <= _MIN_DURATION_MONTHS:
                continue
            if any(k in extra_info or k in functional for k in _SCHOLARSHIP_KEYWORDS):
                scholarship_count += 1
            else:
                other_scholarships += 1
            continue

        if "VOLUNTARI" in link_type and duration > _MIN_DURATION_MONTHS:
            volunteer_count += 1

    for ic in root.findall(".//OUTRAS-ORIENTACOES-CONCLUIDAS/DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"):
        if ic.attrib.get("NATUREZA") == "INICIACAOCIENTIFICA" and ic.attrib.get("FLAG-BOLSA") == "SIM":
            other_scholarships += 1

    return {
        "scholarship_pet_pibid_pibex_residencia": scholarship_count,
        "other_scholarships_mentoring_ic": other_scholarships,
        "volunteer_count": volunteer_count,
    }


def _extract_scientific_production(root: ET.Element) -> dict:
    def count(path: str) -> int:
        return len(root.findall(path))

    def count_by_nature(path: str, nature: str) -> int:
        return sum(
            1 for el in root.findall(path)
            if el.attrib.get("NATUREZA") == nature
        )

    return {
        "bibliographic": {
            "complete_articles": count_by_nature(
                ".//PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO/DADOS-BASICOS-DO-ARTIGO",
                "COMPLETO",
            ),
            "conference_papers": count_by_nature(
                ".//TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO",
                "COMPLETO",
            ),
            "conference_abstracts": count_by_nature(
                ".//TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO",
                "RESUMO",
            ),
            "books": count(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/LIVRO-PUBLICADO-OU-ORGANIZADO"),
            "book_chapters": count(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/CAPITULO-DE-LIVRO-PUBLICADO"),
        },
    }


def _extract_events(root: ET.Element) -> dict:
    participation = sum(
        len(root.findall(f".//PARTICIPACAO-EM-EVENTOS-CONGRESSOS/{tag}"))
        for tag in _PARTICIPATION_TAGS
    )

    coordination = len(root.findall(
        ".//PRODUCAO-TECNICA/DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/ORGANIZACAO-DE-EVENTO"
    ))

    short_courses = len(root.findall(
        ".//PRODUCAO-TECNICA/DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/CURSO-DE-CURTA-DURACAO-MINISTRADO"
    ))

    return {
        "event_participation": participation,
        "event_coordination": coordination,
        "short_courses_taught": short_courses,
    }


def extract_student_summary(root: ET.Element, lattes_id: str) -> dict:
    general_data = root.find(".//DADOS-GERAIS")
    name = general_data.attrib.get(
        "NOME-COMPLETO", "Unknown") if general_data is not None else "Unknown"

    return {
        "lattes_id": lattes_id,
        "name": name,
        "type": "student",
        "data": {
            "extension": _extract_extension(root),
            "scientific_production": _extract_scientific_production(root),
            "events": _extract_events(root),
        },
    }
