import xml.etree.ElementTree as ET
from datetime import date

_SUPERVISION_NATURE_MAP = {
    "trabalho_de_conclusao_de_curso_graduacao": "undergraduate_thesis",
    "monografia_de_conclusao_de_curso_aperfeicoamento_e_especializacao": "specialization_monograph",
    "iniciacao_cientifica": "scientific_initiation",
    "orientacao_de_outra_natureza": "other_supervision",
}


def _extract_titulation(root: ET.Element) -> dict:
    academic_formation_base_path = ".//FORMACAO-ACADEMICA-TITULACAO"

    def count_concluded_formations(formation_tag: str) -> int:
        formation_elements = root.findall(
            f"{academic_formation_base_path}/{formation_tag}")
        return sum(
            1 for formation in formation_elements
            if formation.attrib.get("STATUS-DO-CURSO") == "CONCLUIDO"
        )

    return {
        "specialization": count_concluded_formations("ESPECIALIZACAO"),
        "masters": count_concluded_formations("MESTRADO"),
        "doctorate": count_concluded_formations("DOUTORADO"),
    }


def _extract_extension(root: ET.Element, lattes_id: str) -> dict:
    current_year = date.today().year

    counters = {
        (True, True): 0,
        (True, False): 0,
        (False, True): 0,
        (False, False): 0,
    }

    for extension_project in root.findall(".//PARTICIPACAO-EM-PROJETO/PROJETO-DE-PESQUISA"):
        if extension_project.attrib.get("NATUREZA") != "EXTENSAO":
            continue

        try:
            start_year = int(extension_project.attrib.get("ANO-INICIO", 0))
            end_year_raw = extension_project.attrib.get("ANO-FIM", "")
            end_year = int(end_year_raw) if end_year_raw else current_year
            duration_years = end_year - start_year if start_year else 0
        except (ValueError, TypeError):
            duration_years = 0

        is_coordinator = False
        for project_member in extension_project.findall(".//EQUIPE-DO-PROJETO/INTEGRANTES-DO-PROJETO"):
            if project_member.attrib.get("NRO-ID-CNPQ") != lattes_id:
                continue
            is_coordinator = project_member.attrib.get(
                "FLAG-RESPONSAVEL") == "SIM"
            break

        longer_than_two_years = duration_years > 2
        counters[(is_coordinator, longer_than_two_years)] += 1

    return {
        "extension_coordinator_up_to_2_years": counters[(True, False)],
        "extension_coordinator_over_2_years": counters[(True, True)],
        "extension_collaborator_up_to_2_years": counters[(False, False)],
        "extension_collaborator_over_2_years": counters[(False, True)],
    }


def _count_technical_works(root: ET.Element) -> int:
    excluded = {"CONSULTORIA", "ASSESSORIA"}
    return sum(
        1 for el in root.findall(".//PRODUCAO-TECNICA/TRABALHO-TECNICO/DADOS-BASICOS-DO-TRABALHO-TECNICO")
        if el.attrib.get("NATUREZA") not in excluded
    )


def _extract_scientific_production(root: ET.Element) -> dict:
    def count_elements(xml_path: str) -> int:
        return len(root.findall(xml_path))

    def count_elements_by_nature(xml_path: str, nature_value: str) -> int:
        return sum(
            1 for el in root.findall(xml_path)
            if el.attrib.get("NATUREZA") == nature_value
        )

    return {
        "bibliographic": {
            "complete_articles": count_elements_by_nature(
                ".//PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO/DADOS-BASICOS-DO-ARTIGO",
                "COMPLETO",
            ),
            "conference_papers": count_elements_by_nature(
                ".//TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO",
                "COMPLETO",
            ),
            "conference_abstracts": count_elements_by_nature(
                ".//TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS/DADOS-BASICOS-DO-TRABALHO",
                "RESUMO",
            ),
            "books": count_elements(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/LIVRO-PUBLICADO-OU-ORGANIZADO"),
            "book_chapters": count_elements(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/CAPITULO-DE-LIVRO-PUBLICADO"),
        },
        "technical": {
            "presentations": count_elements(".//PRODUCAO-TECNICA/DEMAIS-TIPOS-DE-PRODUCAO-TECNICA/APRESENTACAO-DE-TRABALHO"),
            "software": count_elements(".//PRODUCAO-TECNICA/SOFTWARE"),
            "products": count_elements(".//PRODUCAO-TECNICA/PRODUTO-TECNOLOGICO"),
            "processes_techniques": count_elements(".//PRODUCAO-TECNICA/PROCESSOS-OU-TECNICAS"),
            "technical_works": _count_technical_works(root),
        },
        "patents": {
            "patents": count_elements(".//PRODUCAO-TECNICA/PATENTE"),
            "protected_cultivar": count_elements(".//PRODUCAO-TECNICA/CULTIVAR-PROTEGIDA"),
        },
        "cultural": {
            "performing_arts": count_elements(".//OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL/ARTES-CENICAS"),
            "visual_arts": count_elements(".//OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL/ARTES-VISUAIS"),
            "music": count_elements(".//OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL/MUSICA"),
        },
    }


def _extract_human_resources(root: ET.Element) -> dict:
    base = root.find("OUTRA-PRODUCAO/ORIENTACOES-CONCLUIDAS")

    if base is None:
        return {
            "doctorate_supervised": 0,
            "masters_supervised": 0,
            "postdoc_supervised": 0,
            "others": {},
        }

    other_supervisions_by_nature: dict[str, int] = {}
    for supervision in base.findall("OUTRAS-ORIENTACOES-CONCLUIDAS/DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"):
        raw = supervision.attrib.get(
            "NATUREZA", "outros").lower().replace("-", "_")
        nature = _SUPERVISION_NATURE_MAP.get(raw, raw)
        other_supervisions_by_nature[nature] = other_supervisions_by_nature.get(
            nature, 0) + 1

    return {
        "doctorate_supervised": len(base.findall("ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO")),
        "masters_supervised": len(base.findall("ORIENTACOES-CONCLUIDAS-PARA-MESTRADO")),
        "postdoc_supervised": len(base.findall("SUPERVISOES-CONCLUIDAS")),
        "others": other_supervisions_by_nature,
    }


def extract_teacher_summary(root: ET.Element, lattes_id: str) -> dict:
    general_data_element = root.find(".//DADOS-GERAIS")
    full_name = general_data_element.attrib.get(
        "NOME-COMPLETO", "Unknown") if general_data_element is not None else "Unknown"

    return {
        "lattes_id": lattes_id,
        "name": full_name,
        "type": "teacher",
        "data": {
            "titulation": _extract_titulation(root),
            "extension": _extract_extension(root, lattes_id),
            "scientific_production": _extract_scientific_production(root),
            "human_resources": _extract_human_resources(root),
        },
    }
