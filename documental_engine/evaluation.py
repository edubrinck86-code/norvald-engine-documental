"""Roda um conjunto de perguntas sobre um documento e monta o resultado.json."""

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from documental_engine import __version__
from documental_engine.document import split_markdown
from documental_engine.llm import ChatClient
from documental_engine.session import run_question


def run_evaluation(
    client: ChatClient,
    document_path: Path,
    questions_path: Path,
    *,
    language: str = "pt-BR",
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, Any]:
    text = document_path.read_text(encoding="utf-8")
    evidence = split_markdown(text, document_path.stem)
    questions: List[Dict[str, Any]] = json.loads(questions_path.read_text(encoding="utf-8"))
    results = []
    for index, entry in enumerate(questions):
        if on_progress:
            on_progress(index, len(questions))
        outcome = run_question(
            client, evidence, text, entry["question"], language=language, expected=entry.get("expected"),
        )
        outcome["answerable"] = entry.get("answerable")
        results.append(outcome)
    if on_progress:
        on_progress(len(questions), len(questions))
    return {
        "engine_version": __version__,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "model": client.model,
        "temperature": client.temperature,
        "document": document_path.name,
        "evidence": [item.to_dict() for item in evidence],
        "results": results,
    }
