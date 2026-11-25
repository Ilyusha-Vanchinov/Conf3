"""Тесты ассемблера (этапы 1—2)."""

from pathlib import Path

import pytest

from src.assembler import assemble, parse_file, parse_line
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


def test_a_b_fields() -> None:
    """Свойства a_field и b_field."""
    instr = Instruction(Opcode.LOAD_CONST, 463)
    assert instr.a_field == 41
    assert instr.b_field == 463


def test_operand_out_of_range() -> None:
    """Контроль диапазона операнда при парсинге."""
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


@pytest.mark.parametrize(
    ("opcode", "operand", "expected"),
    [
        (Opcode.LOAD_CONST, 463, b"\xE9\x73\x00\x00"),
        (Opcode.LOAD_MEM, 1002, b"\x99\xFA\x00\x00"),
        (Opcode.STORE_MEM, 122, b"\xB1\x1E\x00\x00"),
        (Opcode.SUB_MEM, 993, b"\x5E\xF8\x00\x00"),
    ],
)
def test_encode(
    opcode: Opcode, operand: int, expected: bytes
) -> None:
    """Кодирование совпадает с тестами из спецификации."""
    assert Instruction(opcode, operand).encode() == expected


def test_decode_roundtrip() -> None:
    """decode(encode(x)) == x."""
    for opcode, operand in [
        (Opcode.LOAD_CONST, 463),
        (Opcode.LOAD_MEM, 1002),
        (Opcode.STORE_MEM, 122),
        (Opcode.SUB_MEM, 993),
    ]:
        instr = Instruction(opcode, operand)
        assert Instruction.decode(instr.encode()) == instr


def test_assemble_spec_program() -> None:
    """Сборка spec_tests.asm воспроизводит все тестовые байты."""
    program = parse_file(SPEC_PATH)
    expected = (
        b"\xE9\x73\x00\x00"
        b"\x99\xFA\x00\x00"
        b"\xB1\x1E\x00\x00"
        b"\x5E\xF8\x00\x00"
    )
    assert assemble(program) == expected