"""CLI-ассемблер УВМ: текст -> промежуточное -> машинное."""

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


def assemble(program: list[Instruction]) -> bytes:
    """Переводит список инструкций в машинный код."""
    return b"".join(instr.encode() for instr in program)


def format_bytes(data: bytes) -> str:
    """Форматирует байты как в тестах: 0xE9, 0x73."""
    return ", ".join(f"0x{byte:02X}" for byte in data)


def print_test_output(program: list[Instruction]) -> None:
    """Печатает результат ассемблирования в формате тестов."""
    reverse = {opcode: name for name, opcode in MNEMONICS.items()}
    for instr in program:
        name = reverse[instr.opcode]
        fields = f"A={instr.a_field}, B={instr.b_field}"
        bytes_repr = format_bytes(instr.encode())
        print(f"{name} {instr.operand} ({fields}): {bytes_repr}")


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="UVM assembler")
    parser.add_argument("source", type=Path, help="source .asm file")
    parser.add_argument(
        "binary",
        type=Path,
        help="output .bin (machine code)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="print bytes of each instruction",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    args = build_parser().parse_args(argv)
    program = parse_file(args.source)
    machine_code = assemble(program)

    args.binary.write_bytes(machine_code)
    print(f"Binary size: {len(machine_code)} bytes")

    if args.test:
        print_test_output(program)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())