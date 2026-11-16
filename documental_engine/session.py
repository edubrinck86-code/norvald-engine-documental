"""Uma sessão: documento + pergunta -> resposta declarada, validada e revista.

Fluxo de cada pergunta:
1. o documento entra no Working Context como trechos `evidence`;
2. o modelo responde e declara o que sabe (tipo, confiança, relações, lacunas);
3. a engine valida e grava só o que passou, com o motivo de cada recusa;
4. o modelo revê a própria resposta, vendo-a como itens e relações.

Para comparação, a mesma pergunta pode ser feita sem a engine (documento em
texto corrido, sem contrato de declaração).
"""

import uuid
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from documental_engine.context_item import ContextItem
from documental_engine.contribution import Contribution
from documental_engine.instructions import declaration_contract, texts_for
from documental_engine.llm import ChatClient
from documental_engine.projection import project_json
from documental_engine.updater import WorkingContextUpdater
from documental_engine.validation import validate_and_convert
from documental_engine.working_context import WorkingContext

_REVIEW = {
    "pt-BR": "Revise a sua resposta anterior, que está no Working Context como itens e relações. Mantenha o que se sustenta no documento e corrija o que não se sustenta. Termine com o bloco CONTRIBUTION.",
    "en": "Review your previous answer, which is in the Working Context as items and relations. Keep what the document supports and correct what it does not. End with the CONTRIBUTION block.",
}
_BASELINE = {
    "pt-BR": "Responda à pergunta com base no documento abaixo.\n\nDOCUMENTO:\n{document}",
    "en": "Answer the question based on the document below.\n\nDOCUMENT:\n{document}",
}


def _turn(client: ChatClient, context: WorkingContext, user: str, author: str, round_number: int, language: str) -> Dict[str, Any]:
    system = declaration_contract(language) + "\n\n" + texts_for(language)["header"] + "\n" + project_json(context)
    raw = client.complete([{"role": "system", "content": system}, {"role": "user", "content": user}])
    contribution = Contribution.parse(raw, author_id=author, round_number=round_number, contribution_id=str(uuid.uuid4()))
    validated = validate_and_convert(contribution, context)
    rejected = list(validated.rejected)
    WorkingContextUpdater().update(context, validated.items, validated.relations, rejected)
    return {
        "prose": contribution.response,
        "declared": [item.to_dict() for item in validated.items],
        "relations": validated.relations,
        "rejected": [asdict(part) for part in rejected],
        "block_found": bool(contribution.knowledge or contribution.relations or contribution.malformed),
    }


def run_question(
    client: ChatClient,
    evidence: List[ContextItem],
    document_text: str,
    question: str,
    *,
    language: str = "pt-BR",
    review: bool = True,
    baseline: bool = True,
    expected: Optional[str] = None,
) -> Dict[str, Any]:
    context = WorkingContext(question=question)
    for item in evidence:
        context.add(ContextItem.from_dict(item.to_dict()))
    author = client.model
    result: Dict[str, Any] = {"question": question, "expected": expected, "model": client.model}
    result["answer"] = _turn(client, context, question, author, 1, language)
    if review:
        result["review"] = _turn(client, context, _REVIEW[language], author, 2, language)
    if baseline:
        result["baseline"] = client.complete([
            {"role": "system", "content": _BASELINE[language].format(document=document_text)},
            {"role": "user", "content": question},
        ])
    result["gaps"] = context.gap_registry()
    result["open_questions"] = [item.to_dict() for item in context.by_type("open_question", active_only=True)]
    result["working_context"] = context.to_dict()
    return result
