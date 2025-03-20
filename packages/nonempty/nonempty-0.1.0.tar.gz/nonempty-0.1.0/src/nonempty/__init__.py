"""NonEmpty - lists with at least one element."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import total_ordering
from typing import (
    TYPE_CHECKING,
    Generic,
    Self,
    SupportsIndex,
    TypeVar,
    overload,
)

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

T = TypeVar("T")


@total_ordering
class NonEmpty(Generic[T]):
    """Mutable non-empyt lists."""

    __slots__ = "_items"
    __match_args__ = ("head", "tail")

    def __init__(self, first: T, *rest: T) -> None:
        """Create a new non-empty list."""
        self._items = [first]
        self._items += rest

    @property
    def head(self) -> T:
        """Return the first element."""
        return self._items[0]

    @property
    def tail(self) -> list[T]:
        """Return"""
        return self._items[1:]

    def append(self, object: T, /) -> None:
        """Append object to the end of the list."""
        self._items.append(object)

    def copy(self) -> Self:
        """Return a shallow copy of the list."""
        return self.__class__(*self._items.copy())

    def count(self, value: T, /) -> int:
        """Return number of occurrences of value."""
        return self._items.count(value)

    def extend(self, iterable: Iterable[T], /) -> None:
        """Extend non-empty list by appending elements from the iterable."""
        self._items.extend(iterable)

    def index(self, value: T, start: int = 0, stop: int = 2**63, /) -> int:
        """Return first index of value.

        Raises ValueError if the value is not present.
        """
        return self._items.index(value, start, stop)

    def insert(self, index: int, object: T, /) -> None:
        """Insert object before index."""
        self._items.insert(index, object)

    def pop(self, index: int = -1, /) -> T | None:
        """Remove and return item at index (default last)."""
        if len(self._items) != 1:
            return self._items.pop(index)
        raise ValueError("NonEmpty.pop(x): the last value cannot be removed")

    def remove(self, value: T, /) -> None:
        """Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        if len(self._items) == 1 and value == self._items[0]:
            raise ValueError("NonEmpty.remove(x): the last value cannot be removed")
        self._items.remove(value)

    def reverse(self) -> None:
        """Reverse *IN PLACE*."""
        self._items.reverse()

    @overload
    def sort(
        self,
        *,
        key: None = None,
        reverse: bool = False,
    ) -> None: ...

    @overload
    def sort(
        self,
        *,
        key: Callable[[T], SupportsRichComparison],
        reverse: bool = False,
    ) -> None: ...

    def sort(
        self,
        *,
        key: Callable[[T], SupportsRichComparison] | None = None,
        reverse: bool = False,
    ) -> None:
        """Sort the list in ascending order and return None.

        The sort is in-place (i.e. the list itself is modified) and stable (i.e. the
        order of two equal elements is maintained).

        If a key function is given, apply it once to each list item and sort them,
        ascending or descending, according to their function values.

        The reverse flag can be set to sort in descending order.
        """
        self._items.sort(key=key, reverse=reverse)  # pyright: ignore[reportArgumentType]

    def __len__(self) -> int:
        """Return len(self)."""
        return len(self._items)

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"{self.__class__.__name__}({', '.join(repr(x) for x in self._items)})"

    def __contains__(self, key: T, /) -> bool:
        """Return bool(key in self)."""
        return key in self._items

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> T: ...

    @overload
    def __getitem__(self, index: slice, /) -> list[T]: ...

    def __getitem__(self, index: SupportsIndex | slice, /) -> T | list[T]:
        """Return self[index]."""
        return self._items[index]

    def __setitem__(self, key: SupportsIndex, value: T, /) -> None:
        """Set self[key] to value."""
        self._items[key] = value

    def __delitem__(self, key: SupportsIndex, /) -> None:
        """Delete self[key]."""
        if len(self._items) == 1:
            raise ValueError(
                "NonEmpty.__delitem__(x): the last value cannot be removed"
            )
        self._items.__delitem__(key)

    def __reversed__(self) -> Iterator[T]:
        """Return a reverse iterator over the list."""
        return self._items.__reversed__()

    def __add__(self, value: Self, /) -> Self:
        """Return self+value."""
        self._items.__add__(value._items)
        return self

    def __iadd__(self, value: Self, /) -> Self:
        """Implement self+=value."""
        self._items.__iadd__(value._items)
        return self

    def __mul__(self, value: SupportsIndex, /) -> Self:
        """Return self*value."""
        items = self._items * value
        if len(items) == 0:
            raise ValueError("can't multiply NonEmpty by values smaller than '1'")
        self._items = items
        return self

    def __rmul__(self, value: SupportsIndex, /) -> Self:
        """Return value*self."""
        return self.__mul__(value)

    def __imul__(self, value: SupportsIndex, /) -> Self:
        """Implement self*=value."""
        return self.__mul__(value)

    def __eq__(self, value: object, /) -> bool:
        """Return self==value."""
        return isinstance(value, NonEmpty) and self._items == value._items

    def __lt__(self, value: object, /) -> bool:
        """Return self<value."""
        return (
            self._items < value._items
            if isinstance(value, NonEmpty)
            else NotImplemented
        )

    def __iter__(self) -> Iterator[T]:
        """Implement iter(self)."""
        yield from self._items
