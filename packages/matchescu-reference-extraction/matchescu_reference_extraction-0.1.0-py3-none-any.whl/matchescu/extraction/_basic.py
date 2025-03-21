from typing import Iterable
from matchescu.data import EntityReferenceExtraction

from matchescu.data_sources._record import Record


class EntityReferenceExtractionFromRecords(EntityReferenceExtraction[Record]):
    def _merge_records(self, records: Iterable[Record]) -> Record:
        return Record.merge(records)
