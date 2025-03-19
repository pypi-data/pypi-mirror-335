from typing import (
    Callable,
    get_args,
    get_origin,
    Literal,
    Type,
    TypeGuard,
    TypeVar,
)


T = TypeVar("T")

def is_literal(t: Type[T]) -> Callable[[str], TypeGuard[T]]:
    assert get_origin(t) is Literal
    return lambda value: value in get_args(t) # type: ignore
