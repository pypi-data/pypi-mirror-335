from typing import Protocol, Iterable, Sized

from matchescu.typing import EntityReference


class BinaryComparisonSpace(Iterable, Sized, Protocol):
    def put(self, left: EntityReference, right: EntityReference) -> None:
        pass
