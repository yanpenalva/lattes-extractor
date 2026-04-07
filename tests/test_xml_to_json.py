from xml.etree.ElementTree import fromstring

from app.infrastructure.external.xml_to_json import element_to_dict


def test_element_to_dict_simple():
    root = fromstring('<ROOT a="1"><CHILD>ok</CHILD></ROOT>')
    data = element_to_dict(root)

    assert data["ROOT"]["@attributes"]["a"] == "1"
    assert data["ROOT"]["CHILD"][0]["CHILD"] == "ok"
