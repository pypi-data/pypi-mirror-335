import re

from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from _pytest._code.code import ExceptionChainRepr
from _pytest.reports import TestReport


class TestResultStatus(Enum):
    FAILED = "failed"
    SKIPPED = "skipped"
    RUNS = "pending"
    PASSED = "passed"


@dataclass(frozen=True)
class TestActionResult:
    action: str
    status: TestResultStatus
    error: Optional[Exception] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    skip_reason: Optional[str] = None
    parameters: Optional[List[Tuple[str, Any]]] = None
    duration: Optional[float] = 0.0

    @classmethod
    def create_from_test_report(cls, report: TestReport) -> "TestActionResult":
        status = cls.make_status(report)
        action = report.when
        stdout = None
        if hasattr(report, "sections"):
            for name, content in report.sections:
                if "stdout" in name:
                    stdout = content

        skip_reason = None
        if report.outcome == TestResultStatus.SKIPPED.value:
            if hasattr(report, "wasxfail") and report.wasxfail:
                skip_reason = report.wasxfail
            elif isinstance(report.longrepr, ExceptionChainRepr):
                skip_reason = report.longrepr.chain[-1][2]
            else:
                skip_reason = report.longrepr[2][9:]

        return cls(
            action=action,
            status=status,
            error=report.exception if status == TestResultStatus.FAILED else None,
            stdout=stdout,
            skip_reason=skip_reason,
            parameters=list(report.parameters.items()),
            duration=report.duration,
        )

    @classmethod
    def make_status(cls, record: TestReport) -> TestResultStatus:
        if record.outcome == TestResultStatus.FAILED.value:
            return TestResultStatus.FAILED
        elif record.outcome == TestResultStatus.SKIPPED.value:
            return TestResultStatus.SKIPPED
        elif record.when in ["setup", "call"]:
            return TestResultStatus.RUNS

        return TestResultStatus.PASSED


class TestResult:
    FAIL = "failed"
    SKIPPED = "skipped"
    RUNS = "pending"
    PASS = "passed"

    def __init__(self, identifier: str, description: str) -> None:
        self._identifier = identifier
        self._description = description
        self._results: List[TestActionResult] = []

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def base_identifier(self) -> str:
        return re.sub(r"\[(.+)]$", "", self._identifier)

    @property
    def description(self) -> str:
        return self._description

    @property
    def skip_reason(self) -> Optional[str]:
        return next(
            (r.skip_reason for r in self._results if r.skip_reason is not None), None
        )

    @property
    def status(self) -> TestResultStatus:
        if self.has_failed():
            return TestResultStatus.FAILED
        elif self.is_skipped():
            return TestResultStatus.SKIPPED
        elif self.is_running():
            return TestResultStatus.RUNS

        return TestResultStatus.PASSED

    @property
    def icon(self) -> str:
        return self._get_icon()

    @property
    def compact_icon(self) -> str:
        return self._get_icon(compact=True)

    @property
    def color(self) -> str:
        return self._get_color()

    @property
    def compact_color(self) -> str:
        return self._get_color(compact=True)

    @property
    def error(self) -> Optional[Exception]:
        return next((r.error for r in self._results if r.error is not None), None)

    @property
    def stdout(self) -> Optional[str]:
        if not self._results:
            return None

        return self._results[-1].stdout

    def has_failed(self) -> bool:
        return any(result.status is TestResultStatus.FAILED for result in self._results)

    def is_skipped(self) -> bool:
        return not self.has_failed() and any(
            result.status is TestResultStatus.SKIPPED for result in self._results
        )

    def is_running(self) -> bool:
        if not self._results:
            return True

        return self._results[-1].action != "teardown"

    @property
    def parameters(self) -> Optional[List[Tuple[str, Any]]]:
        if not self._results:
            return None

        return self._results[0].parameters

    @property
    def duration(self) -> float:
        return sum(result.duration for result in self._results)

    @classmethod
    def create_from_test_report(
        cls, report: TestReport, type: Optional[str] = None
    ) -> "TestResult":
        identifier = report.nodeid
        description = cls.make_description(report)

        result = TestResult(identifier, description)

        return result

    @classmethod
    def make_description(cls, record: TestReport) -> str:
        description = record.description
        if not description:
            description = record.nodeid.split("::")[-1]

            # Replace underscores with spaces
            description = description.replace("_", " ")

            # If it starts with `test_`, we remove it
            description = re.sub("^test(.*)", "\\1", description)

            # Remove spaces
            description = description.strip()

            # Drop parameters since they will be handled by the Style instance
            description = re.sub(r"\[(.+)]$", "", description)

        return description

    def add_result(self, result: TestActionResult) -> None:
        self._results.append(result)

    def _get_icon(self, compact: bool = False) -> str:
        status = self.status
        if status == TestResultStatus.FAILED:
            return "✕"
        elif status == TestResultStatus.SKIPPED:
            return "s"
        elif not self._results or self._results[-1].action in ["setup", "call"]:
            return "•" if not compact else "."

        return "✓" if not compact else "."

    def _get_color(self, compact: bool = False) -> str:
        status = self.status
        if status == TestResultStatus.FAILED:
            return "red"
        elif status == TestResultStatus.SKIPPED:
            return "yellow"
        elif not self._results or self._results[-1].action in ["setup", "call"]:
            return "blue" if not compact else "default;options=dark"

        return "green" if not compact else "default;options=dark"
