"""Тесты ассемблера (этап 1)."""

from pathlib import Path

import pytest

from src.assembler import format_instruction, parse_file, parse_line
from src.isa import Instruction, Opcode


SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "spec_tests.asm"
)


def test_parse_spec_program() -> None:
    """Разбор тестовой программы из спецификации."""
    program = parse_file(SPEC_PATH)
    assert program == [
        Instruction(Opcode.LOAD_CONST, 463),
        Instruction(Opcode.LOAD_MEM, 1002),
        Instruction(Opcode.STORE_MEM, 122),
        Instruction(Opcode.SUB_MEM, 993),
    ]


def test_format_fields() -> None:
    """Формат вывода полей A и B."""
    instr = Instruction(Opcode.LOAD_CONST, 463)
    assert format_instruction(instr) == "LOAD_CONST: A=41, B=463"


def test_operand_out_of_range() -> None:
    """Контроль диапазона операнда."""
    with pytest.raises(ValueError):
        parse_line("load_const 8192", 1)


def test_comment_and_blank() -> None:
    """Комментарии и пустые строки игнорируются."""
    assert parse_line("; comment", 1) is None
    assert parse_line("   ", 2) is None


def test_unknown_mnemonic() -> None:
    """Неизвестная мнемоника вызывает ошибку."""
    with pytest.raises(ValueError):
        parse_line("nop 0", 1)


def test_hex_operand() -> None:
    """Поддержка шестнадцатеричной записи операнда."""
    instr = parse_line("load_mem 0x3EA", 1)
    assert instr == Instruction(Opcode.LOAD_MEM, 1002)