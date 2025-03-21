from collections.abc import Sequence, Iterator
from os import PathLike
from pathlib import Path

import polars as pl

from matchescu.typing import Trait

from matchescu.data import Record


class CsvDataSource:
    def __init__(
        self,
        file_path: str | PathLike,
        traits: Sequence[Trait],
        has_header: bool = True,
    ):
        file_path = Path(file_path)
        self.name = file_path.name.replace(file_path.suffix, "")
        self.traits = traits

        self.__file_path = file_path
        self.__df: pl.DataFrame | None = None
        self.__header = has_header

    def read(self) -> "CsvDataSource":
        self.__df = pl.read_csv(
            self.__file_path, ignore_errors=True, has_header=self.__header
        )
        return self

    def __iter__(self) -> Iterator[Record]:
        if self.__df is None:
            return iter([])
        return iter(map(Record, self.__df.iter_rows(named=True)))

    def __len__(self) -> int:
        return self.__df.shape[0] if self.__df is not None else 0
