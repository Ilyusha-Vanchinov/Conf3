"""CLI-ассемблер УВМ: разбор текста в промежуточное представление."""

import argparse
from pathlib import Path

from src.isa import OPERAND_LIMITS, Instruction, Opcode


MNEMONICS = {
    "load_const": Opcode.LOAD_CONST,
    "load_mem": Opcode.LOAD_MEM,
    "store_mem": Opcode.STORE_MEM,
    "sub_mem": Opcode.SUB_MEM,
}

COMMENT_CHAR = ";"
EXPECTED_PARTS = 2


def parse_line(line: str, line_no: int) -> Instruction | None:
    """Разбирает строку; None для пустой строки или комментария."""
    text = line.split(COMMENT_CHAR, 1)[0].strip()
    if not text:
        return None

    parts = text.split()
    if len(parts) != EXPECTED_PARTS:
        msg = f"line {line_no}: expected mnemonic and operand"
        raise ValueError(msg)

    mnemonic = parts[0].lower()
    if mnemonic not in MNEMONICS:
        msg = f"line {line_no}: unknown mnemonic {mnemonic!r}"
        raise ValueError(msg)

    try:
        operand = int(parts[1], 0)
    except ValueError as exc:
        msg = f"line {line_no}: operand is not a number"
        raise ValueError(msg) from exc

    opcode = MNEMONICS[mnemonic]
    low, high = OPERAND_LIMITS[opcode]
    if not low <= operand <= high:
        msg = (
            f"line {line_no}: operand {operand} "
            f"out of range [{low}, {high}]"
        )
        raise ValueError(msg)

    return Instruction(opcode, operand)


def parse_file(path: Path) -> list[Instruction]:
    """Читает .asm и возвращает список инструкций."""
    program: list[Instruction] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), 1):
        instr = parse_line(line, line_no)
        if instr is not None:
            program.append(instr)
    return program


def format_instruction(instr: Instruction) -> str:
    """Форматирует команду для режима --test."""
    return (
        f"{instr.opcode.name}: "
        f"A={instr.a_field}, B={instr.b_field}"
    )


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="UVM assembler")
    parser.add_argument("source", type=Path, help="source .asm file")
    parser.add_argument(
        "binary",
        type=Path,
        help="output .bin (used on stage 2)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="print intermediate representation",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    args = build_parser().parse_args(argv)
    program = parse_file(args.source)

    if args.test:
        for instr in program:
            print(format_instruction(instr))

    # Этап 1: бинарный файл пока не формируется.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())