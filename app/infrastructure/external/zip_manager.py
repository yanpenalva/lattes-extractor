import io
import tempfile
import zipfile


class ZipManager:
    def extract_xml(self, zip_content: bytes) -> str:
        """
        GET /researchers/raw/{lattes_id} e endpoints de summary chamam este método.
        Extrai o primeiro XML do ZIP para um arquivo temporário e retorna o caminho.
        O caller é responsável por deletar o arquivo após o uso.
        """
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
            xml_files = [f for f in zip_ref.namelist() if f.endswith(".xml")]

            if not xml_files:
                raise ValueError("No XML file found in ZIP")

            with tempfile.TemporaryDirectory() as tmp_dir:
                extracted_path = zip_ref.extract(xml_files[0], path=tmp_dir)
                with open(extracted_path, "rb") as f:
                    xml_bytes = f.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp_file:
            tmp_file.write(xml_bytes)
            return tmp_file.name
