"""Testes da engine. Rodam só com a biblioteca padrão: python -m unittest -v"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from documental_engine import (  # noqa: E402
    ContextItem, Contribution, WorkingContext, WorkingContextUpdater,
    declaration_contract, project_json, split_markdown, validate_and_convert,
)
from documental_engine.session import run_question  # noqa: E402


def block(knowledge, relations=(), prose="Prosa."):
    return prose + "\n<<CONTRIBUTION>>\n" + json.dumps({"knowledge": list(knowledge), "relations": list(relations)}) + "\n<<END_CONTRIBUTION>>"


def context_with_evidence():
    context = WorkingContext(question="Q?")
    context.add(ContextItem(id="evidence-doc-1", type="evidence", content="Art. 8º ...", document_id="doc", section_id="1", source_type="document"))
    return context


def apply(context, raw, author="m1", round_number=1):
    contribution = Contribution.parse(raw, author_id=author, round_number=round_number)
    validated = validate_and_convert(contribution, context)
    rejected = list(validated.rejected)
    WorkingContextUpdater().update(context, validated.items, validated.relations, rejected)
    return validated, rejected


class ParserTest(unittest.TestCase):
    def test_no_block_keeps_prose_and_declares_nothing(self):
        c = Contribution.parse("Só prosa.", author_id="m", round_number=1)
        self.assertEqual(c.response, "Só prosa.")
        self.assertEqual(c.knowledge, [])

    def test_code_fence_inside_block_is_accepted(self):
        raw = 'P.\n<<CONTRIBUTION>>\n```json\n{"knowledge":[{"local_id":"k1","type":"claim","content":"x"}],"relations":[]}\n```\n<<END_CONTRIBUTION>>'
        c = Contribution.parse(raw, author_id="m", round_number=1)
        self.assertEqual(len(c.knowledge), 1)
        self.assertEqual(c.response, "P.")

    def test_one_malformed_part_does_not_drop_the_others(self):
        raw = block([{"type": "claim", "content": "sem id"}, {"local_id": "k2", "type": "claim", "content": "ok"}])
        c = Contribution.parse(raw, author_id="m", round_number=1)
        self.assertEqual([k.local_id for k in c.knowledge], ["k2"])
        self.assertEqual(len(c.malformed), 1)

    def test_invalid_json_drops_block_but_keeps_answer(self):
        c = Contribution.parse("P.\n<<CONTRIBUTION>>\n{nope\n<<END_CONTRIBUTION>>", author_id="m", round_number=1)
        self.assertEqual(c.knowledge, [])
        self.assertIn("P.", c.response)


class ValidationTest(unittest.TestCase):
    def test_claim_supported_by_evidence_is_accepted(self):
        context = context_with_evidence()
        validated, rejected = apply(context, block(
            [{"local_id": "k1", "type": "claim", "content": "O controlador prova.", "confidence": "alta"}],
            [{"relation_type": "supports", "source": "evidence-doc-1", "target": "k1"}],
        ))
        self.assertEqual(rejected, [])
        self.assertEqual(len(context.relations), 1)
        self.assertEqual(validated.items[0].confidence, "alta")

    def test_relation_not_allowed_by_graph_is_rejected_with_reason(self):
        context = context_with_evidence()
        _, rejected = apply(context, block(
            [{"local_id": "k1", "type": "claim", "content": "x"}],
            [{"relation_type": "selects", "source": "k1", "target": "evidence-doc-1"}],
        ))
        self.assertEqual(len(rejected), 1)
        self.assertIn("incompatível", rejected[0].reason)
        self.assertEqual(len(context.by_type("claim")), 1)  # o item válido entrou

    def test_unknown_target_is_rejected(self):
        context = context_with_evidence()
        _, rejected = apply(context, block(
            [{"local_id": "k1", "type": "claim", "content": "x"}],
            [{"relation_type": "supports", "source": "evidence-inexistente", "target": "k1"}],
        ))
        self.assertEqual(rejected[0].reason, "source ou target inexistente")

    def test_non_declarable_type_is_rejected(self):
        context = context_with_evidence()
        _, rejected = apply(context, block([{"local_id": "k1", "type": "evidence", "content": "inventada"}]))
        self.assertEqual(rejected[0].reason, "tipo semântico não declarável")
        self.assertEqual(len(context.by_type("evidence")), 1)

    def test_identical_statements_from_different_authors_are_kept_apart(self):
        context = context_with_evidence()
        apply(context, block([{"local_id": "k", "type": "claim", "content": "Igual"}]), author="a")
        apply(context, block([{"local_id": "k", "type": "claim", "content": "Igual"}]), author="b")
        self.assertEqual(len(context.by_type("claim")), 2)

    def test_same_author_repeating_is_merged(self):
        context = context_with_evidence()
        apply(context, block([{"local_id": "k", "type": "claim", "content": "Igual"}]), round_number=1)
        apply(context, block([{"local_id": "k", "type": "claim", "content": "Igual", "confidence": "média"}]), round_number=2)
        claims = context.by_type("claim")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].confidence, "média")


class GapLifecycleTest(unittest.TestCase):
    def test_gap_is_open_until_resolved(self):
        context = context_with_evidence()
        validated, _ = apply(context, block([{"local_id": "g", "type": "gap", "content": "O trecho não traz o prazo."}]))
        gap_id = validated.local_ids["g"]
        self.assertEqual(context.gap_registry()[0]["state"], "open")
        apply(context, block(
            [{"local_id": "c", "type": "claim", "content": "O prazo é X."}],
            [{"relation_type": "resolves", "source": "c", "target": gap_id}],
        ), round_number=2)
        self.assertEqual(context.gap_registry()[0]["state"], "resolved")
        self.assertNotIn(gap_id, [i.id for i in context.deliberative_items()])


class ProjectionTest(unittest.TestCase):
    def test_projection_is_deterministic_and_complete(self):
        context = context_with_evidence()
        apply(context, block([{"local_id": "k1", "type": "claim", "content": "x"}]))
        self.assertEqual(project_json(context), project_json(WorkingContext.from_dict(context.to_dict())))
        self.assertEqual(len(json.loads(project_json(context))["items"]), 2)

    def test_contract_only_teaches_relations_the_graph_accepts(self):
        lines = {line.split(":")[0]: line for line in declaration_contract("pt-BR").splitlines() if line.startswith("- ")}
        self.assertIn("evidence→claim", lines["- supports"])
        self.assertEqual(lines["- selects"], "- selects: decision→option")


class DocumentTest(unittest.TestCase):
    def test_example_document_splits_by_article_and_drops_comments(self):
        items = split_markdown((ROOT / "examples/lgpd/documento.md").read_text(encoding="utf-8"), "lgpd")
        self.assertEqual([i.source_location for i in items][0], "Art. 1º")
        self.assertFalse(any("<!--" in i.content for i in items))


class FakeClient:
    model = "fake"
    temperature = 0.0

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def complete(self, messages):
        self.calls.append(messages)
        return self.replies.pop(0)


class SessionTest(unittest.TestCase):
    def test_unanswerable_question_ends_with_open_gap(self):
        evidence = split_markdown("# Art. 8º\nO consentimento...", "lgpd")
        client = FakeClient([
            block([{"local_id": "g1", "type": "gap", "content": "O trecho não traz o valor da multa."}], prose="Não está no documento."),
            block([{"local_id": "g1", "type": "gap", "content": "O trecho não traz o valor da multa."}], prose="Mantenho."),
            "Até R$ 50 milhões.",
        ])
        result = run_question(client, evidence, "texto", "Qual a multa máxima?")
        self.assertEqual([g["state"] for g in result["gaps"]], ["open"])
        self.assertEqual(result["baseline"], "Até R$ 50 milhões.")
        # a revisão vê a resposta anterior como itens no Working Context
        self.assertIn("O trecho não traz o valor da multa.", client.calls[1][0]["content"])

    def test_key_never_appears_in_client_repr(self):
        from documental_engine.llm import ChatClient
        self.assertNotIn("segredo", repr(ChatClient(api_key="segredo", model="m")))


if __name__ == "__main__":
    unittest.main()
