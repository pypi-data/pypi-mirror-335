from typing import Generator
from matchescu.typing import RecordAdapter, DataSource

from matchescu.data_sources import CsvDataSource
from matchescu.extraction._basic import EntityReferenceExtractionFromRecords


class CsvEntityReferenceExtraction(EntityReferenceExtractionFromRecords):
    def __init__(
        self,
        ds: CsvDataSource,
        record_adapter: RecordAdapter,
    ):
        super().__init__(
            ds, record_adapter, CsvEntityReferenceExtraction._sample_csv_records
        )

    @staticmethod
    def _sample_csv_records(ds: DataSource) -> Generator[list, None, None]:
        yield from map(lambda x: [x], ds)
