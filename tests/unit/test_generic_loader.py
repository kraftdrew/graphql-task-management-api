"""Unit tests for generic DataLoader batching and alignment."""

import asyncio
from asyncio import Lock
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID, uuid4

from task_api.presentation.graphql.loaders.generic_loader import create_loader


@dataclass(frozen=True)
class Record:
    """Minimal UUID-keyed value returned by the fake batch function."""

    id: UUID


async def test_loader_batches_caches_and_aligns_results() -> None:
    """Batch unique keys and restore database results to request order."""

    first = Record(uuid4())
    second = Record(uuid4())
    missing_id = uuid4()
    calls: list[list[UUID]] = []

    async def load_many(keys: Sequence[UUID]) -> Sequence[Record]:
        calls.append(list(keys))
        # Deliberately return database rows in a different order.
        return [first, second]

    loader = create_loader(load_many, lambda record: record.id, Lock())
    results = await asyncio.gather(
        loader.load(second.id),
        loader.load(missing_id),
        loader.load(first.id),
        loader.load(second.id),
    )

    assert results[0] == second
    assert results[1] is None
    assert results[2] == first
    assert results[3] == second
    assert calls == [[second.id, missing_id, first.id]]
