"""Leitura de um documento em trechos endereçáveis.

Cada trecho vira um item `evidence` com endereço estável (documento +
seção). O modelo cita o trecho pelo id; a engine não resume nem seleciona.
"""

import re
from typing import List

from documental_engine.context_item import ContextItem

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def split_markdown(text: str, document_id: str) -> List[ContextItem]:
    """Um trecho por título Markdown. Texto antes do primeiro título vira a seção 0."""
    text = _COMMENT.sub("", text)  # comentários HTML são nota do autor, não conteúdo
    sections: List[tuple] = []
    title, buffer = "", []
    for line in text.splitlines():
        match = _HEADING.match(line)
        if match:
            if "".join(buffer).strip():
                sections.append((title, "\n".join(buffer).strip()))
            title, buffer = match.group(2).strip(), []
        else:
            buffer.append(line)
    if "".join(buffer).strip():
        sections.append((title, "\n".join(buffer).strip()))
    items = []
    for index, (section_title, body) in enumerate(sections):
        content = f"{section_title}\n{body}" if section_title else body
        items.append(ContextItem(
            id=f"evidence-{document_id}-{index}", type="evidence", content=content,
            document_id=document_id, section_id=str(index), source_type="document",
            source_id=document_id, source_location=section_title or None,
        ))
    return items
