"""Roda o exemplo pela linha de comando e grava o resultado.json.

    export OPENROUTER_API_KEY=...   # a sua chave; nunca é gravada
    python examples/run.py --model openai/gpt-4o-mini

O resultado pode ser aberto no painel estático: dashboard/index.html?result=../resultado.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from documental_engine.evaluation import run_evaluation  # noqa: E402
from documental_engine.llm import DEFAULT_BASE_URL, ChatClient  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--document", default=str(ROOT / "examples/lgpd/documento.md"))
    parser.add_argument("--questions", default=str(ROOT / "examples/lgpd/perguntas.json"))
    parser.add_argument("--language", default="pt-BR", choices=["pt-BR", "en"])
    parser.add_argument("--output", default=str(ROOT / "resultado.json"))
    args = parser.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("Defina OPENROUTER_API_KEY (ou OPENAI_API_KEY) no ambiente.")
    client = ChatClient(api_key=key, model=args.model, base_url=args.base_url)
    result = run_evaluation(
        client, Path(args.document), Path(args.questions), language=args.language,
        on_progress=lambda done, total: print(f"{done}/{total}", file=sys.stderr),
    )
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
