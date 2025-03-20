import asyncio
from collections.abc import Callable
from functools import partial
from inspect import iscoroutine
from typing import Protocol, Type


class Paradigm[**P, T](Protocol):
    def __call__(self, callable_: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs) -> T: ...


class Caller[**P, T](Protocol):

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


class Paradigms:

    def get[**P, T](
        self,
        callable_: Callable[P, T],
        paradigm: Type[Paradigm[P, T]] | None = None,
        execution: None = None,
    ) -> Caller[P, T]:
        return partial(callable_)

    __call__ = get
