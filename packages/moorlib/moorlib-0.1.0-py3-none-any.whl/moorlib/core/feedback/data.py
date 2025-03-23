from typing import (
    Generic,
    TypeVar,
)


# S is the type of the feedback value
S = TypeVar("S")
# U is the type of the feedback's termination
U = TypeVar("U")


class Feedback(Generic[S, U]):
    def __init__(self) -> None:
        pass


class Value(Feedback[S, U]):
    def __init__(self, value: S) -> None:
        super().__init__()
        self.value = value


class Termination(Feedback[S, U]):
    def __init__(self, value: U) -> None:
        super().__init__()
        self.value = value
