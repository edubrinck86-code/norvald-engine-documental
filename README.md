# Engine documental Norvald

*[English below](#english)*

O modelo declara o que sabe; a engine valida e organiza.

Em vez de entregar ao modelo um texto corrido e torcer para ele se lembrar do que disse, a engine pede que cada resposta termine com uma declaração estruturada: cada afirmação com um **tipo** (afirmação, inferência, decisão, lacuna, pergunta em aberto...), uma **confiança** e as **relações** com os trechos do documento que a sustentam. A engine lê essa declaração, aceita o que fecha, recusa o resto com o motivo e guarda tudo num grafo, o Working Context. Na rodada seguinte, o modelo recebe o próprio raciocínio nesse formato, e não como texto corrido.

> Esta é uma parte do sistema; a versão mais ampla está em teste.

## O que a pesquisa mediu

Três estudos pré-registrados, com dados abertos:

| Estudo | DOI |
|---|---|
| Quantos contribuem e quantos só concordam (efeito manada em painéis de modelos) | [10.5281/zenodo.24265239](https://doi.org/10.5281/zenodo.24265239) |
| Quantos juízes valem cinco modelos (correlação de erros) | [10.5281/zenodo.24265355](https://doi.org/10.5281/zenodo.24265355) |
| O formato da resposta anterior ancora a revisão? | [10.5281/zenodo.24265357](https://doi.org/10.5281/zenodo.24265357) |

No terceiro, com o mesmo conteúdo, ver a própria resposta anterior como itens e relações (o formato desta engine) fez os modelos mudarem de resposta em 3,9% das revisões, contra 10,3% em texto corrido (p = 0,00006, 431 pares), sem perder correções.

## Como funciona

```
documento ──► trechos (evidence) ──► Working Context
                                         │
pergunta ──► modelo responde + declara ──► engine valida ──► grafo
                                         │        └─ recusas com motivo
                       revisão: o modelo vê a própria resposta como itens
```

- `documental_engine/contribution.py`: lê o bloco declarado; uma parte defeituosa não derruba as outras.
- `documental_engine/validation.py`: tipo declarável, conteúdo não vazio, relação permitida pelo grafo, alvo existente.
- `documental_engine/graph.py`: as relações permitidas e o ciclo de vida das lacunas (aberta, resolvida, substituída).
- `documental_engine/projection.py`: o que o modelo vê, integral e determinístico.
- `documental_engine/instructions.py`: o contrato de declaração (pt-BR e en), gerado a partir do grafo.

A engine não chama nenhum modelo para julgar outro: não há revisor nem juiz. Só valida a forma do que foi declarado.

## Rodar

Sem dependências para a engine (Python 3.10+).

```bash
python -m unittest -v
```

Exemplo com um trecho da LGPD e cinco perguntas, duas sem resposta no trecho:

```bash
export OPENROUTER_API_KEY=...        # a sua chave; nunca é gravada
python examples/run.py --model openai/gpt-4o-mini
```

Painel local (a chave é digitada na tela e fica só na memória do servidor, em 127.0.0.1):

```bash
pip install fastapi uvicorn
python dashboard/server.py           # http://127.0.0.1:8790
```

O painel também abre sem servidor: abra `dashboard/index.html` e escolha um `resultado.json`. Há um pronto em `examples/lgpd/resultado-exemplo.json` (gpt-4o-mini, 16/11/2026).

## O que o exemplo mostra, e o que não mostra

No exemplo pronto, o modelo acertou as três perguntas respondíveis e marcou as duas sem resposta como lacunas. Sem a engine, o mesmo modelo também não inventou resposta nessas duas. A diferença está em como o resultado chega: com a engine, cada afirmação está ligada ao artigo que a sustenta e cada lacuna é um item com estado, que pode ser contado, auditado e resolvido depois. Cinco perguntas de um modelo não medem estabilidade; para isso existem os estudos acima.

## Licença

Apache 2.0. Veja `LICENSE` e `NOTICE`.

Eduardo Guedes · Norvald · ORCID [0009-0003-9960-3337](https://orcid.org/0009-0003-9960-3337) · contato@norvald.com.br

---

## English

The model declares what it knows; the engine validates and organizes it.

Each answer ends with a structured declaration: every statement with a **type** (claim, inference, decision, gap, open question...), a **confidence**, and its **relations** to the document excerpts that support it. The engine accepts what fits, rejects the rest with a reason, and stores everything in a graph, the Working Context. On the next turn the model sees its own reasoning in this form, not as running text.

> This is one part of the system; the broader version is under testing.

**Research.** Three preregistered studies with open data (DOIs above). In the third, seeing one's own previous answer as items and relations, rather than plain text with the same content, made models change their answer in 3.9% of reviews against 10.3% (p = 0.00006, 431 pairs), with no loss of correction.

**Run.** `python -m unittest -v` (no dependencies, Python 3.10+). Example: `OPENROUTER_API_KEY=... python examples/run.py --model openai/gpt-4o-mini --language en`. Local dashboard: `pip install fastapi uvicorn && python dashboard/server.py` (127.0.0.1 only; the key lives in memory only). The dashboard also opens statically on a `resultado.json`.

**What the example shows.** In the bundled run the model answered the three answerable questions and flagged the two unanswerable ones as gaps; without the engine it did not invent answers either. The difference is that every statement is linked to the article that supports it, and every gap is a tracked item. Five questions do not measure stability; the studies do.

**License.** Apache 2.0.
