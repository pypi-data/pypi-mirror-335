from typing import Any
from typing import Dict
from typing import NoReturn
from typing import Type
from typing import TypeVar
from typing import Union

from treat.mock.any import Any as MockAny
from treat.mock.mock import Mock
from treat.mock.spy import Spy


T = TypeVar("T")
_ANY = MockAny()


class Mockery:
    def __init__(self) -> None:
        self._mocks: Dict[Any, Mock | Spy] = {}

    def mock(self, obj: Union[Any, Type]) -> Mock:
        if obj in self._mocks:
            return self._mocks[obj]

        self._mocks[obj] = Mock(obj)

        return self._mocks[obj]

    def spy(self, obj: Any) -> Spy:
        if obj in self._mocks:
            return self._mocks[obj]

        self._mocks[obj] = Spy(obj)

        return self._mocks[obj]

    def close(self) -> NoReturn:
        self._verify()

    def any(self) -> MockAny:
        return _ANY

    def _verify(self) -> None:
        try:
            for mock in self._mocks.values():
                mock.verify()
        finally:
            self._reset()

    def _reset(self) -> None:
        for mock in self._mocks.values():
            mock.reset()

        self._mocks = {}
