from collections import defaultdict
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from _pytest.reports import TestReport

from .test_result import TestActionResult
from .test_result import TestResult
from .test_result import TestResultStatus


class State:
    def __init__(self, group: Tuple[str]) -> None:
        self.suite_total_tests = None
        self._suite_tests: Dict[Tuple[str], Dict[str, TestResult]] = {}
        self._group = group
        self._group_tests: Dict[str, TestResult] = {}
        self._errors: Dict[Tuple[str], List[TestResult]] = {}
        self._errors_count = 0
        self._parameter_sets = defaultdict(dict)
        self._durations = defaultdict(lambda: 0.0)
        self.header_printed = False

    @property
    def group(self) -> Tuple[str]:
        return self._group

    @property
    def tests(self) -> Iterator[TestResult]:
        return self._group_tests.values()

    @property
    def group_title(self) -> str:
        if any(
            test.status == TestResultStatus.FAILED
            for test in self._group_tests.values()
        ):
            return "FAIL"

        if any(
            test.status != TestResultStatus.PASSED
            for test in self._group_tests.values()
        ):
            return "WARN"

        return "PASS"

    @property
    def group_title_color(self) -> str:
        if any(
            test.status == TestResultStatus.FAILED
            for test in self._group_tests.values()
        ):
            return "red"

        if any(
            test.status != TestResultStatus.PASSED
            for test in self._group_tests.values()
        ):
            return "yellow"

        return "green"

    @property
    def group_tests_count(self) -> int:
        return len(self._group_tests)

    @property
    def suite_tests_count(self) -> int:
        count = 0
        for group_tests in self._suite_tests.values():
            for _ in group_tests.values():
                count += 1

        return count

    @property
    def errors(self) -> Dict[Tuple[str], List[TestResult]]:
        return self._errors

    @property
    def errors_count(self) -> int:
        return self._errors_count

    def parameter_set(self, test) -> Optional[int]:
        if (
            test.base_identifier not in self._parameter_sets
            or test.identifier not in self._parameter_sets[test.base_identifier]
        ):
            return None

        return self._parameter_sets[test.base_identifier][test.identifier]

    def get_test_from_report(self, report: TestReport) -> TestResult:
        test = TestResult.create_from_test_report(report)

        if test.identifier in self._group_tests:
            return self._group_tests[test.identifier]

        return test

    def add_report(self, report: TestReport) -> None:
        test = self.get_test_from_report(report)

        self._group_tests[test.identifier] = test

        action_result = TestActionResult.create_from_test_report(report)
        test.add_result(action_result)

        if action_result.error:
            self._errors.setdefault(self._group, [])
            self._errors[self._group].append(test)
            self._errors_count += 1

        if self._group not in self._suite_tests:
            self._suite_tests[self._group] = {}

        self._suite_tests[self._group] = self._group_tests

        if action_result.parameters:
            if test.identifier not in self._parameter_sets[test.base_identifier]:
                self._parameter_sets[test.base_identifier][test.identifier] = (
                    len(self._parameter_sets[test.base_identifier]) + 1
                )

        self._durations[test.identifier] += action_result.duration

    def test_exists_in_group(self, test: TestResult) -> bool:
        return test.identifier in self._group_tests

    def group_has_changed(self, report: TestReport) -> bool:
        return tuple(report.nodeid.split("::")[:-1]) != self._group

    def move_to(self, report: TestReport) -> None:
        self._group = tuple(report.nodeid.split("::")[:-1])
        self._group_tests = {}
        self.header_printed = False

    def count_tests_in_suite_with_type(self, type: TestResultStatus) -> int:
        count = 0

        for group_tests in self._suite_tests.values():
            for test in group_tests.values():
                if test.status == type:
                    count += 1

        return count

    def duration(self, test: TestResult) -> float:
        return self._durations[test.identifier]
