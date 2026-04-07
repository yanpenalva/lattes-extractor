from __future__ import annotations

from typing import Any, Dict, List, Union
from xml.etree.ElementTree import Element

JsonValue = Union[None, bool, int, float, str,
                  List["JsonValue"], Dict[str, "JsonValue"]]


def element_to_dict(el: Element) -> Dict[str, JsonValue]:
    children = list(el)
    text = (el.text or "").strip()

    node: Dict[str, JsonValue] = {}
    if el.attrib:
        node["@attributes"] = dict(el.attrib)

    if children:
        grouped: Dict[str, List[Dict[str, JsonValue]]] = {}
        for ch in children:
            grouped.setdefault(ch.tag, []).append(element_to_dict(ch))

        for tag, items in grouped.items():
            node[tag] = items

        if text:
            node["#text"] = text

        return {el.tag: node}

    if node:
        if text:
            node["#text"] = text
        return {el.tag: node}

    return {el.tag: text if text else None}
