# Norvald documental engine

*[Português abaixo](#português)*

**Auditable AI answers: every statement linked to the passage that supports it, every "I don't know" recorded as an item.**

Anyone running LLMs over documents (contracts, regulations, case files, medical records) hits the same three problems:

1. **You can't check where the answer came from.** Running text mixes what is in the document with what the model assumed.
2. **"Not stated" gets lost.** When the information isn't there, the model either invents or answers vaguely, and nobody can count how many questions went unanswered.
3. **The model changes its mind for no reason.** On a second pass, it revises what it already had right.

The engine solves this with a simple contract: the model answers and declares, in a structured format, every statement with a **type**, a **confidence** and the **document passage** that supports it. Gaps and open questions become items with a state (open, resolved, superseded). The engine validates the form, rejects what doesn't fit (with the reason) and stores everything in a graph that can be audited, counted and exported.

## Who it is for

- **Legal and compliance:** opinions where every conclusion points to the article or clause.
- **Regulation and oversight:** case triage where "no information" must be recorded, not omitted.
- **Health and insurance:** reading rules and documents where a wrong answer is expensive.
- **AI teams:** a declaration and validation layer that works with any OpenAI-compatible model, with no judge and no second model.

## Why trust it

The method comes from three preregistered studies with open data, and exploratory tests with more than 30 models:

- **Seeing its own reasoning stabilizes review.** When the model reviews its own full work, not just its previous choice, answer changes drop from **18.8% to 2.9%**.
- **The engine's format stabilizes it further.** With the same content organized as items and relations instead of running text, answer changes drop from **10.3% to 3.9%** (p = 0.00006, 431 pairs), with no loss of corrections.
- **And it is cheaper.** On the same questions and models, review in the engine's format cost **6.6% less** per call: the model gets slightly more context but rewrites less.

| Study | Preregistration | Paper (DOI) |
|---|---|---|
| How many contribute and how many just agree (herding in model panels) | [osf.io/aw9vf](https://osf.io/aw9vf) | [10.5281/zenodo.24265239](https://doi.org/10.5281/zenodo.24265239) |
| How many judges are five models worth (error correlation) | [osf.io/5dpjr](https://osf.io/5dpjr) | [10.5281/zenodo.24265355](https://doi.org/10.5281/zenodo.24265355) |
| Does the format of the previous answer anchor the review? | [osf.io/46erj](https://osf.io/46erj) | [10.5281/zenodo.24265357](https://doi.org/10.5281/zenodo.24265357) |

## Try it on your documents

Open source (Apache-2.0); it runs on your machine with your key, so the document never leaves your environment. Questions about integration or the research: **contato@norvald.com.br**.

> This is one part of the system; the broader version is under testing.

## How it works

```
document ──► passages (evidence) ──► Working Context
                                         │
question ──► model answers + declares ──► engine validates ──► graph
                                         │        └─ rejections with reason
                    review: the model sees its own answer as items
```

- `documental_engine/contribution.py`: reads the declared block; one malformed part does not bring down the others.
- `documental_engine/validation.py`: declarable type, non-empty content, relation allowed by the graph, existing target.
- `documental_engine/graph.py`: the allowed relations and the gap life cycle (open, resolved, superseded).
- `documental_engine/projection.py`: what the model sees, complete and deterministic.
- `documental_engine/instructions.py`: the declaration contract (pt-BR and en), generated from the graph.

The engine never calls a model to judge another: there is no reviewer and no judge. It only validates the form of what was declared.

## Run

No dependencies for the engine (Python 3.10+).

```bash
python -m unittest -v
```

Example on a passage of Brazil's data protection law (LGPD):

```bash
export OPENROUTER_API_KEY=...        # your key; never written to disk
python examples/run.py --model openai/gpt-4o-mini --language en
```

Local dashboard (the key is typed on screen and lives only in the server's memory, on 127.0.0.1):

```bash
pip install fastapi uvicorn
python dashboard/server.py           # http://127.0.0.1:8790
```

The dashboard also opens without a server: open `dashboard/index.html` and pick a `resultado.json`. There is a ready one in `examples/lgpd/resultado-exemplo.json` (gpt-4o-mini, 2026-11-16).

## See it working

The example runs the engine on a passage of the LGPD: every statement comes out linked to the article that supports it, and whatever the passage does not answer becomes a recorded gap, with a state, that can be counted, audited and resolved later. The stability and cost numbers come from the three preregistered studies above.

## License

Apache 2.0. See `LICENSE` and `NOTICE`.

Eduardo Guedes · Norvald · ORCID [0009-0003-9960-3337](https://orcid.org/0009-0003-9960-3337) · [norvald.com.br/engine](https://norvald.com.br/engine/) · contato@norvald.com.br

---

## Português

**Respostas de IA que se pode auditar: cada afirmação ligada ao trecho que a sustenta, e cada "não sei" registrado como item.**

Quem usa LLM sobre documentos (contratos, normas, processos, prontuários) esbarra sempre nos mesmos três problemas:

1. **Não dá para conferir de onde veio a resposta.** O texto corrido mistura o que está no documento com o que o modelo supôs.
2. **O "não consta" se perde.** Quando a informação não existe, ou o modelo inventa, ou responde vago, e ninguém consegue contar quantas perguntas ficaram sem resposta.
3. **O modelo muda de ideia sem motivo.** Numa segunda rodada, ele revisa o que já tinha acertado.

A engine resolve isso com um contrato simples: o modelo responde e declara, em formato estruturado, cada afirmação com **tipo**, **confiança** e o **trecho do documento** que a sustenta. Lacunas e perguntas em aberto viram itens com estado (aberta, resolvida, substituída). A engine valida a forma, recusa o que não fecha (com o motivo) e guarda tudo num grafo que pode ser auditado, contado e exportado.

### Para quem

- **Jurídico e compliance:** parecer com cada conclusão apontando o artigo ou a cláusula.
- **Regulação e controle:** triagem de processos em que "não há informação" precisa ser registrado, não omitido.
- **Saúde e seguros:** leitura de normas e documentos em que a resposta errada custa caro.
- **Times de IA:** uma camada de declaração e validação que funciona com qualquer modelo compatível com a API da OpenAI, sem juiz nem segundo modelo.

### Por que confiar

O método vem de três estudos pré-registrados, com dados abertos, e testes exploratórios com mais de 30 modelos (pré-registros e DOIs na tabela acima):

- **Ver o próprio raciocínio estabiliza a revisão.** Quando o modelo revê o próprio trabalho completo, e não só a escolha anterior, a troca de resposta cai de **18,8% para 2,9%**.
- **O formato da engine estabiliza ainda mais.** Com o mesmo conteúdo, organizado em itens e relações em vez de texto corrido, a troca cai de **10,3% para 3,9%** (p = 0,00006, 431 pares), sem perder correções.
- **E sai mais barato.** Nas mesmas perguntas e modelos, a revisão no formato da engine custou **6,6% menos** por chamada: o modelo recebe um pouco mais de contexto, mas reescreve menos.

### Teste nos seus documentos

O código é aberto (Apache-2.0) e roda na sua máquina, com a sua chave: o documento não sai do seu ambiente. Dúvidas sobre integração ou sobre a pesquisa: **contato@norvald.com.br**.

> Esta é uma parte do sistema; a versão mais ampla está em teste.

### Rodar

```bash
python -m unittest -v
export OPENROUTER_API_KEY=...        # a sua chave; nunca é gravada
python examples/run.py --model openai/gpt-4o-mini
pip install fastapi uvicorn && python dashboard/server.py   # http://127.0.0.1:8790
```

O painel também abre sem servidor: abra `dashboard/index.html` e escolha um `resultado.json` (há um pronto em `examples/lgpd/resultado-exemplo.json`). A arquitetura está descrita em [How it works](#how-it-works).

### Veja funcionando

O exemplo roda a engine sobre um trecho da LGPD: cada afirmação sai ligada ao artigo que a sustenta, e o que o trecho não responde vira lacuna registrada, com estado, que pode ser contada, auditada e resolvida depois. Os números de estabilidade e custo vêm dos três estudos pré-registrados acima.

### Licença

Apache 2.0. Veja `LICENSE` e `NOTICE`.
