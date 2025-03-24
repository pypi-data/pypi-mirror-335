from collections.abc import Mapping
from typing import Any, _TypedDictMeta  # type: ignore[attr-defined]

from pydantic import TypeAdapter, ValidationError


def is_instance_typeddict(val: Mapping[str, Any], type_: _TypedDictMeta) -> bool:
    adapter = TypeAdapter(type_)
    try:
        adapter.validate_python(val)
        return True
    except ValidationError:
        return False
