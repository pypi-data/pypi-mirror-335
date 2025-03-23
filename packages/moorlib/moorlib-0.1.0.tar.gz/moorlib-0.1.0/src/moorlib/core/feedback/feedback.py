from typing import (
    Any,
    Generator,
    Generic,
    Iterator,
    Optional,
    TypeVar,
)

from moorlib.core.feedback.data import Feedback, Termination, Value
from moorlib.core.feedback.errors import (
    FeedbackError,
    LifeCycleError,
    MixtureOfErrors,
)


# T is the type yielded by the generator
T = TypeVar("T")
# S is the type of the feedback value
S = TypeVar("S")
# U is the type of the feedback's termination
U = TypeVar("U")


class FeedbackLoop(Generic[T, S, U]):
    """
    The following are the properties of the feedback loop, if any of them is violated, the feedback loop is corrupted:
    - The loop starts by getting the first guess from the guesser, and then sending feedback to the guesser, and so on.
        - Sending two feedbacks without getting a guess will result in an exception (not corruption).
        - Getting a guess without sending feedback for the last guess will result in an exception (and corruption).
    - The guesser finishes its execution by one of the following cases:
        1. The guesser returns.
        2. The guesser is informed of acceptance/rejection/corruption (if the guesser continues guessing, an exception will be raised).
        3. The guesser raises an exception (which will corrupt the loop).
    - After the guesser finishes, the feedback loop is done and further asking (or sending feedbacks) results in exceptions (but not corruption).
    - When existing the feedback loop, the guesser should be done, otherwise an exception will be raised.
        - If it is through an exception, and the guesser is not done, the exception will be augmented with not informing the guesser.
    NOTE:
    - Calling any methods of a corrupted feedback loop will raise the exception that caused the corruption.
    - Calling any methods of a feedback loop after it is done will raise an exception.
    - Accessing the private methods or variables of the feedback loop may cause assertions, which are not recoverable (hopefully).
    """

    def __init__(self, gen: Generator[T, Feedback[S, U], None]) -> None:
        self._gen: Generator[T, Feedback[S, U], None] = gen
        self._current_feedback: Optional[Feedback[S, U]] = None
        self._current_guess: Optional[T] = None

        # Lifecycle flags
        self._guesser_started: bool = False  # the feedback loop has started
        self._guesser_done: bool = False  # the guesser has finished guessing
        self._corrupted: Optional[FeedbackError] = None  # the cause of the corruption

    def _if_corrupted_raise(self) -> None:
        assert self._guesser_started, "feedback loop should be started before checking for corruption"

        if self._corrupted is not None:
            assert self._guesser_done, "feedback loop should be informed if it is corrupted"
            raise self._corrupted

    def _raise_and_corrupt(self, error: FeedbackError) -> None:
        assert self._guesser_started, "feedback loop should be started by now"
        assert not self._guesser_done, "feedback loop should not be done yet"
        assert self._corrupted is None, "feedback loop should not be corrupted yet"

        self._corrupted = error
        if not self._guesser_done:
            try:
                # TODO change to sending an Error value instead
                self._gen.close()
            except BaseException as e:
                self._corrupted = MixtureOfErrors([error, e])
            self._guesser_done = True
        raise self._corrupted

    def __enter__(self) -> "FeedbackLoop[T, S, U]":
        """WARN: do not use this method directly"""
        assert not self._guesser_started, "feedback loop should not be started yet"
        assert not self._guesser_done, "feedback loop should not be done yet"
        assert self._corrupted is None, "feedback loop should not be corrupted yet"

        self._guesser_started = True

        try:
            self._current_guess = next(self._gen)
        except StopIteration:
            self._guesser_done = True
        except BaseException as e:
            self._guesser_done = True
            self._raise_and_corrupt(LifeCycleError("an exception happened inside guesser.", e))
        return self

    def __exit__(self, exc_type: Any, exc_value: BaseException, traceback: Any) -> None:
        """WARN: do not use this method directly"""
        assert self._guesser_started, "feedback loop should be started by now"

        if not self._guesser_done:
            self._raise_and_corrupt(LifeCycleError("feedback loop closed without informing the guesser", exc_value))

    def __iter__(self) -> Iterator[T]:
        assert self._guesser_started, "feedback loop should be started by now"

        self._if_corrupted_raise()

        if self._guesser_done:
            raise LifeCycleError("feedback loop is being used after guesser has finished guessing")

        while not self._guesser_done:
            assert self._current_guess is not None
            yield self._current_guess

            self._if_corrupted_raise()

            if self._guesser_done:
                break

            if self._current_feedback is None:
                self._raise_and_corrupt(
                    LifeCycleError("feedback is not provided although being asked for more guesses")
                )
            try:
                assert self._current_feedback is not None
                self._current_guess = self._gen.send(self._current_feedback)
                self._current_feedback = None
                continue
            except StopIteration:
                self._guesser_done = True
                break
            except Exception as e:
                self._raise_and_corrupt(LifeCycleError("an exception happened inside guesser", e))

    def send_feedback(self, value: S) -> None:
        assert self._guesser_started, "feedback loop should be started by now"
        self._if_corrupted_raise()

        if self._guesser_done:
            raise LifeCycleError("cannot send feedback after the guesser has finished")
        if self._current_feedback is not None:
            raise LifeCycleError("cannot send two feedbacks without getting a guess")

        self._current_feedback = Value(value)

    def terminate(self, value: U) -> None:
        assert self._guesser_started, "feedback loop should be started by now"
        self._if_corrupted_raise()

        if self._guesser_done:
            raise LifeCycleError("cannot accept guess after the guesser has finished")
        if self._current_feedback is not None:
            raise LifeCycleError("cannot accept a guess without getting a guess")

        self._current_feedback = Termination(value)
        try:
            self._gen.send(self._current_feedback)
        except StopIteration:
            self._guesser_done = True
            return
        except BaseException as e:
            self._raise_and_corrupt(
                LifeCycleError(
                    "an exception happened inside guesser while informing it of acceptance",
                    e,
                )
            )

        self._raise_and_corrupt(LifeCycleError("the guesser didn't finish guessing after being accepted"))
