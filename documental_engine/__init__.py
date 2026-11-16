"""Engine documental Norvald: o modelo declara o que sabe; a engine valida e organiza.

Esta é uma parte do sistema; a versão mais ampla está em teste.
"""

from documental_engine.context_item import CONTEXT_ITEM_TYPES, ContextItem
from documental_engine.context_relation import RELATION_TYPES, ContextRelation
from documental_engine.contribution import DECLARABLE_KNOWLEDGE_TYPES, Contribution
from documental_engine.document import split_markdown
from documental_engine.instructions import declaration_contract
from documental_engine.projection import project, project_json
from documental_engine.updater import WorkingContextUpdater
from documental_engine.validation import ValidatedContribution, validate_and_convert
from documental_engine.working_context import WorkingContext

__all__ = [
    "CONTEXT_ITEM_TYPES", "ContextItem", "RELATION_TYPES", "ContextRelation",
    "DECLARABLE_KNOWLEDGE_TYPES", "Contribution", "split_markdown", "declaration_contract",
    "project", "project_json", "WorkingContextUpdater", "ValidatedContribution",
    "validate_and_convert", "WorkingContext",
]

__version__ = "0.1.0"
