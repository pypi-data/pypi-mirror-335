from collections.abc import Iterable

from matchescu.data import Record
from matchescu.typing import EntityReferenceIdentifier


class EntityReference(Record):
    id: EntityReferenceIdentifier

    def __init__(self, identifier: EntityReferenceIdentifier, value: Iterable):
        super().__init__(value)
        self.id = identifier
