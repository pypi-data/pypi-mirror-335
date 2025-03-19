from collections.abc import Iterator
from contextlib import contextmanager
from typing import Callable, Literal, Optional, Union, overload

from classiq.interface.exceptions import ClassiqInternalError

from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.quantum_function import (
    BaseQFunc,
    ExternalQFunc,
    GenerativeQFunc,
    QFunc,
)

_GENERATIVE_SWITCH = False


@contextmanager
def set_global_generative_switch() -> Iterator[None]:
    global _GENERATIVE_SWITCH
    previous = _GENERATIVE_SWITCH
    _GENERATIVE_SWITCH = True
    try:
        yield
    finally:
        _GENERATIVE_SWITCH = previous


@overload
def qfunc(func: Callable) -> QFunc: ...


@overload
def qfunc(
    *,
    external: Literal[True],
    synthesize_separately: Literal[False] = False,
    atomic_qualifiers: Optional[list[str]] = None,
) -> Callable[[Callable], ExternalQFunc]: ...


@overload
def qfunc(
    *,
    generative: Literal[True],
    synthesize_separately: bool = False,
    atomic_qualifiers: Optional[list[str]] = None,
) -> Callable[[Callable], GenerativeQFunc]: ...


@overload
def qfunc(
    *, synthesize_separately: bool, atomic_qualifiers: Optional[list[str]] = None
) -> Callable[[Callable], QFunc]: ...


@overload
def qfunc(
    *,
    synthesize_separately: bool = False,
    atomic_qualifiers: Optional[list[str]] = None,
) -> Callable[[Callable], QFunc]: ...


def qfunc(
    func: Optional[Callable] = None,
    *,
    external: bool = False,
    generative: bool = False,
    synthesize_separately: bool = False,
    atomic_qualifiers: Optional[list[str]] = None,
) -> Union[Callable[[Callable], QCallable], QCallable]:
    def wrapper(func: Callable) -> QCallable:
        qfunc: BaseQFunc

        if external:
            _validate_directives(synthesize_separately, atomic_qualifiers)
            return ExternalQFunc(func)

        if generative or _GENERATIVE_SWITCH:
            qfunc = GenerativeQFunc(func)
        else:
            qfunc = QFunc(func)
        if synthesize_separately:
            qfunc.update_compilation_metadata(should_synthesize_separately=True)
        if atomic_qualifiers is not None and len(atomic_qualifiers) > 0:
            qfunc.update_compilation_metadata(atomic_qualifiers=atomic_qualifiers)
        return qfunc

    if func is not None:
        return wrapper(func)
    return wrapper


def _validate_directives(
    synthesize_separately: bool, atomic_qualifiers: Optional[list[str]] = None
) -> None:
    error_msg = ""
    if synthesize_separately:
        error_msg += "External functions can't be marked as synthesized separately. \n"
    if atomic_qualifiers is not None and len(atomic_qualifiers) > 0:
        error_msg += "External functions can't have atomic qualifiers."
    if error_msg:
        raise ClassiqInternalError(error_msg)
