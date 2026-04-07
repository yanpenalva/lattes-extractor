import tempfile
from pathlib import Path

from app.interface.deps import get_lattes_client, get_zip_manager


class FakeLattesClient:
    def get_curriculum_zip(self, lattes_id: str):
        return b"fake-zip-bytes"


class FakeZipManager:
    def __init__(self, xml_path: str):
        self._xml_path = xml_path

    def extract_xml(self, zip_content: bytes) -> str:
        return self._xml_path


def test_get_researcher_raw_xml_as_json(client_app):
    xml = '<ROOT a="1"><CHILD>ok</CHILD></ROOT>'

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "1282159496743447.xml"
        p.write_text(xml, encoding="utf-8")

        def override_get_lattes_client():
            return FakeLattesClient()

        def override_get_zip_manager():
            return FakeZipManager(str(p))

        client_app.dependency_overrides[get_lattes_client] = override_get_lattes_client
        client_app.dependency_overrides[get_zip_manager] = override_get_zip_manager

        r = client_app.get("/api/v1/researchers/raw/1282159496743447")
        assert r.status_code == 200

        body = r.json()
        assert body["lattes_id"] == "1282159496743447"
        assert body["raw"]["ROOT"]["@attributes"]["a"] == "1"
        assert body["raw"]["ROOT"]["CHILD"] == "ok"
