"""O contrato de declaração: como o modelo devolve conhecimento à engine.

O guia de relações é gerado a partir do próprio grafo, para nunca ensinar
ao modelo uma relação que a validação recusaria.
"""

from typing import Dict, List

from documental_engine.contribution import DECLARABLE_KNOWLEDGE_TYPES
from documental_engine.graph import _ALLOWED_RELATIONS

_TEXTS: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "truth": "O WORKING CONTEXT abaixo é a fonte de verdade: o que está nele foi declarado e validado. Responda com base no documento e no Working Context.",
        "block": "OBRIGATÓRIO: termine a resposta com o bloco abaixo, com estes delimitadores e JSON puro (sem cerca de código):",
        "types": "type é um de: {types}. Uma unidade por afirmação. Em claim, argument, inference e decision, declare confidence (alta, média ou baixa): é o peso que você atribui à afirmação, não certificação de verdade.",
        "gaps": "Se o documento não traz a resposta, declare um gap ou open_question em vez de completar com conhecimento externo. Uma lacuna declarada vale mais que uma resposta inventada.",
        "relations": "source é um local_id desta resposta; target é um local_id desta resposta ou um id já existente no Working Context (os trechos do documento aparecem como evidence). Relações permitidas:",
        "header": "WORKING CONTEXT:",
    },
    "en": {
        "truth": "The WORKING CONTEXT below is the source of truth: what is in it has been declared and validated. Answer based on the document and the Working Context.",
        "block": "MANDATORY: end your answer with the block below, with these delimiters and plain JSON (no code fence):",
        "types": "type is one of: {types}. One unit per statement. In claim, argument, inference and decision, declare confidence (high, medium or low): it is the weight you give the statement, not a certification of truth.",
        "gaps": "If the document does not contain the answer, declare a gap or open_question instead of filling it with outside knowledge. A declared gap is worth more than an invented answer.",
        "relations": "source is a local_id from this answer; target is a local_id from this answer or an id already in the Working Context (document excerpts appear as evidence). Allowed relations:",
        "header": "WORKING CONTEXT:",
    },
}

_EXAMPLE = (
    '<<CONTRIBUTION>>\n'
    '{"knowledge":[{"local_id":"k1","type":"claim","content":"...","confidence":"..."}],'
    '"relations":[{"relation_type":"supports","source":"<evidence-id>","target":"k1"}]}\n'
    '<<END_CONTRIBUTION>>'
)


def texts_for(language: str) -> Dict[str, str]:
    if language not in _TEXTS:
        raise ValueError(f"Idioma não suportado: {language!r}")
    return _TEXTS[language]


def relation_guide() -> str:
    by_relation: Dict[str, List[str]] = {}
    for source, relation, target in sorted(_ALLOWED_RELATIONS):
        by_relation.setdefault(relation, []).append(f"{source}→{target}")
    return "\n".join(f"- {relation}: {'; '.join(pairs)}" for relation, pairs in sorted(by_relation.items()))


def declaration_contract(language: str = "pt-BR") -> str:
    t = texts_for(language)
    return "\n\n".join([
        t["truth"],
        t["block"] + "\n" + _EXAMPLE,
        t["types"].format(types=", ".join(DECLARABLE_KNOWLEDGE_TYPES)),
        t["gaps"],
        t["relations"] + "\n" + relation_guide(),
    ])
