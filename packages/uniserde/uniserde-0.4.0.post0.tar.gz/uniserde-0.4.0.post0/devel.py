from __future__ import annotations


import uniserde
import uniserde.compat
from datetime import datetime, timezone
import typing as t
import dataclasses
from bson import ObjectId
import tests.models as models


class Model:
    value: t.Literal["a", "b", "c"]


serde = uniserde.BsonSerde(lazy=False)


print(serde.from_bson(Model, {"value": "a"}))

print(serde.from_bson(Model, {"value": "d"}))
