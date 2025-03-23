# Copyright (C) 2022-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import overload
from typing import Any
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import SupportsIndex
from typing import TypeVar

import pydantic
from datasets import load_dataset # type: ignore
from datasets import Dataset as BaseDataset # type: ignore
from datasets import Features
from datasets import Sequence
from datasets import Value


M = TypeVar('M', bound=pydantic.BaseModel)
T = TypeVar('T')
Self = TypeVar('Self', bound='Dataset[Any]')


class Dataset(Generic[T]):
    name: str | None = None
    dataset: BaseDataset

    @classmethod
    def load(cls, split: str, name: str | None = None):
        name = name or cls.name
        if name is None:
            raise TypeError("The `name` parameter is required.")
        return cls(name, load_dataset(name, split=split)) # type: ignore

    @classmethod
    def create(cls: type[Self], name: str, split: str) -> Self:
        columns = cls.column_values()
        features = Features(columns) # type: ignore
        rows: dict[str, list[Any]] = {k: [] for k in columns.keys()}
        return cls(name=name, dataset=BaseDataset.from_dict(rows, features, split=split)) # type: ignore

    @classmethod
    def features(cls) -> Features:
        return Features(cls.column_values())

    @classmethod
    def column_values(cls) -> dict[str, Sequence | Value]:
        raise NotImplementedError

    def __init__(self, name: str, dataset: BaseDataset): # type: ignore
        self.dataset = dataset # type: ignore
        self.name = name

    def append(self, row: dict[str, Any]):
        self.dataset = self.dataset.add_item(row) # type: ignore

    def filter(
        self: Self,
        function: Callable[[T], bool]
    ) -> Self:
        return Dataset(self.dataset.filter(function))  # type: ignore

    def objects(self, model: type[M]) -> Iterable[M]:
        for row in self.dataset: # type: ignore
            yield model.model_validate(row)

    def sort(self, column: str):
        self.dataset = self.dataset.sort(column)
        return self

    def model_validate(self, model: type[M]) -> list[M]:
        return [model.model_validate(row) for row in self.dataset]  # type: ignore

    def push(self):
        assert self.name is not None
        self.dataset.push_to_hub(self.name)

    def select(
        self: Self,
        indices: Iterable[int],
        keep_in_memory: bool = False,
        indices_cache_file_name: str | None = None,
        writer_batch_size: int | None = 1000,
        new_fingerprint: str | None = None,
    ) -> Self:
        return type(self)(self.name, self.dataset.select( # type: ignore
            indices,
            keep_in_memory=keep_in_memory,
            indices_cache_file_name=indices_cache_file_name,
            writer_batch_size=writer_batch_size,
            new_fingerprint=new_fingerprint
        ))

    @overload
    def __getitem__(self, i: slice, /) -> list[T]:
        ...

    @overload
    def __getitem__(self, i: SupportsIndex, /) -> T:
        ...

    def __getitem__(self, i: SupportsIndex | slice, /) -> list[T] | T:
        return self.dataset[i]  # type: ignore