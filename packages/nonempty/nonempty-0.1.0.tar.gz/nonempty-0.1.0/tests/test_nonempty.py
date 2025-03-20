import sys

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nonempty import NonEmpty

NonEmptyList = st.lists(st.integers(), min_size=1)


def test_init_missing_argument() -> None:
    with pytest.raises(
        TypeError,
        match=r"NonEmpty\.__init__\(\) missing 1 required positional argument: 'first'",
    ):
        NonEmpty()  # pyright: ignore[reportCallIssue]


@given(NonEmptyList)
def test_init(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    assert ys._items == xs


@given(NonEmptyList, st.integers())
def test_append_singleton(xs: list[int], x: int) -> None:
    ys = NonEmpty(*xs)
    ys.append(x)
    assert list(ys) == xs + [x]


@given(NonEmptyList)
def test_copy(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    zs = ys.copy()
    assert ys is not zs and ys == zs


@given(NonEmptyList, st.integers())
def test_count(xs: list[int], x: int) -> None:
    assert NonEmpty(*xs).count(x) == xs.count(x)


@given(NonEmptyList, st.lists(st.integers()))
def test_extend(xs: list[int], ys: list[int]) -> None:
    zs = NonEmpty(*xs)
    zs.extend(ys)
    xs.extend(ys)
    assert list(zs) == xs


@given(NonEmptyList, st.integers(), st.integers(), st.integers())
def test_index(xs: list[int], value: int, start: int, stop: int) -> None:
    try:
        xs.index(value, start, stop)
    except ValueError:
        with pytest.raises(ValueError, match=f"{value} is not in list"):
            NonEmpty(*xs).index(value, start, stop)
    else:
        assert NonEmpty(*xs).index(value, start, stop) == xs.index(value, start, stop)


@given(
    NonEmptyList,
    st.integers(min_value=-sys.maxsize, max_value=sys.maxsize),
    st.integers(),
)
def test_insert(xs: list[int], index: int, value: int) -> None:
    ys = NonEmpty(*xs)
    ys.insert(index, value)
    xs.insert(index, value)
    assert ys.index(value) == xs.index(value)


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=sys.maxsize))
def test_pop(xs: list[int], index: int) -> None:
    ys = NonEmpty(*xs)
    if len(ys) == 1:
        with pytest.raises(
            ValueError, match=r"NonEmpty\.pop\(x\): the last value cannot be removed"
        ):
            ys.pop(index)
    else:
        if -len(xs) <= index < len(xs):
            assert ys.pop(index) == xs.pop(index)
        else:
            with pytest.raises(IndexError, match="pop index out of range"):
                ys.pop(index)


@given(NonEmptyList, st.integers())
def test_remove(xs: list[int], value: int) -> None:
    ys = NonEmpty(*xs)
    if len(xs) == 1 and value in xs:
        with pytest.raises(
            ValueError, match=r"NonEmpty\.remove\(x\): the last value cannot be removed"
        ):
            ys.remove(value)
    elif value in xs:
        ys.remove(value)
        xs.remove(value)
        assert list(ys) == xs
    else:
        with pytest.raises(ValueError, match=r"list\.remove\(x\): x not in list"):
            ys.remove(value)


@given(NonEmptyList)
def test_sort(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    ys.sort()
    xs.sort()
    assert list(ys) == xs


@given(NonEmptyList)
def test_sort_reverse(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    ys.sort(reverse=True)
    xs.sort(reverse=True)
    assert list(ys) == xs


@given(NonEmptyList)
def test_sort_key(xs: list[int]) -> None:
    def neg_str(x: int) -> str:
        return str(-x)

    ys = NonEmpty(*xs)
    ys.sort(key=neg_str)
    xs.sort(key=neg_str)
    assert list(ys) == xs


@given(NonEmptyList)
def test_len(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    assert len(ys) == len(xs)


@given(NonEmptyList)
def test_repr(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    assert repr(ys) == f"NonEmpty({', '.join(map(str, xs))})"


@given(NonEmptyList, st.integers())
def test_contains(xs: list[int], value: int) -> None:
    ys = NonEmpty(*xs)
    assert (value in ys) == (value in xs)


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=sys.maxsize))
def test_getitem(xs: list[int], index: int) -> None:
    ys = NonEmpty(*xs)
    if -len(ys) <= index < len(ys):
        assert ys[index] == xs[index]
    else:
        with pytest.raises(IndexError, match="list index out of range"):
            ys[index]


@given(
    NonEmptyList,
    st.integers(min_value=-sys.maxsize),
    st.integers(max_value=sys.maxsize),
)
def test_get_item_slice(xs: list[int], i: int, j: int) -> None:
    ys = NonEmpty(*xs)
    assert ys[i:j] == xs[i:j]


@given(
    NonEmptyList,
    st.integers(min_value=-sys.maxsize, max_value=sys.maxsize),
    st.integers(),
)
def test_setitem(xs: list[int], index: int, value: int) -> None:
    ys = NonEmpty(*xs)
    if -len(ys) <= index < len(ys):
        xs[index] = value
        ys[index] = value
        assert list(ys) == xs
    else:
        with pytest.raises(IndexError, match="list assignment index out of range"):
            ys[index] = value


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=sys.maxsize))
def test_delitem(xs: list[int], index: int) -> None:
    ys = NonEmpty(*xs)
    if len(ys) == 1:
        with pytest.raises(
            ValueError,
            match=r"NonEmpty\.__delitem__\(x\): the last value cannot be removed",
        ):
            del ys[0]
    elif -len(ys) <= index < len(ys):
        del xs[index]
        del ys[index]
        assert list(ys) == xs
    else:
        with pytest.raises(IndexError, match="list assignment index out of range"):
            del ys[index]


@given(NonEmptyList)
def test_reversed(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    assert list(reversed(ys)) == list(reversed(xs))


@given(NonEmptyList, NonEmptyList)
def test_add(xs: list[int], ys: list[int]) -> None:
    zs = NonEmpty(xs) + NonEmpty(ys)
    assert list(zs)


@given(NonEmptyList, NonEmptyList)
def test_iadd(xs: list[int], ys: list[int]) -> None:
    zs = NonEmpty(*xs)
    zs += NonEmpty(*ys)
    assert zs == NonEmpty(*xs, *ys)


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=1000))
def test_mul(xs: list[int], value: int) -> None:
    if value < 1:
        with pytest.raises(
            ValueError, match="can't multiply NonEmpty by values smaller than '1'"
        ):
            NonEmpty(*xs) * value  # pyright: ignore[reportUnusedExpression]
    else:
        ys = NonEmpty(*xs) * value
        zs = xs * value
        assert ys == NonEmpty(*zs)


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=1000))
def test_rmul(xs: list[int], value: int) -> None:
    if value < 1:
        with pytest.raises(
            ValueError, match="can't multiply NonEmpty by values smaller than '1'"
        ):
            value * NonEmpty(*xs)  # pyright: ignore[reportUnusedExpression]
    else:
        ys = value * NonEmpty(*xs)
        zs = value * xs
        assert ys == NonEmpty(*zs)


@given(NonEmptyList, st.integers(min_value=-sys.maxsize, max_value=1000))
def test_imul(xs: list[int], value: int) -> None:
    ys = NonEmpty(*xs)
    if value < 1:
        with pytest.raises(
            ValueError, match="can't multiply NonEmpty by values smaller than '1'"
        ):
            ys *= value
    else:
        ys *= value
        xs *= value
        assert ys == NonEmpty(*xs)


@given(NonEmptyList, NonEmptyList)
def test_eq(xs: list[int], ys: list[int]) -> None:
    assert (NonEmpty(*xs) == NonEmpty(*ys)) == (xs == ys)


@given(NonEmptyList, NonEmptyList)
def test_lt(xs: list[int], ys: list[int]) -> None:
    assert (NonEmpty(*xs) < NonEmpty(*ys)) == (xs < ys)


@given(NonEmptyList)
def test_iter(xs: list[int]) -> None:
    assert list(iter(NonEmpty(*xs))) == xs


@given(NonEmptyList)
def test_match(xs: list[int]) -> None:
    ys = NonEmpty(*xs)
    first, rest = xs[0], xs[1:]
    match ys:
        case NonEmpty(head, tail):
            assert head == first
            assert tail == rest
