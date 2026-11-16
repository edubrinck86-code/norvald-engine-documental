"""Working Context: a fonte de verdade do conhecimento declarado."""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from documental_engine.context_item import CONTEXT_ITEM_TYPES, ContextItem
from documental_engine.context_relation import ContextRelation
from documental_engine.graph import WorkingContextGraph


@dataclass
class WorkingContext:
    """Conhecimento declarado e validado, com as relações entre os itens.

    Regra: execução é efêmera; conhecimento declarado é persistente.
    Resultado de ferramenta, raciocínio intermediário e documento completo
    nunca entram no grafo sem uma declaração explícita, validada pela
    engine.
    """

    question: str = ""
    graph: WorkingContextGraph = field(default_factory=WorkingContextGraph)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def items(self) -> List[ContextItem]:
        return list(self.graph.items.values())

    @property
    def relations(self) -> List[ContextRelation]:
        return list(self.graph.relations)

    def add(self, item: ContextItem) -> ContextItem:
        self._validate_item(item)
        return self.graph.add_item(item)

    def extend(self, items: Iterable[ContextItem]) -> None:
        for item in items:
            self.add(item)

    def get(self, item_id: str) -> Optional[ContextItem]:
        return self.graph.get_item(item_id)

    def relate(
        self,
        source_id: str,
        relation_type: str,
        target_id: str,
        *,
        author_id: Optional[str] = None,
        round_number: Optional[int] = None,
    ) -> ContextRelation:
        return self.graph.relate(
            source_id, relation_type, target_id,
            author_id=author_id, round_number=round_number,
        )

    def set_status(self, item_id: str, status: str) -> bool:
        item = self.get(item_id)
        if item is None:
            return False
        item.status = status
        return True

    def by_type(self, item_type: str, active_only: bool = False) -> List[ContextItem]:
        return self.graph.by_type(item_type, active_only=active_only)

    def active_items(self) -> List[ContextItem]:
        return self.graph.active_items()

    def deliberative_items(self) -> List[ContextItem]:
        """Itens correntes, sem as lacunas já resolvidas ou substituídas."""
        return self.graph.deliberative_items()

    def gap_registry(self) -> List[Dict[str, object]]:
        """Todas as lacunas e o estado derivado de cada uma."""
        return self.graph.gap_registry()

    def open_gaps(self) -> List[ContextItem]:
        return self.graph.open_gaps()

    def contested_items(self) -> List[ContextItem]:
        return self.graph.contested_items()

    def validate_integrity(self) -> None:
        """Revalida o estado inteiro sem alterá-lo.

        Todo item é declarado em resposta a uma pergunta; um grafo com
        conhecimento e sem pergunta não teria como ser interpretado.
        """
        if self.items and not self.question.strip():
            raise ValueError("Working Context com conhecimento exige uma pergunta.")
        for item in self.items:
            self._validate_item(item)
        for relation in self.relations:
            self.graph.validate_relation(
                relation.source_id, relation.relation_type, relation.target_id
            )

    @staticmethod
    def _validate_item(item: ContextItem) -> None:
        if item.type not in CONTEXT_ITEM_TYPES:
            raise ValueError(f"Tipo não reconhecido: {item.type}")
        if not item.id.strip():
            raise ValueError("Item exige id.")
        if not item.content.strip():
            raise ValueError(f"Item {item.id} exige conteúdo não vazio.")

    def to_dict(self) -> Dict[str, Any]:
        graph = self.graph.to_dict()
        return {
            "question": self.question,
            "items": graph["items"],
            "relations": graph["relations"],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingContext":
        context = cls(
            question=data.get("question", ""),
            graph=WorkingContextGraph.from_dict(data),
            metadata=dict(data.get("metadata", {})),
        )
        context.validate_integrity()
        return context
