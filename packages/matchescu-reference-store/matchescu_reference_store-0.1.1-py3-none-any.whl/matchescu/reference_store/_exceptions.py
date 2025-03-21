from matchescu.typing import EntityReferenceIdentifier


class EntityReferenceNotFound(Exception):
    def __init__(self, identifier: EntityReferenceIdentifier) -> None:
        super().__init__(
            f"Entity reference with label '{identifier.label}' from source '{identifier.source}' not found"
        )
