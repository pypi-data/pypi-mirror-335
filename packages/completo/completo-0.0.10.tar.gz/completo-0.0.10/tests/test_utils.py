from typing import TypedDict

from completo.util import is_instance_typeddict


def test_is_instance_typeddict() -> None:
    class A(TypedDict):
        a: int

    assert is_instance_typeddict({"a": 1}, A)
    assert not is_instance_typeddict({"b": 1}, A)
