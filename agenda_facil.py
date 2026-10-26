"""AgendaFácil: agenda de atendimentos de uma clínica pequena.

O módulo marca, remarca e lista atendimentos mantidos em memória. Toda
entrada é validada antes do uso: entradas inválidas geram exceções
específicas (ver :class:`AgendaError`) em vez de falhar em silêncio.

Exemplo:
    >>> agenda = Agenda()
    >>> atendimento = agenda.marcar("Ana", "Dr. Silva", "2026-10-05", 9, 30)
    >>> atendimento.hora
    9

Para executar a demonstração::

    python3 agenda_facil.py
"""

import re
from dataclasses import dataclass, replace
from datetime import datetime

# --- Regras de negócio -------------------------------------------------------

HORA_ABERTURA = 8
HORA_FECHAMENTO = 18
MINUTOS_POR_HORA = 60
DURACAO_MINIMA_MINUTOS = 15
DURACAO_MAXIMA_MINUTOS = 120
MULTIPLO_DURACAO_MINUTOS = 15
FORMATO_DATA = "%Y-%m-%d"
PADRAO_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
STATUS_MARCADO = "MARCADO"

# --- Mensagens exibidas pela demonstração (camada de apresentação) -----------

MENSAGEM_ATENDIMENTO_MARCADO = "Atendimento marcado para"
MENSAGEM_REMARCADO = "Remarcado"
MENSAGEM_HORARIO_OCUPADO = "Horario ocupado"


# --- Exceções ----------------------------------------------------------------


class AgendaError(Exception):
    """Classe base de todos os erros específicos da agenda."""


class EntradaInvalidaError(AgendaError, ValueError):
    """Um argumento viola o formato ou uma regra de negócio.

    Herda também de ``ValueError`` para que quem já captura ``ValueError``
    continue funcionando.
    """


class ConflitoDeHorarioError(AgendaError):
    """O profissional já possui atendimento no mesmo dia e horário."""


class AtendimentoNaoEncontradoError(AgendaError):
    """Não existe atendimento correspondente aos dados informados."""


# --- Modelo ------------------------------------------------------------------


@dataclass(frozen=True)
class Atendimento:
    """Um atendimento agendado.

    A classe é imutável: para alterar um atendimento, cria-se outro com
    :func:`dataclasses.replace`. Isso impede que código externo mude a agenda
    sem passar pelas validações de :class:`Agenda`.

    Attributes:
        paciente: Nome do paciente.
        profissional: Nome do profissional que atende.
        data: Data no formato ``AAAA-MM-DD``.
        hora: Hora de início, inteira, entre ``HORA_ABERTURA`` e 17.
        duracao_minutos: Duração em minutos (15 a 120, múltiplo de 15).
        status: Situação do atendimento.
    """

    paciente: str
    profissional: str
    data: str
    hora: int
    duracao_minutos: int
    status: str = STATUS_MARCADO


# --- Validações (privadas): só verificam, nunca alteram a agenda -------------


def _validar_texto(nome_campo, valor):
    if not isinstance(valor, str) or not valor.strip():
        raise EntradaInvalidaError(
            f"{nome_campo} deve ser um texto não vazio; recebido: {valor!r}"
        )


def _validar_data(data):
    # strptime sozinho aceita "2026-1-5"; a regex exige o formato com zeros.
    if not isinstance(data, str) or not PADRAO_DATA.fullmatch(data):
        raise EntradaInvalidaError(
            f"data deve estar no formato AAAA-MM-DD; recebido: {data!r}"
        )
    try:
        datetime.strptime(data, FORMATO_DATA)
    except ValueError:
        raise EntradaInvalidaError(
            f"data não existe no calendário; recebido: {data!r}"
        ) from None


def _validar_inteiro(nome_campo, valor):
    # bool é subclasse de int em Python; True não é uma hora válida.
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise EntradaInvalidaError(
            f"{nome_campo} deve ser um número inteiro; recebido: {valor!r}"
        )


def _validar_duracao(duracao_minutos):
    _validar_inteiro("duracao_minutos", duracao_minutos)
    fora_do_intervalo = not (
        DURACAO_MINIMA_MINUTOS <= duracao_minutos <= DURACAO_MAXIMA_MINUTOS
    )
    if fora_do_intervalo or duracao_minutos % MULTIPLO_DURACAO_MINUTOS != 0:
        raise EntradaInvalidaError(
            f"duracao_minutos deve estar entre {DURACAO_MINIMA_MINUTOS} e "
            f"{DURACAO_MAXIMA_MINUTOS}, em múltiplos de "
            f"{MULTIPLO_DURACAO_MINUTOS}; recebido: {duracao_minutos!r}"
        )


def _validar_expediente(hora, duracao_minutos):
    _validar_inteiro("hora", hora)
    if hora < HORA_ABERTURA:
        raise EntradaInvalidaError(
            f"hora de início deve ser a partir das {HORA_ABERTURA}h; "
            f"recebido: {hora!r}"
        )
    minutos_de_fim = hora * MINUTOS_POR_HORA + duracao_minutos
    if minutos_de_fim > HORA_FECHAMENTO * MINUTOS_POR_HORA:
        raise EntradaInvalidaError(
            f"atendimento deve terminar até as {HORA_FECHAMENTO}h; "
            f"hora={hora!r} com duracao_minutos={duracao_minutos!r} "
            f"termina depois do expediente"
        )


# --- Agenda ------------------------------------------------------------------


class Agenda:
    """Conjunto de atendimentos em memória, com marcação e remarcação.

    Os dados vivem apenas enquanto o objeto existir (sem banco de dados).
    """

    def __init__(self):
        self._atendimentos = []

    def marcar(self, paciente, profissional, data, hora, duracao_minutos):
        """Marca um novo atendimento.

        Args:
            paciente: Nome do paciente (texto não vazio).
            profissional: Nome do profissional (texto não vazio).
            data: Data no formato ``AAAA-MM-DD``.
            hora: Hora de início, inteira (8 a 17).
            duracao_minutos: Duração em minutos (15 a 120, múltiplo de 15).

        Returns:
            O :class:`Atendimento` criado, com status ``MARCADO``.

        Raises:
            EntradaInvalidaError: Se algum argumento violar o formato ou o
                expediente (8h às 18h).
            ConflitoDeHorarioError: Se o profissional já tiver atendimento
                na mesma data e hora.
        """
        _validar_texto("paciente", paciente)
        _validar_texto("profissional", profissional)
        _validar_data(data)
        _validar_duracao(duracao_minutos)
        _validar_expediente(hora, duracao_minutos)
        if self._existe_conflito(profissional, data, hora):
            raise ConflitoDeHorarioError(
                f"{profissional} já tem atendimento em {data} às {hora}h"
            )

        atendimento = Atendimento(
            paciente, profissional, data, hora, duracao_minutos
        )
        self._atendimentos.append(atendimento)
        return atendimento

    def remarcar(self, paciente, data, hora, nova_data, nova_hora):
        """Muda a data e a hora de um atendimento já marcado.

        A duração e o profissional do atendimento são mantidos. Remarcar
        para o mesmo horário em que o atendimento já está é aceito e não
        altera nada.

        Args:
            paciente: Nome do paciente do atendimento a remarcar.
            data: Data atual do atendimento (``AAAA-MM-DD``).
            hora: Hora atual do atendimento.
            nova_data: Nova data (``AAAA-MM-DD``).
            nova_hora: Nova hora de início, inteira.

        Returns:
            O :class:`Atendimento` já com a nova data e hora.

        Raises:
            EntradaInvalidaError: Se algum argumento violar o formato ou, na
                nova posição, o expediente.
            AtendimentoNaoEncontradoError: Se não houver atendimento do
                paciente na data e hora atuais.
            ConflitoDeHorarioError: Se o profissional já tiver atendimento
                na nova data e hora.
        """
        _validar_texto("paciente", paciente)
        _validar_data(data)
        _validar_inteiro("hora", hora)
        _validar_data(nova_data)
        _validar_inteiro("nova_hora", nova_hora)

        posicao = self._localizar(paciente, data, hora)
        atual = self._atendimentos[posicao]
        _validar_expediente(nova_hora, atual.duracao_minutos)
        if self._existe_conflito(
            atual.profissional, nova_data, nova_hora, ignorar=atual
        ):
            raise ConflitoDeHorarioError(
                f"{atual.profissional} já tem atendimento em {nova_data} "
                f"às {nova_hora}h"
            )

        remarcado = replace(atual, data=nova_data, hora=nova_hora)
        self._atendimentos[posicao] = remarcado
        return remarcado

    def listar_por_data(self, data):
        """Lista os atendimentos de um dia, na ordem em que foram marcados.

        Args:
            data: Data no formato ``AAAA-MM-DD``.

        Returns:
            Lista de :class:`Atendimento` da data. Vazia se não houver nenhum.

        Raises:
            EntradaInvalidaError: Se ``data`` não estiver no formato correto.
        """
        _validar_data(data)
        return [a for a in self._atendimentos if a.data == data]

    def _existe_conflito(self, profissional, data, hora, ignorar=None):
        # Decisão: conflito = mesmo profissional, dia e hora de INÍCIO, como
        # define a regra de negócio. Não detectamos sobreposição por duração
        # (ex.: 9h com 90 min e outro às 10h); isso exigiria uma regra nova.
        return any(
            a is not ignorar
            and a.profissional == profissional
            and a.data == data
            and a.hora == hora
            for a in self._atendimentos
        )

    def _localizar(self, paciente, data, hora):
        for posicao, atendimento in enumerate(self._atendimentos):
            if (
                atendimento.paciente == paciente
                and atendimento.data == data
                and atendimento.hora == hora
            ):
                return posicao
        raise AtendimentoNaoEncontradoError(
            f"nenhum atendimento de {paciente!r} em {data} às {hora}h"
        )


# --- Apresentação e demonstração ---------------------------------------------


def formatar_atendimento(atendimento):
    """Formata um atendimento como ``hora paciente profissional status``.

    Args:
        atendimento: O atendimento a exibir.

    Returns:
        Texto de uma linha, por exemplo ``"14 Carla Dra. Souza MARCADO"``.
    """
    return (
        f"{atendimento.hora} {atendimento.paciente} "
        f"{atendimento.profissional} {atendimento.status}"
    )


def marcar_e_informar(agenda, paciente, profissional, data, hora, duracao):
    """Marca um atendimento e imprime o resultado para o usuário.

    Conflito de horário é um resultado esperado da demonstração e vira
    mensagem; entradas inválidas continuam propagando a exceção.

    Args:
        agenda: A agenda onde marcar.
        paciente: Nome do paciente.
        profissional: Nome do profissional.
        data: Data no formato ``AAAA-MM-DD``.
        hora: Hora de início.
        duracao: Duração em minutos.

    Raises:
        EntradaInvalidaError: Se algum argumento for inválido.
    """
    try:
        agenda.marcar(paciente, profissional, data, hora, duracao)
    except ConflitoDeHorarioError:
        print(MENSAGEM_HORARIO_OCUPADO)
    else:
        print(MENSAGEM_ATENDIMENTO_MARCADO, paciente)


def remarcar_e_informar(agenda, paciente, data, hora, nova_data, nova_hora):
    """Remarca um atendimento e imprime o resultado para o usuário.

    Args:
        agenda: A agenda onde remarcar.
        paciente: Nome do paciente.
        data: Data atual do atendimento.
        hora: Hora atual do atendimento.
        nova_data: Nova data.
        nova_hora: Nova hora de início.

    Raises:
        EntradaInvalidaError: Se algum argumento for inválido.
        AtendimentoNaoEncontradoError: Se o atendimento não existir.
    """
    try:
        agenda.remarcar(paciente, data, hora, nova_data, nova_hora)
    except ConflitoDeHorarioError:
        print(MENSAGEM_HORARIO_OCUPADO)
    else:
        print(MENSAGEM_REMARCADO)


def listar_e_informar(agenda, data):
    """Imprime os atendimentos de uma data, um por linha.

    Args:
        agenda: A agenda a consultar.
        data: Data no formato ``AAAA-MM-DD``.

    Raises:
        EntradaInvalidaError: Se ``data`` for inválida.
    """
    for atendimento in agenda.listar_por_data(data):
        print(formatar_atendimento(atendimento))


def executar_demonstracao():
    """Executa o cenário de demonstração do código-base original."""
    agenda = Agenda()
    marcar_e_informar(agenda, "Ana", "Dr. Silva", "2026-10-05", 9, 30)
    marcar_e_informar(agenda, "Bruno", "Dr. Silva", "2026-10-05", 9, 30)
    marcar_e_informar(agenda, "Carla", "Dra. Souza", "2026-10-05", 14, 60)
    remarcar_e_informar(agenda, "Ana", "2026-10-05", 9, "2026-10-06", 10)
    listar_e_informar(agenda, "2026-10-05")


if __name__ == "__main__":
    executar_demonstracao()
