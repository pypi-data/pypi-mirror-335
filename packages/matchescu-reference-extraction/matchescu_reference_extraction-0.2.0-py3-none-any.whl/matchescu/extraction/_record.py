from typing import Iterable
from matchescu.extraction._base import EntityReferenceExtraction

from matchescu.data import Record


class RecordExtraction(EntityReferenceExtraction[Record]):
    def _merge_records(self, records: Iterable[Record]) -> Record:
        return Record.merge(records)
