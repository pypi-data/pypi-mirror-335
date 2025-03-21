import locale

from typing import Any, Callable, Iterator, Union

from matchescu.typing import Trait
from matchescu.data_sources import Record


def _process_string(value: Any) -> str:
    return str(value)


def _process_int(value: Any) -> int:
    return int(value)


def _process_float(value: Any) -> float:
    return float(value)


def _process_currency(value: Any) -> float | None:
    if value is None:
        return None
    str_val = str(value).replace(",", "").strip()
    return locale.atof(str_val.lstrip("$"))


class RecordExtractionTrait:
    def __init__(self, mapping: Callable[[Any], Any], keys: list[int | str]) -> None:
        self.__mapping = mapping
        self.__keys = keys

    def __call__(self, input_records: list[Record]) -> Record:
        if len(input_records) == 0:
            return Record([])
        return Record(
            {key: self.__mapping(input_records[0][key]) for key in self.__keys}
        )


class Traits:
    def __init__(self):
        self._traits = []

    def string(self, keys: list[Union[int, str]]) -> "Traits":
        self._traits.append(RecordExtractionTrait(_process_string, keys))
        return self

    def int(self, keys: list[Union[int, str]]) -> "Traits":
        self._traits.append(RecordExtractionTrait(_process_int, keys))
        return self

    def float(self, keys: list[Union[int, str]]) -> "Traits":
        self._traits.append(RecordExtractionTrait(_process_float, keys))
        return self

    def currency(self, keys: list[Union[int, str]]) -> "Traits":
        self._traits.append(RecordExtractionTrait(_process_currency, keys))
        return self

    def __iter__(self) -> Iterator[Trait]:
        return iter(self._traits)
