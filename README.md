# Engine documental Norvald

*[English below](#english)*

**Respostas de IA que se pode auditar: cada afirmação ligada ao trecho que a sustenta, e cada "não sei" registrado como item.**

Quem usa LLM sobre documentos (contratos, normas, processos, prontuários) esbarra sempre nos mesmos três problemas:

1. **Não dá para conferir de onde veio a resposta.** O texto corrido mistura o que está no documento com o que o modelo supôs.
2. **O "não consta" se perde.** Quando a informação não existe, ou o modelo inventa, ou responde vago, e ninguém consegue contar quantas perguntas ficaram sem resposta.
3. **O modelo muda de ideia sem motivo.** Numa segunda rodada, ele revisa o que já tinha acertado.

A engine resolve isso com um contrato simples: o modelo responde e declara, em formato estruturado, cada afirmação com **tipo**, **confiança** e o **trecho do documento** que a sustenta. Lacunas e perguntas em aberto viram itens com estado (aberta, resolvida, substituída). A engine valida a forma, recusa o que não fecha (com o motivo) e guarda tudo num grafo que pode ser auditado, contado e exportado.

## Para quem

- **Jurídico e compliance:** parecer com cada conclusão apontando o artigo ou a cláusula.
- **Regulação e controle:** triagem de processos em que "não há informação" precisa ser registrado, não omitido.
- **Saúde e seguros:** leitura de normas e documentos em que a resposta errada custa caro.
- **Times de IA:** uma camada de declaração e validação que funciona com qualquer modelo compatível com a API da OpenAI, sem juiz nem segundo modelo.

## Por que confiar

O método vem de três estudos pré-registrados, com dados abertos, cerca de 11 mil perguntas e mais de 30 modelos:

- **Ver o próprio raciocínio estabiliza a revisão.** Quando o modelo revê o próprio trabalho completo, e não só a escolha anterior, a troca de resposta cai de **18,8% para 2,9%**.
- **O formato da engine estabiliza ainda mais.** Com o mesmo conteúdo, organizado em itens e relações em vez de texto corrido, a troca cai de **10,3% para 3,9%** (p = 0,00006), sem perder correções.
- **E sai mais barato.** Nas mesmas perguntas e modelos, a revisão no formato da engine custou **6,6% menos** por chamada: o modelo recebe um pouco mais de contexto, mas reescreve menos.

## Teste nos seus documentos

O código é aberto (Apache-2.0) e roda na sua máquina, com a sua chave: o documento não sai do seu ambiente. Se preferir, rodamos um piloto **gratuito** num documento e num conjunto de perguntas escolhidos por você, e entregamos o resultado com cada fonte marcada: **contato@norvald.com.br**.

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

**Auditable AI answers: every statement linked to the passage that supports it, every "I don't know" recorded as an item.**

For legal, compliance, regulatory and health teams running LLMs over documents. Works with any OpenAI-compatible model, no judge or second model. Runs on your machine with your key.

**Free pilot** on a document and questions you choose: contato@norvald.com.br

Each answer ends with a structured declaration: every statement with a **type** (claim, inference, decision, gap, open question...), a **confidence**, and its **relations** to the document excerpts that support it. The engine accepts what fits, rejects the rest with a reason, and stores everything in a graph, the Working Context. On the next turn the model sees its own reasoning in this form, not as running text.

> This is one part of the system; the broader version is under testing.

**Research.** Three preregistered studies with open data (DOIs above). Seeing its own full reasoning, rather than only its previous choice, cut answer changes from 18.8% to 2.9%. In the third, seeing one's own previous answer as items and relations, rather than plain text with the same content, made models change their answer in 3.9% of reviews against 10.3% (p = 0.00006, 431 pairs), with no loss of correction, and at 6.6% lower cost per call.

**Run.** `python -m unittest -v` (no dependencies, Python 3.10+). Example: `OPENROUTER_API_KEY=... python examples/run.py --model openai/gpt-4o-mini --language en`. Local dashboard: `pip install fastapi uvicorn && python dashboard/server.py` (127.0.0.1 only; the key lives in memory only). The dashboard also opens statically on a `resultado.json`.

**What the example shows.** In the bundled run the model answered the three answerable questions and flagged the two unanswerable ones as gaps; without the engine it did not invent answers either. The difference is that every statement is linked to the article that supports it, and every gap is a tracked item. Five questions do not measure stability; the studies do.

**License.** Apache 2.0.
