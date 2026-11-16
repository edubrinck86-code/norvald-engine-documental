"""Painel local da engine.

    pip install fastapi uvicorn
    python dashboard/server.py           # abre em http://127.0.0.1:8790
    python dashboard/server.py --port 9000

Só escuta em 127.0.0.1. A chave de API digitada no painel vive só na memória
da requisição: não é gravada em disco, em log nem no resultado.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.concurrency import run_in_threadpool  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from documental_engine.evaluation import run_evaluation  # noqa: E402
from documental_engine.llm import DEFAULT_BASE_URL, ChatClient  # noqa: E402

EXAMPLE_DOCUMENT = ROOT / "examples/lgpd/documento.md"
EXAMPLE_QUESTIONS = ROOT / "examples/lgpd/perguntas.json"

app = FastAPI(title="Engine documental Norvald", docs_url=None, redoc_url=None)


class RunRequest(BaseModel):
    api_key: str
    model: str
    base_url: str = DEFAULT_BASE_URL
    language: str = "pt-BR"

    def __repr__(self) -> str:  # nunca expor a chave
        return f"RunRequest(model={self.model!r})"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path(__file__).with_name("index.html"), headers={"Cache-Control": "no-store"})


@app.get("/api/example")
def example() -> JSONResponse:
    return JSONResponse({
        "document": EXAMPLE_DOCUMENT.read_text(encoding="utf-8"),
        "questions": EXAMPLE_QUESTIONS.read_text(encoding="utf-8"),
    })


@app.get("/api/example-result")
def example_result() -> FileResponse:
    """O resultado pronto do exemplo: /?result=/api/example-result abre sem gastar crédito."""
    return FileResponse(ROOT / "examples/lgpd/resultado-exemplo.json", media_type="application/json")


@app.post("/api/run")
async def run(request: RunRequest) -> JSONResponse:
    if not request.api_key.strip() or not request.model.strip():
        raise HTTPException(400, "Informe a chave e o modelo.")
    client = ChatClient(api_key=request.api_key.strip(), model=request.model.strip(), base_url=request.base_url)
    try:
        result = await run_in_threadpool(
            run_evaluation, client, EXAMPLE_DOCUMENT, EXAMPLE_QUESTIONS, language=request.language,
        )
    except Exception as error:  # a mensagem do provedor não contém a chave
        raise HTTPException(502, f"Falha ao chamar o modelo: {type(error).__name__}: {error}") from None
    return JSONResponse(result)


if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8790)
    uvicorn.run(app, host="127.0.0.1", port=parser.parse_args().port, log_level="warning")
