"""Cliente mínimo para APIs compatíveis com OpenAI (OpenRouter, OpenAI, vLLM...).

A chave é passada por parâmetro e nunca gravada em disco nem em log.
Só biblioteca padrão: nada a instalar para usar a engine.
"""

import json
import ssl
import urllib.request
from dataclasses import dataclass
from typing import List, Mapping

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def _ssl_context() -> ssl.SSLContext:
    """Usa os certificados do certifi quando instalado.

    Algumas instalações de Python (MacPorts, python.org no macOS) não
    encontram os certificados do sistema e falham com
    CERTIFICATE_VERIFY_FAILED; o certifi resolve sem desligar a verificação.
    """
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


@dataclass(frozen=True)
class ChatClient:
    api_key: str
    model: str
    base_url: str = DEFAULT_BASE_URL
    temperature: float = 0.7
    timeout: float = 180.0

    def __repr__(self) -> str:  # nunca expor a chave
        return f"ChatClient(model={self.model!r}, base_url={self.base_url!r})"

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        body = json.dumps({
            "model": self.model, "messages": list(messages), "temperature": self.temperature,
        }).encode("utf-8")
        request = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions", data=body, method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout, context=_ssl_context()) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"] or ""
