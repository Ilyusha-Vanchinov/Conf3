"""Описание системы команд УВМ (вариант 6)."""

from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """Коды операций учебной виртуальной машины."""

    LOAD_CONST = 41
    LOAD_MEM = 25
    STORE_MEM = 49
    SUB_MEM = 30


INSTRUCTION_SIZE = 4
OPCODE_BITS = 6
OPCODE_MASK = (1 << OPCODE_BITS) - 1

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

    def encode(self) -> bytes:
        """Кодирует команду в 4 байта (little-endian)."""
        low, high = OPERAND_LIMITS[self.opcode]
        if not low <= self.operand <= high:
            msg = (
                f"operand {self.operand} "
                f"out of range [{low}, {high}]"
            )
            raise ValueError(msg)
        word = (self.operand << OPCODE_BITS) | self.a_field
        return word.to_bytes(INSTRUCTION_SIZE, byteorder="little")

    @classmethod
    def decode(cls, data: bytes) -> "Instruction":
        """Декодирует 4 байта в инструкцию."""
        if len(data) != INSTRUCTION_SIZE:
            msg = (
                f"expected {INSTRUCTION_SIZE} bytes, "
                f"got {len(data)}"
            )
            raise ValueError(msg)
        word = int.from_bytes(data, byteorder="little")
        opcode = Opcode(word & OPCODE_MASK)
        operand = word >> OPCODE_BITS
        low, high = OPERAND_LIMITS[opcode]
        if not low <= operand <= high:
            msg = (
                f"operand {operand} "
                f"out of range [{low}, {high}]"
            )
            raise ValueError(msg)
        return cls(opcode, operand)