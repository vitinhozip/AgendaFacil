# AgendaFácil

Agenda de atendimentos de uma clínica pequena: **marca**, **remarca** e **lista**
atendimentos, tudo em memória (sem banco de dados e sem interface gráfica).
Projeto da Unidade 1 de DIM0501 — Boas Práticas de Programação (DIMAp/UFRN, 2026.1),
versão refatorada do código-base `agenda_base.py`.

## Requisitos

- Python 3.10 ou superior.
- O programa usa **apenas a biblioteca padrão**. A ferramenta `pdoc` é necessária
  somente para gerar a documentação (não é dependência do programa).

## Como executar

Python não precisa de compilação. Para rodar a demonstração:

```bash
python3 agenda_facil.py
```

Saída esperada (idêntica à do código-base original):

```text
Atendimento marcado para Ana
Horario ocupado
Atendimento marcado para Carla
Remarcado
14 Carla Dra. Souza MARCADO
```

Para usar como biblioteca:

```python
from agenda_facil import Agenda

agenda = Agenda()
agenda.marcar("Ana", "Dr. Silva", "2026-10-05", 9, 30)
agenda.remarcar("Ana", "2026-10-05", 9, "2026-10-06", 10)
agenda.listar_por_data("2026-10-06")
```

## Regras de negócio

| Regra     | Definição                                                              |
|-----------|------------------------------------------------------------------------|
| Expediente | Atendimentos começam entre 8h e 17h e terminam até as 18h.            |
| Duração   | De 15 a 120 minutos, em múltiplos de 15.                               |
| Conflito  | Um profissional não pode ter dois atendimentos no mesmo dia e horário. |
| Data      | Formato `AAAA-MM-DD`; qualquer outro formato é entrada inválida.       |

Entradas inválidas lançam `EntradaInvalidaError` (também é um `ValueError`);
conflito lança `ConflitoDeHorarioError`; remarcar algo que não existe lança
`AtendimentoNaoEncontradoError`. Todas herdam de `AgendaError`.

## Como gerar a documentação da API

```bash
pip install pdoc
python3 -m pdoc agenda_facil -o docs
```

A documentação HTML fica na pasta `docs/`; abra `docs/agenda_facil.html` no
navegador. Para navegar sem gerar arquivos: `python3 -m pdoc agenda_facil`.

## Estrutura

```text
agenda_facil.py   código refatorado (módulo + demonstração)
README.md         este arquivo
RELATORIO.md      diagnóstico, decisões e mudanças de comportamento
docs/             documentação de API gerada com pdoc
```

## Autoria

   - Joackym Pedro Araujo Coelho — 2025002667
   - Renato Augusto Silva — 20250061567
   - Kleison Vitoriano da Silva — 2025006607
   - Vitor Gabriel da Costa Sousa — 20250027387

   Uso de ferramentas de IA declarado no `RELATORIO.md`.
