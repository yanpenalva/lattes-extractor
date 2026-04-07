import os
import xml.etree.ElementTree as ET

from app.domain.entities import Publication, Researcher, Statistic


class LattesParser:
    def __init__(self, xml_path: str):
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {xml_path}")
        self.xml_path = xml_path
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        self.lattes_id = os.path.splitext(os.path.basename(xml_path))[0]

    def parse(self) -> Researcher:
        nome = self._extract_general_data("NOME-COMPLETO") or "Unknown"

        publications = [
            *self._extract_articles(),
            *self._extract_books(),
            *self._extract_chapters(),
            *self._extract_event_papers(),
            *self._extract_technical_production(),
            *self._extract_cultural_production(),
        ]

        statistics = [
            Statistic(category="orientacoes", subcategory=sub, count=count)
            for sub, count in self._extract_orientations().items()
        ]
        event_part = self._extract_event_participation()
        statistics.append(Statistic(category="participacao_eventos",
                          subcategory="total", count=event_part["total"]))

        return Researcher(
            lattes_id=self.lattes_id,
            name=nome,
            publications=publications,
            statistics=statistics,
        )

    def _extract_general_data(self, attribute: str):
        dados_gerais = self.root.find(".//DADOS-GERAIS")
        return dados_gerais.attrib.get(attribute) if dados_gerais is not None else None

    def _extract_articles(self):
        items = []
        for item in self.root.findall(".//PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO"):
            dados = item.find("DADOS-BASICOS-DO-ARTIGO")
            if dados is not None and dados.attrib.get("NATUREZA") == "COMPLETO":
                items.append(Publication(
                    title=dados.attrib.get("TITULO-DO-ARTIGO") or "",
                    year=dados.attrib.get("ANO-DO-ARTIGO"),
                    doi=dados.attrib.get("DOI", ""),
                    nature=dados.attrib.get("NATUREZA"),
                    category="artigos_publicados",
                    metadata={"tipo": "artigo_completo"},
                ))
        return items

    def _extract_books(self):
        items = []
        for item in self.root.findall(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/LIVRO-PUBLICADO-OU-ORGANIZADO"):
            dados = item.find("DADOS-BASICOS-DO-LIVRO")
            if dados is not None:
                items.append(Publication(
                    title=dados.attrib.get("TITULO-DO-LIVRO") or "",
                    year=dados.attrib.get("ANO"),
                    nature=dados.attrib.get("NATUREZA"),
                    category="livros_publicados",
                    metadata={"tipo": "livro"},
                ))
        return items

    def _extract_chapters(self):
        items = []
        for item in self.root.findall(".//PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/CAPITULO-DE-LIVRO-PUBLICADO"):
            dados = item.find("DADOS-BASICOS-DO-CAPITULO")
            if dados is not None:
                items.append(Publication(
                    title=dados.attrib.get(
                        "TITULO-DO-CAPITULO-DO-LIVRO") or "",
                    year=dados.attrib.get("ANO"),
                    doi=dados.attrib.get("DOI", ""),
                    category="capitulos_livros",
                    metadata={"tipo": "capitulo"},
                ))
        return items

    def _extract_event_papers(self):
        items = []
        for item in self.root.findall(".//PRODUCAO-BIBLIOGRAFICA/TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTO"):
            dados = item.find("DADOS-BASICOS-DO-TRABALHO")
            if dados is not None:
                items.append(Publication(
                    title=dados.attrib.get("TITULO-DO-TRABALHO") or "",
                    year=dados.attrib.get("ANO-DO-TRABALHO"),
                    doi=dados.attrib.get("DOI", ""),
                    nature=dados.attrib.get("NATUREZA"),
                    category="trabalhos_eventos",
                    metadata={"tipo": "trabalho_evento"},
                ))
        return items

    def _extract_technical_production(self):
        items = []
        for item in self.root.findall(".//PRODUCAO-TECNICA/SOFTWARE/SOFTWARE"):
            dados = item.find("DADOS-BASICOS-DO-SOFTWARE")
            if dados is not None:
                items.append(Publication(
                    title=dados.attrib.get("TITULO-DO-SOFTWARE") or "",
                    year=dados.attrib.get("ANO"),
                    category="producao_tecnica",
                    metadata={"tipo": "Software"},
                ))

        for item in self.root.findall(".//PRODUCAO-TECNICA/PATENTE/PATENTE"):
            dados = item.find("DADOS-GERAIS-DA-PATENTE")
            if dados is not None:
                items.append(Publication(
                    title=dados.attrib.get("TITULO") or "",
                    year=dados.attrib.get("ANO-DESENVOLVIMENTO"),
                    category="producao_tecnica",
                    metadata={"tipo": "Patente"},
                ))
        return items

    def _extract_cultural_production(self):
        items = []
        base_path = ".//OUTRA-PRODUCAO/PRODUCAO-ARTISTICA-CULTURAL"

        type_map = {
            "ARTES-CENICAS": "DADOS-BASICOS-DE-ARTES-CENICAS",
            "ARTES-VISUAIS": "DADOS-BASICOS-DE-ARTES-VISUAIS",
            "MUSICA": "DADOS-BASICOS-DE-MUSICA",
        }

        for parent_tag, dados_tag in type_map.items():
            for item in self.root.findall(f"{base_path}/{parent_tag}"):
                dados = item.find(dados_tag)
                if dados is not None:
                    items.append(Publication(
                        title=dados.attrib.get("TITULO") or "",
                        year=dados.attrib.get("ANO"),
                        category="producao_cultural",
                        metadata={"tipo": parent_tag},
                    ))
        return items

    def _extract_orientations(self):
        return {
            "Doutorado": len(self.root.findall(".//OUTRA-PRODUCAO/ORIENTACOES-CONCLUIDAS/ORIENTACAO-CONCLUIDA-PARA-DOUTORADO")),
            "Mestrado": len(self.root.findall(".//OUTRA-PRODUCAO/ORIENTACOES-CONCLUIDAS/ORIENTACAO-CONCLUIDA-PARA-MESTRADO")),
            "PosDoutorado": len(self.root.findall(".//OUTRA-PRODUCAO/ORIENTACOES-CONCLUIDAS/SUPERVISOES-CONCLUIDAS/SUPERVISAO-CONCLUIDA")),
            "Outras": len(self.root.findall(".//OUTRA-PRODUCAO/ORIENTACOES-CONCLUIDAS/OUTRAS-ORIENTACOES-CONCLUIDAS/OUTRA-ORIENTACAO-CONCLUIDA")),
        }

    def _extract_event_participation(self):
        section = self.root.find(
            ".//DADOS-COMPLEMENTARES/PARTICIPACAO-EM-EVENTOS-CONGRESSOS")
        return {"total": len(list(section)) if section is not None else 0}
