from typing import Optional


class FeedbackError(RuntimeError):
    def __init__(self, message: str, after: Optional[BaseException] = None):
        if after is not None:
            self.message = f"{message}\n{after}"
        else:
            self.message = message
        super().__init__(self.message)


class MixtureOfErrors(FeedbackError):
    """Exception raised when a mixture of errors is raised"""

    def __init__(self, errors: list[BaseException]):
        self.errors = errors
        self.message = "the following errors were raised during the feedback loop lifecycle:\n" + "\n".join(
            [str(error) for error in errors]
        )
        super().__init__(self.message)


class LifeCycleError(FeedbackError):
    """Exception raised when feedback loop cycle is not correct"""

    def __init__(self, what: str, after: Optional[BaseException] = None):
        super().__init__(
            f"the following problem happened during the feedback loop lifecycle that is not correct:\n{what}",
            after=after,
        )
