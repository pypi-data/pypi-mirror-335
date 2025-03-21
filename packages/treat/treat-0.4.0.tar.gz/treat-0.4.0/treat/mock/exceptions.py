import inspect

from typing import Optional
from typing import Tuple

from treat.exceptions import FrameAwareExceptionMixin
from treat.exceptions import TreatException
from treat.ui.errors import UIError


class MockError(TreatException, UIError):
    @property
    def pretty_error(self) -> str:
        return str(self)


class FrameAwareMockError(MockError, FrameAwareExceptionMixin):
    def __init__(
        self, *args, frame: Optional[inspect.FrameInfo] = None, **kwargs
    ) -> None:
        self.set_frame(frame)

        super().__init__(*args, **kwargs)


class InvalidMockCallsCount(FrameAwareMockError):
    MESSAGE_FORMAT = (
        "Expected <fg=cyan>{call}</> to {expected_message} "
        "but it was actually {got_message}."
    )

    def __init__(
        self,
        name: str,
        expected: int,
        got: int,
        arguments: Optional[Tuple] = None,
        frame: Optional[inspect.FrameInfo] = None,
    ) -> None:
        self._name = name
        self._expected = expected
        self._got = got
        self._arguments = arguments

        if self._arguments:
            args, kwargs = self._arguments
            call_args = []
            if args:
                call_args += list(repr(arg) for arg in args)

            if kwargs:
                for kwarg_name, kwarg_value in kwargs:
                    call_args.append(f"{kwarg_name}={repr(kwarg_value)}")

            self._call = f"{self._name}({', '.join(call_args)})"
        else:
            self._call = f"{self._name}()"
        self._message = self.MESSAGE_FORMAT.format(
            call=self._call,
            expected_message=self._get_call_message(expected),
            got_message=self._get_call_message(got, expected=False),
        )

        super().__init__(self.remove_format(self._message), frame=frame)

    @property
    def pretty_error(self) -> str:
        return self._message

    def _get_call_message(self, value: int, expected: bool = True) -> str:
        color = "green"
        if not expected:
            color = "red"

        never = ""
        if value == 0:
            never = f"<fg={color};options=bold>never</> "

        if expected:
            message = never + "be called"
        else:
            message = never + "called"

        if value == 1:
            message += f" <fg={color};options=bold>once</>"
        elif value == 2:
            message += f" <fg={color};options=bold>twice</>"
        elif value != 0:
            message += f" <fg={color};options=bold>{value}</> times"

        return message
