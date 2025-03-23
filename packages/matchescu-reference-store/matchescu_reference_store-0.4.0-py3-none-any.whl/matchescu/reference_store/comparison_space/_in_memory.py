from collections.abc import Iterator

from matchescu.typing import EntityReference, EntityReferenceIdentifier


class InMemoryComparisonSpace:
    def __init__(self):
        self.__data = {}

    def put(self, ref1: EntityReference, ref2: EntityReference) -> None:
        key = (ref1.id, ref2.id)
        val = self.__data.get(key, 0)
        self.__data[key] = val + 1

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(
        self,
    ) -> Iterator[tuple[EntityReferenceIdentifier, EntityReferenceIdentifier]]:
        return iter(self.__data.keys())
