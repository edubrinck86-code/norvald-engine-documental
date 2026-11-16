"""Validação de uma Contribution contra o Working Context.

Nada é reparado nem inferido: cada parte declarada entra como item ou
relação, ou sai como recusa com motivo.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

from documental_engine.context_item import ContextItem
from documental_engine.context_relation import RELATION_TYPES
from documental_engine.contribution import DECLARABLE_KNOWLEDGE_TYPES, Contribution
from documental_engine.graph import WorkingContextGraph
from documental_engine.working_context import WorkingContext


@dataclass(frozen=True)
class RejectedContributionPart:
    kind: str
    identifier: str
    reason: str


@dataclass(frozen=True)
class ValidatedContribution:
    items: List[ContextItem] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    rejected: List[RejectedContributionPart] = field(default_factory=list)
    #: `local_id` declarado -> id atribuído ao item aceito. Sem este mapa
    #: não há como dizer a qual unidade declarada uma relação se refere.
    local_ids: Dict[str, str] = field(default_factory=dict)


def validate_and_convert(contribution: Contribution, context: WorkingContext) -> ValidatedContribution:
    rejected: List[RejectedContributionPart] = [
        RejectedContributionPart(
            part.kind,
            part.identifier or f"{'knowledge' if part.kind == 'knowledge' else 'relations'}[{part.index}]",
            part.reason,
        )
        for part in contribution.malformed
    ]
    items: List[ContextItem] = []
    local_to_id: Dict[str, str] = {}
    for knowledge in contribution.knowledge:
        if not knowledge.local_id:
            rejected.append(RejectedContributionPart("knowledge", "", "local_id obrigatório"))
            continue
        if knowledge.local_id in local_to_id:
            rejected.append(RejectedContributionPart("knowledge", knowledge.local_id, "local_id duplicado"))
            continue
        if knowledge.type not in DECLARABLE_KNOWLEDGE_TYPES:
            rejected.append(RejectedContributionPart("knowledge", knowledge.local_id, "tipo semântico não declarável"))
            continue
        if not knowledge.content.strip():
            rejected.append(RejectedContributionPart("knowledge", knowledge.local_id, "conteúdo vazio"))
            continue
        item_id = str(uuid.uuid4())
        local_to_id[knowledge.local_id] = item_id
        metadata = dict(knowledge.metadata)
        metadata.setdefault("contribution_id", contribution.id)
        metadata.setdefault("provenance", [contribution.id])
        # `source_id` identifica a origem e impede que afirmações idênticas
        # de autores diferentes sejam fundidas numa só: isso apagaria o
        # sinal de concordância justo onde ele é maior.
        items.append(ContextItem(
            id=item_id, type=knowledge.type, content=knowledge.content,
            source_type="model", source_id=contribution.author_id,
            author_id=contribution.author_id, round_number=contribution.round_number,
            confidence=knowledge.confidence, metadata=metadata,
        ))
    item_types = {item.id: item.type for item in context.items}
    item_types.update({item.id: item.type for item in items})
    validated_relations: List[Dict[str, Any]] = []
    for relation in contribution.relations:
        if relation.relation_type not in RELATION_TYPES:
            rejected.append(RejectedContributionPart("relation", relation.id, "relação semântica desconhecida"))
            continue
        source_id = local_to_id.get(relation.source, relation.source)
        target_id = local_to_id.get(relation.target, relation.target)
        if source_id == target_id:
            rejected.append(RejectedContributionPart("relation", relation.id, "relação reflexiva não permitida"))
            continue
        if source_id not in item_types or target_id not in item_types:
            rejected.append(RejectedContributionPart("relation", relation.id, "source ou target inexistente"))
            continue
        if not WorkingContextGraph.relation_is_allowed(item_types[source_id], relation.relation_type, item_types[target_id]):
            rejected.append(RejectedContributionPart(
                "relation", relation.id,
                f"relação incompatível: {item_types[source_id]} -{relation.relation_type}-> {item_types[target_id]}",
            ))
            continue
        validated_relations.append({
            "source_id": source_id, "relation_type": relation.relation_type, "target_id": target_id,
            "author_id": contribution.author_id, "round_number": contribution.round_number,
        })
    return ValidatedContribution(items=items, relations=validated_relations, rejected=rejected, local_ids=dict(local_to_id))
