class VersionCheckFailed(Exception):
    """
    Exception raised when one or more tool version checks fail.

    This exception indicates that the installed tool versions do not meet the required criteria.
    """

    def __init__(
        self,
        message: str = (
            "One or more tools failed the version check. "
            "Please review the instructions above and fix the issues."
        ),
    ):
        super().__init__(message)
        self.message = message
