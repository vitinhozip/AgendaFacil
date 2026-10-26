# Relatório do Projeto da Unidade 1 — AgendaFácil

DIM0501 — Boas Práticas de Programação · Prof. Marcus Terra · DIMAp/UFRN · 2026.1

| Integrantes (nome e matrícula) | Linguagem |
|---|---|
|Joackym Pedro Araujo Coelho - 2025002667|Python 3.10+ (testado em 3.14; só biblioteca padrão)|
|Renato Augusto Silva - 20250061567|Python 3.10+ (testado em 3.14; só biblioteca padrão)|
|Kleison Vitoriano da Silva - 2025006607|Python 3.10+ (testado em 3.14; só biblioteca padrão)|
|Vitor Gabriel da Costa Sousa - 20250027387|Python 3.10+ (testado em 3.14; só biblioteca padrão)|

Entregue em: https://github.com/vitinhozip/AgendaFacil

## 1. Diagnóstico do código-base

Linhas referem-se ao `agenda_base.py` original.

| # | Categoria | Anomalia e onde está | Por que é um problema |
|---|---|---|---|
| 1 | Adequação e lógica | `add` (l. 14-16, 26-27): hora fora de 8h–18h ou duração ≤ 0 não faz nada e não avisa. | Quem chama acredita que marcou; o paciente chega e não existe atendimento. |
| 2 | Adequação e lógica | `add`/`rem`: regras ausentes — duração máxima de 120 min e múltiplo de 15, término até 18h (17h com 300 min passa) e formato da data. | A agenda aceita dados que a clínica não consegue atender; datas como `"hoje"` entram e nunca casam com nada. |
| 3 | Adequação e lógica | `rem` (l. 30-43): não valida o novo dia/hora, não avisa quando o atendimento não existe e remarca todos os que casam. | Dá para remarcar para as 22h, e um erro de digitação no nome falha em silêncio. |
| 4 | Adequação e lógica | Conflito compara só a hora de **início** (l. 19, 36); 9h com 90 min e outro às 10h do mesmo profissional passam. | Dois pacientes podem ser marcados sobrepostos para o mesmo profissional. |
| 5 | Adequação e lógica | `lst` (l. 52-56): comentário diz "do mês", mas filtra o dia exato; nada é retornado, só impresso. | O comentário engana quem lê; o resultado não pode ser reaproveitado nem testado. |
| 6 | Manutenibilidade | Nomes opacos: `ag`, `add`, `rem`, `lst`, `p`, `pr`, `d`, `h`, `dur`, `nd`, `nh`, `a`, `b`, `ok`. | Cada leitura exige adivinhar o significado (`pr` é profissional? preço?). |
| 7 | Manutenibilidade | Atendimento é uma lista acessada por posição: `a[2]`, `a[3]`, `a[1]`, `a[5]` (l. 19, 22, 33, 56). | Trocar ou acrescentar um campo quebra tudo sem aviso; o índice não diz o que é. |
| 8 | Manutenibilidade | Verificação de conflito duplicada em `add` (l. 18-20) e `rem` (l. 35-37). | Mudar a regra exige lembrar de editar dois lugares; um deles será esquecido. |
| 9 | Manutenibilidade | `add`, `rem` e `lst` validam, buscam, alteram e imprimem ao mesmo tempo; estado em variável global `ag` (l. 8). | Não dá para testar a regra sem capturar a saída; qualquer código pode alterar `ag`. |
| 10 | Manutenibilidade | Valores com significado de negócio soltos: `8`, `18`, `"MARCADO"`, textos das mensagens. | Mudar o expediente exige caçar números pelo arquivo. |
| 11 | Organização e estética | `add`: três `if` aninhados + `for` + `if` + `try` (l. 13-25). | A lógica principal fica enterrada vários níveis adentro. |
| 12 | Organização e estética | Cabeçalho com histórico de alterações (l. 2-5), comentários de ruído (l. 12, 31, 53) e TODO vencido de 2025 (l. 49). | O histórico é papel do Git; ruído e TODO velho ensinam a ignorar comentários. |
| 13 | Organização e estética | Código morto comentado: `desmarcar` (l. 46-47). | Ninguém sabe se é plano, esquecimento ou lixo. |
| 14 | Organização e estética | Demonstração executa no nível do módulo (l. 59-63), sem `if __name__ == "__main__"`. | Importar o arquivo já marca atendimentos; não dá para reutilizar como biblioteca. |
| 15 | Prog. defensiva e segurança | `except: pass` (l. 26-27) em `add`. | Engole qualquer erro, até `KeyboardInterrupt`; um bug vira um mistério. |
| 16 | Prog. defensiva e segurança | Sem validação de tipo ou vazio: `h="9"`, `None` ou `p=""` são aceitos ou geram `TypeError` engolido. | Dados corrompidos entram na agenda e estouram longe de onde nasceram. |
| 17 | Desempenho e recursos | `rem` tem laço dentro de laço (O(n²)) e continua varrendo depois de remarcar (l. 32-43). | Custo cresce rápido com a agenda e há trabalho inútil. |
| 18 | Desempenho e recursos | Conflito por varredura linear da lista inteira a cada operação (l. 18, 35). | O(n) por marcação; irrelevante hoje, ruim se a clínica crescer. |

## 2. O que foi resolvido e o que ficou como dívida

| # | Situação | Como foi resolvida, ou por que ficou |
|---|---|---|
| 1 | Resolvida | `marcar` lança `EntradaInvalidaError` informando o campo e o valor. |
| 2 | Resolvida | `_validar_duracao`, `_validar_expediente` e `_validar_data` implementam as quatro regras. |
| 3 | Resolvida | `remarcar` valida tudo, lança `AtendimentoNaoEncontradoError` e move um único atendimento (ressalva na seção 4). |
| 4 | Dívida assumida | A regra do enunciado define conflito como "mesmo dia e horário"; detectar sobreposição por duração é regra nova. Registrado em comentário de decisão em `_existe_conflito`. |
| 5 | Resolvida | Renomeada para `listar_por_data`, devolve a lista e a docstring diz o que faz; a impressão ficou em `listar_e_informar`. |
| 6 | Resolvida | Nomes completos em PEP 8: `Agenda`, `marcar`, `remarcar`, `paciente`, `profissional`… |
| 7 | Resolvida | `Atendimento` é uma `dataclass` com campos nomeados. |
| 8 | Resolvida | Uma única função, `Agenda._existe_conflito`, usada por `marcar` e `remarcar`. |
| 9 | Resolvida | Validação (`_validar_*`), regra (`Agenda`) e impressão (`*_e_informar`) separadas; o estado é privado dentro de `Agenda`. |
| 10 | Resolvida | Constantes `HORA_ABERTURA`, `HORA_FECHAMENTO`, `STATUS_MARCADO`, `MENSAGEM_*`… |
| 11 | Resolvida | Cláusulas de guarda no início de cada método público; a lógica principal ficou no primeiro nível. |
| 12 | Resolvida | Cabeçalho, ruído e TODO removidos; ficaram dois comentários de decisão (conflito e validação de data). |
| 13 | Resolvida | Código morto removido. `desmarcar` não faz parte do escopo. |
| 14 | Resolvida | Demonstração em `executar_demonstracao()` sob `if __name__ == "__main__"`. |
| 15 | Resolvida | Nenhum `except` genérico; só `ConflitoDeHorarioError` é capturado, e apenas na camada de demonstração. |
| 16 | Resolvida | Validação de tipo, vazio e `bool` em `_validar_texto` e `_validar_inteiro`. |
| 17 | Resolvida | `_localizar` para na primeira ocorrência e não há laço aninhado. |
| 18 | Dívida assumida | Para uma clínica pequena em memória, a varredura linear é legível e suficiente; um índice por `(profissional, data, hora)` seria a evolução se o volume crescer. |

## 3. Decisões de projeto

| Decisão tomada | Alternativa descartada | Por que decidimos assim |
|---|---|---|
| `Atendimento` como `dataclass(frozen=True)` dentro de uma classe `Agenda` que guarda a lista. | Dicionários e uma lista global manipulada por funções soltas. | Campos nomeados eliminam os índices mágicos; a imutabilidade obriga toda mudança a passar por `Agenda`, onde ficam as validações; sem global, dá para ter várias agendas e testar isolado. |
| Erros viram exceções específicas (`EntradaInvalidaError` herda também de `ValueError`); conflito também é exceção. | Devolver `False`/`None` ou uma mensagem de erro em texto. | Um retorno pode ser ignorado, e foi assim que o código original falhava em silêncio. Exceção força o chamador a decidir, e a mensagem carrega o campo e o valor recebido. |
| Separar validação (`_validar_*`), regra (`Agenda`) e apresentação (`*_e_informar`). | Uma função grande por operação, como no original. | Cada função tem um motivo para mudar. Conflito é resultado esperado da demonstração e vira mensagem só na camada de apresentação; a regra continua reutilizável. |
| Data guardada como `str` validada por regex + `strptime`. | Converter para `datetime.date`; ou usar só `strptime`. | `strptime` sozinho aceita `"2026-1-5"`, contrariando "AAAA-MM-DD". Manter `str` preserva a saída do código-base e, em ISO, a ordem de texto é a ordem cronológica. |

## 4. Mudanças de comportamento

O caminho feliz **não mudou**: a saída da demonstração é idêntica (diff vazio).

| Entrada ou situação | O que acontecia antes | O que acontece agora |
|---|---|---|
| Marcar às 20h (ou antes das 8h) | Nada, sem aviso. | `EntradaInvalidaError` com hora e regra. |
| Duração 0, negativa, 20 ou 135 | 0/negativa: nada. 20 e 135: aceito. | `EntradaInvalidaError` (15 a 120, múltiplo de 15). |
| Atendimento terminando depois das 18h (17h, 75 min) | Aceito. | `EntradaInvalidaError`. |
| Data fora de AAAA-MM-DD (`"2026-1-5"`, `"hoje"`, `None`) ou inexistente (`"2026-02-30"`) | Aceita como texto. | `EntradaInvalidaError`. |
| Paciente/profissional vazio ou hora não inteira (`9.5`, `True`) | Aceito, ou `TypeError` engolido. | `EntradaInvalidaError`. |
| Remarcar atendimento que não existe | Nada, sem aviso. | `AtendimentoNaoEncontradoError`. |
| Remarcar para fora do expediente ou data inválida | Aceito. | `EntradaInvalidaError`. |
| Remarcar para o mesmo dia e hora em que já está | "Horario ocupado" (conflito consigo mesmo). | Aceito, sem efeito. |
| Remarcar quando o paciente tem dois atendimentos idênticos (mesma data e hora) | Remarcava todos. | Remarca só o primeiro. Dívida: a regra não define o caso. |
| Listar com data inválida | Lista vazia. | `EntradaInvalidaError`. |
| Importar o módulo | Executava a demonstração. | Só executa com `python3 agenda_facil.py`. |

## 5. Como executar e gerar a documentação

| Item | Resposta |
|---|---|
| Comando para compilar e executar | `python3 agenda_facil.py` (Python não compila) |
| Comando para gerar a documentação de API | `pip install pdoc` e `python3 -m pdoc agenda_facil -o docs` |
| Onde a documentação gerada ficou | `docs/agenda_facil.html` |
| Saída do programa de demonstração | ver abaixo |

```text
Atendimento marcado para Ana
Horario ocupado
Atendimento marcado para Carla
Remarcado
14 Carla Dra. Souza MARCADO
```

## 6. Uso de ferramentas de IA

| Pergunta | Resposta |
|---|---|
| Foram usadas ferramentas de IA neste trabalho? | (X) Sim |
| Em quais etapas, e para quê? | Claude (Anthropic) foi usado para produzir uma primeira versão do projeto, como auxiliar de código, gerou a documentação de API e também produziu o relatório.|
