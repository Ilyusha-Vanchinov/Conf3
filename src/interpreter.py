"""Интерпретатор УВМ: модель памяти, стек и цикл интерпретации."""

import argparse
import json
from pathlib import Path

from src.isa import INSTRUCTION_SIZE, Instruction, Opcode


DEFAULT_MEMORY_SIZE = 1 << 20


class VirtualMachine:
    """Модель памяти, стек и цикл интерпретации УВМ."""

    def __init__(self, memory_size: int = DEFAULT_MEMORY_SIZE) -> None:
        self.memory: list[int] = [0] * memory_size
        self.stack: list[int] = []
        self.pc: int = 0
        self.program_end: int = 0

    def load_program(self, program: bytes, base: int = 0) -> None:
        """Загружает бинарную программу в память по адресу base."""
        if len(program) % INSTRUCTION_SIZE != 0:
            msg = "program size is not multiple of 4 bytes"
            raise ValueError(msg)
        count = len(program) // INSTRUCTION_SIZE
        if base + count > len(self.memory):
            msg = "program does not fit into memory"
            raise ValueError(msg)
        for i in range(count):
            start = i * INSTRUCTION_SIZE
            chunk = program[start:start + INSTRUCTION_SIZE]
            self.memory[base + i] = int.from_bytes(
                chunk, byteorder="little"
            )
        self.program_end = base + count

    def fetch(self) -> Instruction:
        """Читает команду по PC и декодирует в промежуточное."""
        word = self.memory[self.pc]
        data = word.to_bytes(INSTRUCTION_SIZE, byteorder="little")
        return Instruction.decode(data)

    def execute(self, instr: Instruction) -> None:
        """Выполняет одну команду."""
        if instr.opcode == Opcode.LOAD_CONST:
            self.stack.append(instr.operand)
        elif instr.opcode == Opcode.LOAD_MEM:
            self.stack.append(self.memory[instr.operand])
        elif instr.opcode == Opcode.STORE_MEM:
            addr = self.stack.pop()
            value = self.stack.pop()
            self.memory[addr + instr.operand] = value
        else:
            msg = f"opcode {instr.opcode!r} not implemented"
            raise NotImplementedError(msg)

    def run(self) -> None:
        """Основной цикл интерпретации."""
        while self.pc < self.program_end:
            instr = self.fetch()
            self.execute(instr)
            self.pc += 1


def dump_memory(vm: VirtualMachine, start: int, end: int) -> dict:
    """Формирует JSON-совместимый дамп диапазона [start, end)."""
    if start < 0 or end > len(vm.memory) or start > end:
        msg = f"invalid dump range [{start}, {end})"
        raise ValueError(msg)
    return {
        "start": start,
        "end": end,
        "memory": {
            str(addr): vm.memory[addr]
            for addr in range(start, end)
        },
    }


def build_parser() -> argparse.ArgumentParser:
    """CLI-парсер интерпретатора."""
    parser = argparse.ArgumentParser(description="UVM interpreter")
    parser.add_argument("program", type=Path, help="binary program")
    parser.add_argument("dump", type=Path, help="output JSON dump")
    parser.add_argument(
        "start", type=int, help="start address (inclusive)"
    )
    parser.add_argument(
        "end", type=int, help="end address (exclusive)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    args = build_parser().parse_args(argv)
    program = args.program.read_bytes()
    vm = VirtualMachine()
    vm.load_program(program)
    vm.run()
    dump = dump_memory(vm, args.start, args.end)
    args.dump.write_text(
        json.dumps(dump, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Dump saved to {args.dump}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())