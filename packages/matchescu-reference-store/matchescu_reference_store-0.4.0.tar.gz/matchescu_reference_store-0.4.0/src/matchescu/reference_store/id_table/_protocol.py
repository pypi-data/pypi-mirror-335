from collections.abc import Iterable
from typing import Protocol, Sized

from matchescu.typing import EntityReferenceIdentifier, EntityReference


class IdTable(Iterable, Sized, Protocol):
    def get(self, ref_id: EntityReferenceIdentifier) -> EntityReference:
        pass

    def get_by_source(self, source: str) -> Iterable[EntityReference]:
        pass

    def put(self, ref: EntityReference) -> None:
        pass
