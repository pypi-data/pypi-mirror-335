from collections.abc import Iterator

from matchescu.typing import EntityReferenceIdentifier


class InMemoryComparisonSpace:
    def __init__(self):
        self.__data = {}

    def put(
        self, left_id: EntityReferenceIdentifier, right_id: EntityReferenceIdentifier
    ) -> None:
        key = (left_id, right_id)
        val = self.__data.get(key, 0)
        self.__data[key] = val + 1

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(
        self,
    ) -> Iterator[tuple[EntityReferenceIdentifier, EntityReferenceIdentifier]]:
        return iter(self.__data.keys())
