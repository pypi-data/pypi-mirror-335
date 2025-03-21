from matchescu.data import Record
from matchescu.references import EntityReference
from matchescu.typing import EntityReferenceIdFactory


class RecordIdAdapter:
    def __init__(self, id_factory: EntityReferenceIdFactory):
        self.__id_factory = id_factory

    def __call__(self, record: Record) -> EntityReference:
        ref_id = self.__id_factory(record)
        return EntityReference(ref_id, record)
