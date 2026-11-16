"""Unidade de conhecimento do Working Context."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

#: Tipos aceitos no Working Context. `context`, `evidence` e `relation` são
#: semeados pela aplicação (documento, trecho); os demais são declarados
#: pelo modelo (ver `contribution.DECLARABLE_KNOWLEDGE_TYPES`).
CONTEXT_ITEM_TYPES = (
    "context", "evidence", "claim", "argument", "counterargument", "response",
    "inference", "option", "comparison", "criterion", "decision", "consequence",
    "condition", "open_question", "uncertainty", "gap", "reference", "relation",
)

SOURCE_TYPES = ("document", "attachment", "model")

ITEM_STATUSES = (
    "active", "superseded", "rejected", "resolved", "accepted", "unresolved",
    "contested", "unknown",
)


@dataclass
class ContextItem:
    """Uma afirmação, evidência ou lacuna, com autoria e proveniência.

    A engine não interpreta `content`: o tipo, a confiança e as relações
    são declarados por quem produziu o item. A engine só valida a forma.
    """

    id: str
    type: str
    content: str
    document_id: Optional[str] = None
    section_id: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_location: Optional[str] = None
    author_id: Optional[str] = None
    round_number: Optional[int] = None
    status: str = "active"
    confidence: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in CONTEXT_ITEM_TYPES:
            raise ValueError(f"Tipo de item inválido: {self.type}")
        if self.source_type is not None and self.source_type not in SOURCE_TYPES:
            raise ValueError(f"Tipo de origem inválido: {self.source_type}")
        if self.status not in ITEM_STATUSES:
            raise ValueError(f"Status inválido: {self.status}")
        if self.section_id is not None and self.document_id is None:
            raise ValueError("section_id exige document_id.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "type": self.type, "content": self.content,
            "document_id": self.document_id, "section_id": self.section_id,
            "source_type": self.source_type, "source_id": self.source_id,
            "source_location": self.source_location,
            "author_id": self.author_id, "round_number": self.round_number,
            "status": self.status, "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextItem":
        return cls(
            id=data["id"], type=data["type"], content=data.get("content", ""),
            document_id=data.get("document_id"), section_id=data.get("section_id"),
            source_type=data.get("source_type"), source_id=data.get("source_id"),
            source_location=data.get("source_location"),
            author_id=data.get("author_id"), round_number=data.get("round_number"),
            status=data.get("status", "active"), confidence=data.get("confidence"),
            metadata=dict(data.get("metadata", {})),
        )
