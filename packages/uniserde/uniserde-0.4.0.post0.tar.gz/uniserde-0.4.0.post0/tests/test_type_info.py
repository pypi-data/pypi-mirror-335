import typing as t
import uuid
from datetime import datetime, timedelta

import pytest

from uniserde import ObjectId
from uniserde.type_hint import TypeHint

UNPARSED_VALID_TYPE_HINTS = (
    (bool, "bool", bool, ()),
    (int, "int", int, ()),
    (float, "float", float, ()),
    (str, "str", str, ()),
    (tuple[int], "tuple[int]", tuple, (int,)),
    (list[str], "list[str]", list, (str,)),
    (set[float], "set[float]", set, (float,)),
    (dict[str, int], "dict[str, int]", dict, (str, int)),
    (t.Optional[str], "t.Optional[str]", t.Optional, (str,)),
    (t.Union[str, None], "t.Union[str, None]", t.Optional, (str,)),
    (t.Union[None, str], "t.Union[None, str]", t.Optional, (str,)),
    (datetime, "datetime", datetime, ()),
    (timedelta, "timedelta", timedelta, ()),
    (ObjectId, "ObjectId", ObjectId, ()),
    (uuid.UUID, "uuid.UUID", uuid.UUID, ()),
)

UNPARSED_INVALID_TYPE_HINTS = (
    None,
    type(None),
    t.Optional,
    list,
    set,
    dict,
    dict[int],  # type: ignore  (intentional error for testing)
    t.Union,
    t.Union[int, str],
)


@pytest.mark.parametrize(
    "raw_type_hint, _, expected_origin, expected_args",
    UNPARSED_VALID_TYPE_HINTS,
)
def test_instantiate_parsed_type_hint(
    raw_type_hint: t.Type,
    _: str,
    expected_origin: t.Type,
    expected_args: tuple[t.Type, ...],
) -> None:
    """
    Instantiates a `TypeHint` object and checks the origin and args.
    """
    # Construct the `TypeHint` object
    type_hint_object = TypeHint(raw_type_hint)

    # Check the origin
    assert type_hint_object.origin is expected_origin

    # Check the args
    assert len(type_hint_object.args) == len(expected_args)

    for arg_should, arg_is in zip(expected_args, type_hint_object.args):
        assert arg_should is arg_is.origin


@pytest.mark.parametrize(
    "_, raw_type_hint, expected_origin, expected_args",
    UNPARSED_VALID_TYPE_HINTS,
)
def test_instantiate_string_type_hint(
    _: t.Type,
    raw_type_hint: str,
    expected_origin: t.Type,
    expected_args: tuple[t.Type, ...],
) -> None:
    """
    Instantiates a `TypeHint` object from a string and checks the origin and
    args.
    """
    # Construct the `TypeHint` object. Note that the hint is converted to a
    # string first.
    type_hint_object = TypeHint(
        raw_type_hint,
        scope=globals(),
    )

    # Check the origin
    assert type_hint_object.origin is expected_origin

    # Check the args
    assert len(type_hint_object.args) == len(expected_args)

    for arg_should, arg_is in zip(expected_args, type_hint_object.args):
        assert arg_should is arg_is.origin


@pytest.mark.parametrize(
    "raw_type_hint",
    UNPARSED_INVALID_TYPE_HINTS,
)
def test_instantiate_invalid_type_hint(
    raw_type_hint: t.Type,
) -> None:
    """
    Instantiates a `TypeHint` object from an invalid type hint and checks that
    a `TypeError` is raised.
    """
    with pytest.raises(TypeError):
        TypeHint(raw_type_hint)
