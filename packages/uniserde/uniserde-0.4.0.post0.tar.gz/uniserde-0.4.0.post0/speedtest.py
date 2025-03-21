import copy
import timeit
import uniserde.lazy_wrapper
from dataclasses import dataclass
from datetime import datetime, timezone
import typing as t

import uniserde


@dataclass
class SubModel:
    id: str
    timestamp: datetime
    reference_to_other_instance: str
    amount: int
    description: str
    events: list[str]


@dataclass
class Model:
    name: str
    subs: list[SubModel]
    sets: set[str]
    timestamp: datetime
    deleted: bool
    duration: float


RAW = {
    "name": "test",
    "subs": [
        {
            "id": "1",
            "timestamp": "2020-01-01T00:00:00Z",
            "referenceToOtherInstance": "2",
            "amount": 100,
            "description": "test",
            "events": ["a", "b", "c"],
        },
        {
            "id": "2",
            "timestamp": "2020-01-01T00:00:00Z",
            "referenceToOtherInstance": "1",
            "amount": 200,
            "description": "test",
            "events": ["a", "b", "c"],
        },
    ],
    "sets": ["a", "b", "c"],
    "timestamp": "2020-01-01T00:00:00Z",
    "deleted": False,
    "duration": 1.0,
}


@dataclass
@uniserde.as_child
class ParentClass(uniserde.Serde):
    parent_int: int
    parent_float: float

    @classmethod
    def create_parent_variant_1(cls) -> "ParentClass":
        return cls(
            parent_int=1,
            parent_float=1.0,
        )


@dataclass
class ChildClass(ParentClass):
    child_float: float
    child_str: str

    @classmethod
    def create_child_variant_1(cls) -> "ChildClass":
        return cls(
            parent_int=1,
            parent_float=1.0,
            child_float=1.0,
            child_str="this is a string",
        )


def main() -> None:
    as_json = ChildClass.create_child_variant_1().as_json()
    uniserde.from_json(ChildClass, as_json)

    number = 10000

    try:
        serde = uniserde.JsonSerde(
            lazy=True,
        )
    except AttributeError:

        def deserialize_lazy() -> None:
            uniserde.from_json(Model, RAW)
    else:

        def deserialize_lazy() -> None:
            uniserde.from_json(Model, RAW, ctx=serde)

    print(
        "deepcopy",
        timeit.timeit(
            lambda: copy.deepcopy(RAW),
            number=number,
        ),
    )

    print(
        "uniserde eager",
        timeit.timeit(
            lambda: uniserde.from_json(copy.deepcopy(RAW), Model),
            number=number,
        ),
    )

    print(
        "uniserde lazy",
        timeit.timeit(
            deserialize_lazy,
            number=number,
        ),
    )


if __name__ == "__main__":
    main()
