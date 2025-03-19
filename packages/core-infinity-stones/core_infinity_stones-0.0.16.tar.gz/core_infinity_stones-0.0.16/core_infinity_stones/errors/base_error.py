from typing import Optional


class BaseError(Exception):
    def __init__(
        self,
        status_code: int,
        occurred_while: str,
        caused_by: Optional[Exception] = None,
        debug_description: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self.status_code = status_code
        self.occurrence_context = occurred_while
        self.original_error = caused_by
        self._debug_description = debug_description
        self._message = message

    @property
    def debug_description(self) -> str:
        debug_description = f"Error occurred while {self.occurrence_context}\n"

        if self._debug_description:
            debug_description += f"with message: {self._debug_description}\n"

        if self.original_error:
            debug_description += f"caused by: {self.original_error}"

        return debug_description

    @property
    def message(self) -> str:
        if self._message:
            return self._message
        return f"Something went wrong while {self.occurrence_context}"
