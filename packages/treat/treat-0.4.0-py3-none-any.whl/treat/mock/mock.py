from typing import Any
from typing import Dict

from treat.mock.expectation import Expectation
from treat.mock.expectation import ExpectationKind
from treat.mock.expectation_director import ExpectationDirector
from treat.utils._compat import ReversableDict


class Mock:
    def __init__(self, mocked: Any) -> None:
        self._mocked: Any = mocked
        self._expectation_directors: Dict[str, ExpectationDirector] = ReversableDict()

    @property
    def mocked(self) -> Any:
        return self._mocked

    def should_receive(self, name: str) -> Expectation:
        if name not in self._expectation_directors:
            director = ExpectationDirector(name, self)
            director.setup()

            self._expectation_directors[name] = director

        expectation = Expectation(name, ExpectationKind.METHOD)
        self._expectation_directors[name].add_expectation(expectation)

        return expectation

    def verify(self) -> None:
        for director in self._expectation_directors.values():
            director.verify()

    def reset(self) -> None:
        for director in reversed(self._expectation_directors.values()):
            director.teardown()
