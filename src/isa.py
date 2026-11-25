"""Описание системы команд УВМ (вариант 6)."""

from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """Коды операций учебной виртуальной машины."""

    LOAD_CONST = 41
    LOAD_MEM = 25
    STORE_MEM = 49
    SUB_MEM = 30


# Ширины поля B (в битах) для каждой команды.
_OPERAND_BITS = {
    Opcode.LOAD_CONST: 13,
    Opcode.LOAD_MEM: 25,
    Opcode.STORE_MEM: 8,
    Opcode.SUB_MEM: 25,
}

# Допустимые диапазоны операнда B по каждой команде.
OPERAND_LIMITS = {
    opcode: (0, (1 << bits) - 1)
    for opcode, bits in _OPERAND_BITS.items()
}


@dataclass(frozen=True)
class Instruction:
    """Команда в промежуточном представлении."""

    opcode: Opcode
    operand: int

    @property
    def a_field(self) -> int:
        """Поле A — код операции (биты 0—5)."""
        return int(self.opcode)

    @property
    def b_field(self) -> int:
        """Поле B — операнд команды."""
        return self.operand