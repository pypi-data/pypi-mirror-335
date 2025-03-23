from typing import Protocol, Iterable, Sized

from matchescu.typing import EntityReferenceIdentifier


class BinaryComparisonSpace(Iterable[EntityReferenceIdentifier], Sized, Protocol):
    def put(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> None:
        pass
