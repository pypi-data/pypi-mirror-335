from typing import Iterable, Iterator

from matchescu.typing import Trait
from matchescu.data_sources._record import Record


class ListDataSource:
    def __init__(self, name: str, traits: Iterable[Trait]):
        self.name = name
        self.traits = traits
        self._items: list[Record] = []

    def append(self, item: Record | Iterable[Record]) -> "ListDataSource":
        if isinstance(item, Iterable):
            item = Record.merge(item)
        self._items.append(item)
        return self

    def extend(
        self, items: Iterable[Record] | Iterable[Iterable[Record]]
    ) -> "ListDataSource":
        for item in items:
            self.append(item)
        return self

    def __iter__(self) -> Iterator[Record]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)
