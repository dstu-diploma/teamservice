from collections import defaultdict
from pydantic import BaseModel
from typing import Sequence, TypeVar

T = TypeVar("T", bound=BaseModel)


def export_int_fields(
    dtos: Sequence[BaseModel], *fields: str
) -> frozenset[int]:
    acc = set()
    for dto in dtos:
        dumped = dto.model_dump()

        for field in fields:
            val: int | None = dumped.get(field, None)
            if val:
                acc.add(val)

    return frozenset(acc)


def inject_mapping(
    dtos: Sequence[T],
    mapping: defaultdict[int, str | None],
    lookup_pattern: str,
    replace_pattern: str,
    *,
    strict: bool,
) -> list[T]:
    injected_dtos: list[T] = []

    for dto in dtos:
        dumped = dto.model_dump()

        if strict:
            if dumped.get(lookup_pattern, None) is not None:
                dumped[replace_pattern] = mapping[dumped[lookup_pattern]]

            injected_dtos.append(dto.__class__(**dumped))
            continue

        dumped_immutable = dto.model_dump()
        for key in dumped_immutable:
            if lookup_pattern not in key:
                continue

            mapping_key = key.replace(lookup_pattern, replace_pattern)
            dumped[mapping_key] = mapping[dumped[key]]
        injected_dtos.append(dto.__class__(**dumped))

    return injected_dtos
