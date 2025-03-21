from __future__ import annotations

import dataclasses
import inspect
import sys
import typing as t

from .type_hint import TypeHint

__all__ = [
    "as_child",
    "get_class_attributes_recursive",
]


T = t.TypeVar("T")


# Caches results of the `get_type_key` function to speed up lookups.
TYPE_KEY_CACHE: dict[t.Type, t.Type] = {}


def as_child(cls: t.Type[T]) -> t.Type[T]:
    """
    Marks the class to be serialized as one of its children. This will add an
    additional "type" field in the result, so the child can be deserialized
    properly.

    This decorator applies to children of the class as well, i.e. they will also
    be serialized with the "type" field.
    """
    assert inspect.isclass(cls), cls
    cls._uniserde_serialize_as_child_ = cls  # type: ignore
    return cls


def root_of_serialize_as_child(cls: t.Type) -> t.Type | None:
    """
    If the given class, or any of its parents, is marked to be serialized
    `@as_child`, returns the class that was marked. Otherwise, returns `None`.
    """
    assert inspect.isclass(cls), cls
    try:
        return cls._uniserde_serialize_as_child_  # type: ignore
    except AttributeError:
        return None


def all_subclasses(cls: t.Type, include_class: bool) -> t.Iterable[t.Type]:
    """
    Yields all classes directly or indirectly inheriting from `cls`. Does not
    perform any sort of cycle checks. If `include_class` is `True`, the class
    itself is also yielded.
    """

    if include_class:
        yield cls

    for subclass in cls.__subclasses__():
        yield from all_subclasses(subclass, True)


def _get_class_attributes_local(
    cls: t.Type,
    result: dict[str, TypeHint],
) -> None:
    """
    Gets all annotated attributes in the given class, without considering any
    parent classes. Applies the same rules as `get_class_attributes_recursive`.

    Instead of returning a result, the attributes are added to the given
    dictionary. If the dictionary already contains an attribute, it is not
    overwritten.
    """
    assert inspect.isclass(cls), cls

    # Get all annotated attributes
    try:
        annotations = cls.__annotations__
    except AttributeError:
        return

    if not isinstance(annotations, dict):
        return

    # Process them individually
    global_ns = sys.modules[cls.__module__].__dict__
    local_ns = vars(cls)

    for name, hint in annotations.items():
        # Because we're going in method resolution order, any previous
        # definitions win
        if name in result:
            continue

        # Resolve string annotations
        if isinstance(hint, str):
            try:
                hint = eval(hint, global_ns, local_ns)
            except NameError:
                raise ValueError(
                    f"Could not resolve string annotation `{hint}` in {cls.__name__}.{name}. Are you missing an import?"
                )

        assert not isinstance(hint, str), repr(hint)

        # By convention, `dataclasses.KW_ONLY` is used as though it were a
        # type hint, but it's not actually valid for that.
        if hint is dataclasses.KW_ONLY:
            continue

        # Store the result
        result[name] = TypeHint(hint)


def get_class_attributes_recursive(cls: t.Type) -> dict[str, TypeHint]:
    """
    Returns the names and types of all attributes in the given class, including
    inherited ones. Attributes are determined from type hints, with some custom
    logic applied:

    - fields annotated with `dataclasses.KW_ONLY` are silently dropped

    - New-style unions are converted to old-style (`types.UnionType` ->
      `t.Union`).
    """
    assert inspect.isclass(cls), cls

    result: dict[str, TypeHint] = {}

    for subcls in cls.__mro__:
        _get_class_attributes_local(subcls, result)

    return result
