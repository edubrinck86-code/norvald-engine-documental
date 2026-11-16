"""Relação semântica entre dois itens do Working Context."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

RELATION_TYPES = (
    "documents", "supports", "addresses", "challenges", "contradicts",
    "derived_from", "evaluated_by", "compares", "selects", "produces",
    "constrains", "resolves", "answers", "supersedes", "motivates",
)


@dataclass(frozen=True)
class ContextRelation:
    """Aresta dirigida `source -relation_type-> target`.

    `author_id` e `round_number` registram quem declarou a relação e quando.
    `None` significa "não declarado", nunca "autor diferente de todos".
    """

    source_id: str
    relation_type: str
    target_id: str
    author_id: Optional[str] = None
    round_number: Optional[int] = None

    def __post_init__(self) -> None:
        if self.relation_type not in RELATION_TYPES:
            raise ValueError(f"Relação inválida: {self.relation_type}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id, "relation_type": self.relation_type,
            "target_id": self.target_id, "author_id": self.author_id,
            "round_number": self.round_number,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextRelation":
        round_number = data.get("round_number")
        return cls(
            source_id=data["source_id"], relation_type=data["relation_type"],
            target_id=data["target_id"], author_id=data.get("author_id") or None,
            round_number=int(round_number) if round_number is not None else None,
        )
