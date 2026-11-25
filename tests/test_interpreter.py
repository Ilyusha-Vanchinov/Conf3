"""Тесты интерпретатора (этап 3)."""

import json
from pathlib import Path

import pytest

from src.assembler import assemble, parse_file
from src.interpreter import VirtualMachine, dump_memory


EXAMPLES = (
    Path(__file__).resolve().parent.parent / "examples"
)


def test_copy_array() -> None:
    """Копирование массива 100..105 -> 200..205."""
    program = assemble(parse_file(EXAMPLES / "copy_array.asm"))
    vm = VirtualMachine()
    vm.load_program(program)
    vm.run()
    expected = [10, 20, 30, 40, 50, 60]
    src = [vm.memory[a] for a in range(100, 106)]
    dst = [vm.memory[a] for a in range(200, 206)]
    assert src == expected
    assert dst == expected


def test_dump_range() -> None:
    """Дамп содержит только указанный диапазон."""
    vm = VirtualMachine()
    vm.memory[100] = 42
    vm.memory[101] = 43
    vm.memory[102] = 44
    dump = dump_memory(vm, 100, 103)
    assert dump["start"] == 100
    assert dump["end"] == 103
    assert dump["memory"] == {"100": 42, "101": 43, "102": 44}


def test_dump_invalid_range() -> None:
    """Некорректный диапазон вызывает ошибку."""
    vm = VirtualMachine()
    with pytest.raises(ValueError):
        dump_memory(vm, 10, 5)


def test_load_program_misaligned() -> None:
    """Размер программы должен быть кратен 4."""
    vm = VirtualMachine()
    with pytest.raises(ValueError):
        vm.load_program(b"\x00\x01\x02")


def test_load_program_too_large() -> None:
    """Программа не помещается в память."""
    vm = VirtualMachine(memory_size=4)
    with pytest.raises(ValueError):
        vm.load_program(b"\x00" * 32)


def test_load_const_and_store() -> None:
    """load_const + store_mem пишут в память."""
    program = assemble(
        parse_file(EXAMPLES / "copy_array.asm")
    )
    vm = VirtualMachine()
    vm.load_program(program)
    vm.run()
    assert vm.memory[200] == 10


def test_json_serialization(tmp_path: Path) -> None:
    """Дамп сериализуется в JSON и обратно без потерь."""
    vm = VirtualMachine()
    vm.memory[10] = 7
    dump = dump_memory(vm, 10, 11)
    out = tmp_path / "dump.json"
    out.write_text(
        json.dumps(dump, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["memory"] == {"10": 7}
    assert loaded["start"] == 10
    assert loaded["end"] == 11