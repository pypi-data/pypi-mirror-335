from functools import wraps
from typing import (
    Callable,
    Generator,
    ParamSpec,
    TypeVar,
)

from moorlib.core.feedback.data import Feedback
from moorlib.core.feedback.feedback import FeedbackLoop


# T is the type yielded by the generator
T = TypeVar("T")
# S is the type of the feedback value
S = TypeVar("S")
# U is the type of the feedback's termination
U = TypeVar("U")

P = ParamSpec("P")


def feedback_based(
    func: Callable[P, Generator[T, Feedback[S, U], None]],
) -> Callable[P, FeedbackLoop[T, S, U]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> FeedbackLoop[T, S, U]:
        gen = func(*args, **kwargs)
        return FeedbackLoop(gen)

    return wrapper
