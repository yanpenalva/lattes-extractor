import xml.etree.ElementTree as ET

import pytest

from app.infrastructure.external.student_extractor import extract_student_summary

MOCK_XML = """<?xml version="1.0" encoding="UTF-8"?>
<CURRICULO-VITAE>
  <DADOS-GERAIS NOME-COMPLETO="Maria Teste da Silva" />

  <ATUACOES-PROFISSIONAIS>
    <ATUACAO-PROFISSIONAL>
      <VINCULOS
        OUTRO-VINCULO-INFORMADO="Voluntária"
        OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO="Voluntária do PET"
        OUTRAS-INFORMACOES=""
        ANO-INICIO="2021"
        MES-INICIO="1"
        ANO-FIM="2022"
        MES-FIM="1"
      />
      <VINCULOS
        OUTRO-VINCULO-INFORMADO="Bolsista"
        OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO="Extensionista"
        OUTRAS-INFORMACOES="Bolsista PIBEX/UEFS"
        ANO-INICIO="2023"
        MES-INICIO="3"
        ANO-FIM="2024"
        MES-FIM="3"
      />
      <VINCULOS
        OUTRO-VINCULO-INFORMADO="Bolsista"
        OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO="Bolsista PET"
        OUTRAS-INFORMACOES=""
        ANO-INICIO="2022"
        MES-INICIO="1"
        ANO-FIM="2023"
        MES-FIM="2"
      />
      <VINCULOS
        OUTRO-VINCULO-INFORMADO="Bolsista"
        OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO="Monitoria departamental"
        OUTRAS-INFORMACOES="Monitoria departamental"
        ANO-INICIO="2023"
        MES-INICIO="1"
        ANO-FIM="2023"
        MES-FIM="8"
      />
      <VINCULOS
        OUTRO-VINCULO-INFORMADO="Bolsista"
        OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO="Monitoria curta"
        OUTRAS-INFORMACOES="Monitoria curta"
        ANO-INICIO="2023"
        MES-INICIO="1"
        ANO-FIM="2023"
        MES-FIM="6"
      />
    </ATUACAO-PROFISSIONAL>
  </ATUACOES-PROFISSIONAIS>

  <PRODUCAO-BIBLIOGRAFICA>
    <ARTIGOS-PUBLICADOS>
      <ARTIGO-PUBLICADO><DADOS-BASICOS-DO-ARTIGO NATUREZA="COMPLETO" /></ARTIGO-PUBLICADO>
      <ARTIGO-PUBLICADO><DADOS-BASICOS-DO-ARTIGO NATUREZA="COMPLETO" /></ARTIGO-PUBLICADO>
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
      </LIVROS-PUBLICADOS-OU-ORGANIZADOS>
      <CAPITULOS-DE-LIVROS-PUBLICADOS>
        <CAPITULO-DE-LIVRO-PUBLICADO />
        <CAPITULO-DE-LIVRO-PUBLICADO />
      </CAPITULOS-DE-LIVROS-PUBLICADOS>
    </LIVROS-E-CAPITULOS>
  </PRODUCAO-BIBLIOGRAFICA>

  <PRODUCAO-TECNICA>
    <DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
      <ORGANIZACAO-DE-EVENTO />
      <ORGANIZACAO-DE-EVENTO />
      <CURSO-DE-CURTA-DURACAO-MINISTRADO />
    </DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
  </PRODUCAO-TECNICA>

  <DADOS-COMPLEMENTARES>
    <PARTICIPACAO-EM-EVENTOS-CONGRESSOS>
      <PARTICIPACAO-EM-CONGRESSO />
      <PARTICIPACAO-EM-CONGRESSO />
      <PARTICIPACAO-EM-SEMINARIO />
    </PARTICIPACAO-EM-EVENTOS-CONGRESSOS>
  </DADOS-COMPLEMENTARES>
</CURRICULO-VITAE>
"""


@pytest.fixture
def root():
    return ET.fromstring(MOCK_XML)


def test_name_and_type(root):
    result = extract_student_summary(root, "9999999999")
    assert result["name"] == "Maria Teste da Silva"
    assert result["type"] == "student"
    assert result["lattes_id"] == "9999999999"


def test_extension_scholarships(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["extension"]["scholarship_pet_pibid_pibex_residencia"] == 2


def test_extension_other_scholarships(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["extension"]["other_scholarships_mentoring_ic"] == 1


def test_extension_volunteer_count(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["extension"]["volunteer_count"] == 1


def test_bibliographic_complete_articles(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["scientific_production"]["bibliographic"]["complete_articles"] == 2


def test_bibliographic_conference_papers(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["scientific_production"]["bibliographic"]["conference_papers"] == 1


def test_bibliographic_conference_abstracts(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["scientific_production"]["bibliographic"]["conference_abstracts"] == 1


def test_bibliographic_books(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["scientific_production"]["bibliographic"]["books"] == 1


def test_bibliographic_book_chapters(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["scientific_production"]["bibliographic"]["book_chapters"] == 2


def test_events_participation(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["events"]["event_participation"] == 3


def test_events_coordination(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["events"]["event_coordination"] == 2


def test_events_short_courses(root):
    result = extract_student_summary(root, "9999999999")
    assert result["data"]["events"]["short_courses_taught"] == 1
