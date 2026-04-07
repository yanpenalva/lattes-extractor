import ssl

import requests
import urllib3
import zeep
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from zeep.transports import Transport

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LattesIdNotFoundError(Exception):
    pass


class LattesClient:
    def __init__(self, wsdl_url: str = "https://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl"):
        self.wsdl_url = wsdl_url
        self._client: zeep.Client | None = None

    @property
    def client(self) -> zeep.Client:
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.verify = False

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            ctx.options |= 0x4
        except AttributeError:
            pass

        if hasattr(ctx, "set_ciphers"):
            try:
                ctx.set_ciphers("DEFAULT@SECLEVEL=1")
            except ssl.SSLError:
                pass

        class CustomSSLAdapter(requests.adapters.HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs["ssl_context"] = ctx
                super().init_poolmanager(*args, **kwargs)

        session.mount("https://", CustomSSLAdapter())
        return session

    def _create_client(self) -> zeep.Client:
        return zeep.Client(self.wsdl_url, transport=Transport(session=self._build_session()))

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_curriculum_zip(self, lattes_id: str) -> bytes:
        result = self.client.service.getCurriculoCompactado(lattes_id)
        if not result:
            raise LattesIdNotFoundError(lattes_id)
        return result

    def probe(self) -> dict:
        try:
            session = self._build_session()
            response = session.get(self.wsdl_url, timeout=5)
            if response.status_code == 200:
                return {
                    "reachable": True,
                    "message": "Serviço Lattes acessível e respondendo normalmente.",
                }
            return {
                "reachable": False,
                "message": f"Serviço Lattes retornou HTTP {response.status_code} inesperado. Pode estar em manutenção ou com instabilidade.",
            }
        except requests.exceptions.Timeout:
            return {
                "reachable": False,
                "message": "O serviço Lattes não respondeu em 5 segundos. O host pode estar sobrecarregado ou inacessível.",
            }
        except requests.exceptions.SSLError as e:
            return {
                "reachable": False,
                "message": f"Falha no handshake SSL com o serviço Lattes: {e}",
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "reachable": False,
                "message": f"Falha ao conectar ao serviço Lattes: {e}",
            }
        except requests.exceptions.RequestException as e:
            return {
                "reachable": False,
                "message": f"Erro inesperado ao verificar o serviço Lattes: {e}",
            }
