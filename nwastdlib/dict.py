"""Module containing utility functions for lists."""
from functools import reduce
from typing import Any, Callable, Dict, Optional, Set, TypeVar, Union, cast

from .either import Either
from .maybe import Maybe

k = TypeVar("k")
α = TypeVar("α")


def filterWithKey(p: Callable[[k, α], bool], d: Dict[k, α]) -> Dict[k, α]:
    """
    Filter the items of a dict with a predicate on key and value.

    >>> d = dict(a=1, b=2)

    >>> filterWithKey(lambda k, v: k == 'a', d)
    {'a': 1}
    """
    return {k: v for k, v in d.items() if p(k, v)}


def filterByKey(ks: Set[k], d: Dict[k, α]) -> Dict[k, α]:
    """
    Filter all items of a dict where the key exists in a key space.

    >>> d = dict(a=1, b=2)

    >>> filterByKey({'a'}, d)
    {'a': 1}
    """
    return filterWithKey(lambda k, v: k in ks, d)


def getByKeys(ks: Set[k], d: Dict[k, α]) -> Either[k, Dict[k, α]]:
    """
    For all keys in a key space get their corresponding value from a dict.

    >>> d = dict(a=1, b=2)

    >>> getByKeys({'a'}, d)
    Right {'a': 1}

    >>> getByKeys({'a', 'c'}, d)
    Left 'c'
    """

    def get(k):
        return lookup(k, d).maybe(Either.Left(k), lambda v: Either.Right((k, v)))

    return Either.sequence([get(k) for k in ks]).map(dict)


def lookup(k: k, d: Dict[k, Optional[α]]) -> Maybe[α]:
    """
    Lookup the value associated with a key in a dict.

    >>> d = dict(a=1, b=2)

    >>> lookup("a", d)
    Some 1

    >>> lookup("c", d)
    Nothing
    """
    return Maybe.of(d.get(k, None))


def delete(key: k, d: Dict[k, α]) -> Dict[k, α]:
    """
    Delete a key from a dict.

    >>> d = dict(a=1, b=2)

    >>> delete("a", d)
    {'b': 2}

    >>> delete("c", d)
    {'a': 1, 'b': 2}
    """
    return {k: v for k, v in d.items() if k != key}


def insert(key: k, value: α, d: Dict[k, α]) -> Dict[k, α]:
    """
    Insert a key/value pair into a dict.

    >>> d = dict(a=1)

    >>> insert('b', 2, d)
    {'a': 1, 'b': 2}

    >>> insert('a', 2, d)
    {'a': 2}
    """
    return {**d, key: value}


def merge(d1: Dict[k, α]) -> Callable[[Dict[k, α]], Dict[k, α]]:
    """
    Curried (one-level) merge for two dicts.

    >>> d = dict(a=1)
    >>> md = merge(d)

    >>> md({'b': 2})
    {'a': 1, 'b': 2}

    >>> md({'a': 2})
    {'a': 2}
    """
    return lambda d2: {**d1, **d2}


def append(d1: Dict[k, Any], d2: Dict[k, Any]) -> Dict[k, Any]:
    """
    Append a Dict.

    A rather limited version of append that only appends dicts. Even values that
    are easily appendable (eg int, str, etc) are /not/ appended by design.

    Conflict resolution:
    Any conflicting keys whose values cannot be appended (ie is not a dict) are
    overwritten with the value of the second dict.

    >>> append({}, {'a': 1})
    {'a': 1}

    >>> append({'a': 1}, {'a': 2})
    {'a': 2}

    >>> append({'a': 1}, {'b': 2})
    {'a': 1, 'b': 2}

    >>> append({'a': {'x': 1}}, {'a': {'y': 2}})
    {'a': {'x': 1, 'y': 2}}
    """
    d3 = {
        k: append(v, cast(dict, d2[k]))
        for (k, v) in d1.items()
        if k in d2 and isinstance(v, dict) and isinstance(d2[k], dict)
    }
    return {**d1, **d2, **d3}


# Proper type is in comments, though MyPy currently doesn't support recursive types yet. Hence the use of `Any`
# UnflatDict = Dict[str, Union[α, 'UnflatDict']]
UnflatDict = Dict[str, Union[α, Any]]


def unflatten(d: Dict[str, α], sep=".") -> UnflatDict:
    """
    Unflatten a dict who'se keys include `sep`.

    >>> unflatten({"a": 1, "b": 2})
    {'a': 1, 'b': 2}

    >>> unflatten({"a.b": 1})
    {'a': {'b': 1}}

    >>> unflatten({"a.b": 1, "a.c": 2, "x": 3})
    {'a': {'b': 1, 'c': 2}, 'x': 3}

    >>> unflatten({})
    {}
    """

    def unflatten1(parts, value):
        h, *t = parts
        if len(t) == 0:
            return {h: value}
        else:
            return {h: unflatten1(t, value)}

    return reduce(append, (unflatten1(k.split(sep), v) for (k, v) in d.items()), {})
