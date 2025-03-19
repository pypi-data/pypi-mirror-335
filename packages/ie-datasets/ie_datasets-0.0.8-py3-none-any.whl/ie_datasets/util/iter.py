from typing import Iterable, TypeVar, Union


T = TypeVar("T")

def only(it: Iterable[T]) -> T:
    it = iter(it)
    x = next(it)
    for y in it:
        raise ValueError("Iterator contains more than one element.")
    return x


def same(it: Iterable[T]) -> T:
    it = iter(it)
    x = next(it)
    for y in it:
        if y != x:
            raise ValueError("Not all elements of the iterator are the same.")
    return x
