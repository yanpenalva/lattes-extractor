import unicodedata
import xml.etree.ElementTree as ET


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").upper()


def _extract_extension(root: ET.Element) -> dict:
    scholarship_count = 0
    other_scholarships = 0
    volunteer_months = 0

    for formation in root.findall(".//FORMACAO-ACADEMICA-TITULACAO/*"):
        if formation.attrib.get("FLAG-BOLSA") != "SIM":
            continue
        agency = _normalize(formation.attrib.get("NOME-AGENCIA", ""))
        try:
            start = int(formation.attrib.get("ANO-DE-INICIO", 0))
            end = int(formation.attrib.get("ANO-DE-CONCLUSAO", 0))
            duration = (end - start) * 12 if start and end else 0
        except (ValueError, TypeError):
            duration = 0

        if any(k in agency for k in ("PIBEX", "PIBID", "PET", "RESIDENCIA")):
            if duration > 6:
                scholarship_count += 1
        else:
            other_scholarships += 1

    for vinculo in root.findall(".//VINCULOS"):
        outro_vinculo = _normalize(
            vinculo.attrib.get("OUTRO-VINCULO-INFORMADO", ""))
        outras_info = _normalize(vinculo.attrib.get("OUTRAS-INFORMACOES", ""))

        if "BOLSISTA" in outro_vinculo and any(k in outras_info for k in ("PIBEX", "PIBID", "PET", "RESIDENCIA")):
            try:
                start = int(vinculo.attrib.get("ANO-INICIO", 0))
                start_m = int(vinculo.attrib.get("MES-INICIO", 1) or 1)
                end = int(vinculo.attrib.get("ANO-FIM", 0))
                end_m = int(vinculo.attrib.get("MES-FIM", 12) or 12)
                duration = (end - start) * 12 + \
                    (end_m - start_m) if start and end else 0
            except (ValueError, TypeError):
                duration = 0
            if duration > 6:
                scholarship_count += 1
            continue

        if "VOLUNTARI" in outro_vinculo:
            try:
                start = int(vinculo.attrib.get("ANO-INICIO", 0))
                start_m = int(vinculo.attrib.get("MES-INICIO", 1) or 1)
                end = int(vinculo.attrib.get("ANO-FIM", 0))
                end_m = int(vinculo.attrib.get("MES-FIM", 12) or 12)
                if start and end:
                    volunteer_months += (end - start) * 12 + (end_m - start_m)
            except (ValueError, TypeError):
                pass

    for ic in root.findall(".//OUTRAS-ORIENTACOES-CONCLUIDAS/DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"):
        if ic.attrib.get("NATUREZA") == "INICIACAOCIENTIFICA" and ic.attrib.get("FLAG-BOLSA") == "SIM":
            other_scholarships += 1

    return {
        "scholarship_pet_pibid_pibex_residencia": scholarship_count,
        "other_scholarships_mentoring_ic": other_scholarships,
        "volunteer_months": volunteer_months,
    }


def _extract_scientific_production(root: ET.Element) -> dict:
    def count(path: str) -> int:
        return len(root.findall(path))

    def count_by_nature(path: str, nature: str, negate: bool = False) -> int:
        elements = root.findall(path)
        if negate:
            return sum(1 for el in elements if el.attrib.get("NATUREZA") != nature)
        return sum(1 for el in elements if el.attrib.get("NATUREZA") == nature)

    return {
        "bibliographic": {
            "complete_articles": count_by_nature(
                ".//PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO/DADOS-BASICOS-DO-ARTIGO",
                "COMPLETO",
            ),
            "conference_papers": count_by_nature(
                ".//PRODUCAO-BIBLIOGRAFICA/TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTO/DADOS-BASICOS-DO-TRABALHO",
                "RESUMO",
                negate=True,
            ),
            "conference_abstracts": count_by_nature(
                ".//PRODUCAO-BIBLIOGRAFICA/TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTO/DADOS-BASICOS-DO-TRABALHO",
                "RESUMO",
            ),
            "books": count(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/LIVRO-PUBLICADO-OU-ORGANIZADO"),
            "book_chapters": count(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/CAPITULO-DE-LIVRO-PUBLICADO"),
        },
    }


def _extract_events(root: ET.Element) -> dict:
    participation_tags = [
        "PARTICIPACAO-EM-CONGRESSO",
        "PARTICIPACAO-EM-SEMINARIO",
        "PARTICIPACAO-EM-ENCONTRO",
        "PARTICIPACAO-EM-SIMPOSIO",
        "PARTICIPACAO-EM-WORKSHOP",
        "PARTICIPACAO-EM-OFICINA",
        "PARTICIPACAO-EM-EXPOSICAO",
        "PARTICIPACAO-EM-FESTIVAL",
        "OUTRA-PARTICIPACAO-EM-EVENTO-ARTISTICO-CULTURAL",
        "OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS",
    ]

    participation = sum(
        len(root.findall(
            f".//DADOS-COMPLEMENTARES/PARTICIPACAO-EM-EVENTOS-CONGRESSOS/{tag}"))
        for tag in participation_tags
    )

    return {
        "event_participation": participation,
        "event_coordination": len(root.findall(".//PRODUCAO-TECNICA/DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/ORGANIZACAO-DE-EVENTO")),
        "short_courses_taught": len(root.findall(".//PRODUCAO-TECNICA/DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/CURSO-DE-CURTA-DURACAO-MINISTRADO")),
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
    