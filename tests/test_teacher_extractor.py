import xml.etree.ElementTree as ET

from app.infrastructure.external.teacher_extractor import extract_teacher_summary

LATTES_ID = "123"


XML = """
<CURRICULO-VITAE>
    <DADOS-GERAIS NOME-COMPLETO="João Silva" />
    <FORMACAO-ACADEMICA-TITULACAO>
        <ESPECIALIZACAO STATUS-DO-CURSO="CONCLUIDO" />
        <ESPECIALIZACAO STATUS-DO-CURSO="INCOMPLETO" />
        <MESTRADO STATUS-DO-CURSO="CONCLUIDO" />
        <DOUTORADO STATUS-DO-CURSO="CONCLUIDO" />
    </FORMACAO-ACADEMICA-TITULACAO>
    <ATUACOES-PROFISSIONAIS>
        <ATUACAO-PROFISSIONAL>
            <ATIVIDADES-DE-PARTICIPACAO-EM-PROJETO>
                <PARTICIPACAO-EM-PROJETO>
                    <PROJETO-DE-PESQUISA NATUREZA="EXTENSAO" ANO-INICIO="2020" ANO-FIM="2021">
                        <EQUIPE-DO-PROJETO>
                            <INTEGRANTES-DO-PROJETO NRO-ID-CNPQ="123" FLAG-RESPONSAVEL="SIM" />
                            <INTEGRANTES-DO-PROJETO NRO-ID-CNPQ="999" FLAG-RESPONSAVEL="NAO" />
                        </EQUIPE-DO-PROJETO>
                    </PROJETO-DE-PESQUISA>
                </PARTICIPACAO-EM-PROJETO>
                <PARTICIPACAO-EM-PROJETO>
                    <PROJETO-DE-PESQUISA NATUREZA="EXTENSAO" ANO-INICIO="2018" ANO-FIM="2021">
                        <EQUIPE-DO-PROJETO>
                            <INTEGRANTES-DO-PROJETO NRO-ID-CNPQ="123" FLAG-RESPONSAVEL="NAO" />
                        </EQUIPE-DO-PROJETO>
                    </PROJETO-DE-PESQUISA>
                </PARTICIPACAO-EM-PROJETO>
                <PARTICIPACAO-EM-PROJETO>
                    <PROJETO-DE-PESQUISA NATUREZA="PESQUISA" ANO-INICIO="2020" ANO-FIM="2021">
                        <EQUIPE-DO-PROJETO>
                            <INTEGRANTES-DO-PROJETO NRO-ID-CNPQ="123" FLAG-RESPONSAVEL="SIM" />
                        </EQUIPE-DO-PROJETO>
                    </PROJETO-DE-PESQUISA>
                </PARTICIPACAO-EM-PROJETO>
            </ATIVIDADES-DE-PARTICIPACAO-EM-PROJETO>
        </ATUACAO-PROFISSIONAL>
    </ATUACOES-PROFISSIONAIS>
    <PRODUCAO-BIBLIOGRAFICA>
        <ARTIGOS-PUBLICADOS>
            <ARTIGO-PUBLICADO>
                <DADOS-BASICOS-DO-ARTIGO NATUREZA="COMPLETO" />
            </ARTIGO-PUBLICADO>
            <ARTIGO-PUBLICADO>
                <DADOS-BASICOS-DO-ARTIGO NATUREZA="COMPLETO" />
            </ARTIGO-PUBLICADO>
            <ARTIGO-PUBLICADO>
                <DADOS-BASICOS-DO-ARTIGO NATUREZA="RESUMO" />
            </ARTIGO-PUBLICADO>
        </ARTIGOS-PUBLICADOS>
        <TRABALHOS-EM-EVENTOS>
            <TRABALHO-EM-EVENTOS>
                <DADOS-BASICOS-DO-TRABALHO NATUREZA="COMPLETO" />
            </TRABALHO-EM-EVENTOS>
            <TRABALHO-EM-EVENTOS>
                <DADOS-BASICOS-DO-TRABALHO NATUREZA="RESUMO" />
            </TRABALHO-EM-EVENTOS>
            <TRABALHO-EM-EVENTOS>
                <DADOS-BASICOS-DO-TRABALHO NATUREZA="RESUMO_EXPANDIDO" />
            </TRABALHO-EM-EVENTOS>
        </TRABALHOS-EM-EVENTOS>
        <LIVROS-E-CAPITULOS>
            <LIVROS-PUBLICADOS-OU-ORGANIZADOS>
                <LIVRO-PUBLICADO-OU-ORGANIZADO />
                <LIVRO-PUBLICADO-OU-ORGANIZADO />
            </LIVROS-PUBLICADOS-OU-ORGANIZADOS>
            <CAPITULOS-DE-LIVROS-PUBLICADOS>
                <CAPITULO-DE-LIVRO-PUBLICADO />
            </CAPITULOS-DE-LIVROS-PUBLICADOS>
        </LIVROS-E-CAPITULOS>
    </PRODUCAO-BIBLIOGRAFICA>
    <PRODUCAO-TECNICA>
        <DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
            <APRESENTACAO-DE-TRABALHO />
            <APRESENTACAO-DE-TRABALHO />
        </DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
        <SOFTWARE />
        <PRODUTO-TECNOLOGICO />
        <PROCESSOS-OU-TECNICAS />
        <TRABALHO-TECNICO>
            <DADOS-BASICOS-DO-TRABALHO-TECNICO NATUREZA="OUTRO" />
        </TRABALHO-TECNICO>
        <TRABALHO-TECNICO>
            <DADOS-BASICOS-DO-TRABALHO-TECNICO NATUREZA="CONSULTORIA" />
        </TRABALHO-TECNICO>
        <TRABALHO-TECNICO>
            <DADOS-BASICOS-DO-TRABALHO-TECNICO NATUREZA="ASSESSORIA" />
        </TRABALHO-TECNICO>
        <PATENTE />
    </PRODUCAO-TECNICA>
    <OUTRA-PRODUCAO>
        <PRODUCAO-ARTISTICA-CULTURAL>
            <ARTES-VISUAIS />
            <ARTES-VISUAIS />
            <MUSICA />
        </PRODUCAO-ARTISTICA-CULTURAL>
        <ORIENTACOES-CONCLUIDAS>
            <ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO />
            <ORIENTACOES-CONCLUIDAS-PARA-MESTRADO />
            <ORIENTACOES-CONCLUIDAS-PARA-MESTRADO />
            <SUPERVISOES-CONCLUIDAS />
            <OUTRAS-ORIENTACOES-CONCLUIDAS>
                <DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS NATUREZA="INICIACAO_CIENTIFICA" />
            </OUTRAS-ORIENTACOES-CONCLUIDAS>
            <OUTRAS-ORIENTACOES-CONCLUIDAS>
                <DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS NATUREZA="INICIACAO_CIENTIFICA" />
            </OUTRAS-ORIENTACOES-CONCLUIDAS>
            <OUTRAS-ORIENTACOES-CONCLUIDAS>
                <DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS NATUREZA="TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO" />
            </OUTRAS-ORIENTACOES-CONCLUIDAS>
        </ORIENTACOES-CONCLUIDAS>
    </OUTRA-PRODUCAO>
</CURRICULO-VITAE>
"""


def get_root() -> ET.Element:
    return ET.fromstring(XML)


def test_extract_teacher_summary_name():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    assert result["name"] == "João Silva"
    assert result["type"] == "teacher"
    assert result["lattes_id"] == LATTES_ID


def test_titulation_counts_only_concluded():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    titulation = result["data"]["titulation"]
    assert titulation["specialization"] == 1
    assert titulation["masters"] == 1
    assert titulation["doctorate"] == 1


def test_extension_filters_by_natureza_and_lattes_id():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    extension = result["data"]["extension"]
    assert extension["extension_coordinator_up_to_2_years"] == 1
    assert extension["extension_coordinator_over_2_years"] == 0
    assert extension["extension_collaborator_up_to_2_years"] == 0
    assert extension["extension_collaborator_over_2_years"] == 1


def test_scientific_production_bibliographic():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    bib = result["data"]["scientific_production"]["bibliographic"]
    assert bib["complete_articles"] == 2
    assert bib["conference_papers"] == 1
    assert bib["conference_abstracts"] == 1
    assert bib["books"] == 2
    assert bib["book_chapters"] == 1


def test_scientific_production_technical():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    tech = result["data"]["scientific_production"]["technical"]
    assert tech["presentations"] == 2
    assert tech["software"] == 1
    assert tech["products"] == 1
    assert tech["processes_techniques"] == 1
    assert tech["technical_works"] == 1


def test_scientific_production_patents():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    patents = result["data"]["scientific_production"]["patents"]
    assert patents["patents"] == 1
    assert patents["protected_cultivar"] == 0


def test_scientific_production_cultural():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    cultural = result["data"]["scientific_production"]["cultural"]
    assert cultural["performing_arts"] == 0
    assert cultural["visual_arts"] == 2
    assert cultural["music"] == 1


def test_human_resources():
    result = extract_teacher_summary(get_root(), LATTES_ID)
    hr = result["data"]["human_resources"]
    assert hr["doctorate_supervised"] == 1
    assert hr["masters_supervised"] == 2
    assert hr["postdoc_supervised"] == 1
    assert hr["others"]["scientific_initiation"] == 2
    assert hr["others"]["undergraduate_thesis"] == 1
