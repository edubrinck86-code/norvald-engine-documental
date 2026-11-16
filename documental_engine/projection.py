"""O que a engine entrega ao modelo: o Working Context como itens e relações.

A projeção é integral: sem seleção semântica e sem truncamento silencioso.
É o mesmo formato medido na pesquisa (texto 3, DOI 10.5281/zenodo.24265357):
o modelo vê a própria resposta anterior como itens com tipo e confiança
e as relações entre eles, e não como texto corrido.
"""

import json
from typing import Any, Dict

from documental_engine.working_context import WorkingContext


def project(context: WorkingContext) -> Dict[str, Any]:
    return {
        "question": context.question,
        "items": [item.to_dict() for item in context.active_items()],
        "relations": [relation.to_dict() for relation in context.relations],
    }


def project_json(context: WorkingContext) -> str:
    """JSON canônico: chaves ordenadas, sem espaços. O mesmo WC dá o mesmo texto."""
    return json.dumps(project(context), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
