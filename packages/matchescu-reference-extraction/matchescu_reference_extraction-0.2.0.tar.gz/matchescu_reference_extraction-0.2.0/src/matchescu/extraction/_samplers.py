from typing import Generator

from matchescu.typing import DataSource


def single_record(data_source: DataSource) -> Generator[list, None, None]:
    """Sample records one at a time from the data source."""
    yield from map(lambda x: [x], data_source)
