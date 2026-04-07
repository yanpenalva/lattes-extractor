import os

from app.domain.repository import ResearcherRepository
from app.infrastructure.external.lattes_client import LattesClient
from app.infrastructure.external.parser import LattesParser
from app.infrastructure.external.zip_manager import ZipManager


class ImportCurriculumUseCase:
    def __init__(self, repository: ResearcherRepository, lattes_client: LattesClient, zip_manager: ZipManager):
        self.repository = repository
        self.lattes_client = lattes_client
        self.zip_manager = zip_manager

    async def execute(self, lattes_id: str):
        # 1. Fetch
        zip_content = self.lattes_client.get_curriculum_zip(lattes_id)
        if not zip_content:
            raise Exception(f"Failed to fetch curriculum for ID {lattes_id}")

        # 2. Extract
        try:
            xml_path = self.zip_manager.extract_xml(zip_content)
        except Exception as e:
            raise Exception(f"Failed to extract XML: {e}")

        try:
            # 3. Parse
            # Note: Parser needs to be instantiated with the file path
            parser = LattesParser(xml_path)
            researcher = parser.parse()

            # Ensure ID matches request (paranoia check)
            if researcher.lattes_id != lattes_id and researcher.lattes_id != os.path.splitext(os.path.basename(xml_path))[0]:
                 # Sometimes XML filename is just what we extracted
                 researcher.lattes_id = lattes_id

            # 4. Save
            saved_researcher = await self.repository.save(researcher)
            return saved_researcher

        finally:
            # Cleanup temp file
            if os.path.exists(xml_path):
                os.remove(xml_path)
            # Cleanup temp dir if ZipManager created one...
            # ZipManager logic returns path inside temp dir. os.path.dirname(xml_path) would give the dir.
            # Ideally ZipManager manages context or cleanup, but for now we just delete the file.
            pass
