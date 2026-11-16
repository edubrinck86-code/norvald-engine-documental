from dataclasses import dataclass


@dataclass(frozen=True)
class MalformedContributionPart:
    """Parte do bloco CONTRIBUTION que o parser não conseguiu ler.

    Uma unidade sem `local_id` ou uma relação sem `target` não descarta o
    bloco inteiro: a parte defeituosa é registrada e as demais seguem para
    o validador.

    Nada é reparado: o campo ausente não é preenchido nem inferido. A
    parte é recusada, com posição e motivo, e aparece entre as recusas do
    validador.

    `kind` é "knowledge" ou "relation". `index` é a posição da parte na
    lista declarada, contada a partir de zero. `identifier` é o
    `local_id` quando existe, ou vazio.
    """

    kind: str
    index: int
    identifier: str
    reason: str
