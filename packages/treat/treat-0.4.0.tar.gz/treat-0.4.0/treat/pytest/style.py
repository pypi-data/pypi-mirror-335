import os
import shutil

from shutil import get_terminal_size
from typing import List
from typing import Optional
from typing import Tuple

import _pytest
import pluggy

from _pytest._code.code import ExceptionInfo
from _pytest.reports import TestReport
from cleo.formatters.formatter import Formatter
from cleo.io.outputs.output import Output
from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.section_output import SectionOutput
from cleo.ui.exception_trace import Highlighter

import treat

from treat.ui.exception_trace import ExceptionTrace

from ..utils.diff import Diff
from .state import State
from .test_result import TestActionResult
from .test_result import TestResult
from .test_result import TestResultStatus


class Style:
    _TYPES: List[TestResultStatus] = [
        TestResultStatus.PASSED,
        TestResultStatus.FAILED,
        TestResultStatus.SKIPPED,
    ]

    def __init__(self, output: Output, compact: bool = False) -> None:
        self._output = output
        self._compact = compact
        self._footer: SectionOutput = self._output.section()
        self._ignore_files_in = r"^({}|{}|{}|{})".format(
            os.path.dirname(_pytest.__file__),
            os.path.dirname(pluggy.__file__),
            treat.__file__,
            os.path.join(os.path.dirname(treat.__file__), "mock"),
        )
        self._inline_errors = False
        self._terminal = shutil.get_terminal_size()
        self._compact_processed = 0
        self._compact_symbols_per_line = self._terminal.columns - 4

    @property
    def footer(self) -> SectionOutput:
        return self._footer

    @property
    def terminal(self) -> os.terminal_size:
        return self._terminal

    def is_compact(self) -> bool:
        return self._compact

    def inline_errors(self, inline_errors: bool = True) -> "Style":
        self._inline_errors = inline_errors

        return self

    def write_current_recap(self, state: State) -> None:
        if self._compact:
            return

        if not state.group_tests_count:
            return

        if not state.header_printed:
            self._footer.clear()

            self._output.write_line(
                self._title_line(
                    "black", state.group_title_color, state.group_title, state.group
                )
            )

            state.header_printed = True

        for test in state.tests:
            self._write_description_line(state, test)

            if test.error:
                if self._inline_errors:
                    self._write_error(test)

    def update_footer(self, state: State, report: Optional[TestReport] = None) -> None:
        if self._compact:
            return None

        self._footer.overwrite(self._footer_content(state, report))

    def write_recap(self, state: State, elapsed: float) -> None:
        if not self._compact:
            self._footer.clear()
        else:
            self._output.write_line("")

        if state.errors and (not self._inline_errors or self._compact):
            self.write_errors_summary(state)

        self._output.write_line(self._footer_content(state))
        self._output.write_line(
            f"  <fg=default;options=bold>Time:   </><fg=default>{elapsed:0.2f}s</>"
        )

    def write_errors_summary(self, state: State) -> None:
        i = 1
        padding = len(str(state.errors_count))
        for group, errors in state.errors.items():
            for test in errors:
                self._output.write_line("")
                if state.errors_count > 1:
                    self._output.write_line("")
                    line = (
                        f"<fg=red;options=bold>Failed test</> "
                        f"<fg=default;options=dark>(</><fg=default;options=bold>{i:{padding}}<fg=default;options=dark>/</>{state.errors_count}</><fg=default;options=dark>)</>"
                    )
                    self._output.write_line(
                        "<fg=default;options=dark>╭─</><fg=red;options=bold>✕</> "
                        + line
                    )
                    self._output.write_line("<fg=default;options=dark>│</>")

                self._output.write_line(
                    f"{'<fg=default;options=dark>╰─</>' if state.errors_count > 1 else '  '}<fg=red;options=bold>•</> "
                    f"{self._group_line(group)} "
                    f"<fg=default;options=dark>></> "
                    f"<fg=red;options=bold>{test.description}</>"
                    "</>"
                )
                self._output.write_line("    " + self._identifier_line(test.identifier))
                self._write_error(test)
                i += 1

    def _write_error(self, test: TestResult) -> None:
        self._write_parameters(test)

        if test.stdout:
            self._output.write_line("")
            self._output.write_line("    <fg=default;options=bold>Stdout:</>")
            self._output.write_line("")
            self._output.write_line(
                "    "
                + self._output.formatter.escape(test.stdout).replace("\n", "\n    ")
            )

        error = test.error
        if isinstance(error, ExceptionInfo):
            error = error.value

        trace = ExceptionTrace(error, base_indent=2)
        trace.ignore_files_in(self._ignore_files_in)
        verbosity = self._output.verbosity
        self._output.set_verbosity(Verbosity.VERY_VERBOSE)
        trace.render(self._output)
        self._output.set_verbosity(verbosity)

        self._output.write_line("")

    def _type_color(self, type: TestResultStatus) -> str:
        if type == TestResultStatus.FAILED:
            return "red"
        elif type == TestResultStatus.SKIPPED:
            return "yellow"

        return "green"

    def _title_line(self, fg: str, bg: str, title: str, group: Tuple[str]) -> str:
        group = self._group_line(group)

        return f"\n  <fg={bg};options=bold>{title}</> <fg=default;options=dark,bold>•</> {group}"

    def _group_line(self, group: Tuple[str]) -> str:
        path = group[0]
        path_parts = path.split(os.path.sep)
        for i, part in enumerate(path_parts[:-1]):
            path_parts[i] = f"<fg=default>{part}</>"

        path_parts[-1] = f"<fg=default;options=bold>{path_parts[-1]}</>"
        line = f"<fg=default;options=dark>{os.path.sep}</>".join(path_parts)

        if len(group) > 1:
            line += " <fg=default;options=dark>></> "
            line += f"<fg=default;options=bold>{group[1]}</>"
            line += " <fg=default;options=dark>></> ".join(
                f"<fg=default;options=bold>{g}" for g in group[1:-1]
            )

        return line

    def _test_line(
        self,
        fg: str,
        icon: str,
        description: str,
        warning: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> str:
        if duration is not None and int(duration * 10) > 0:
            duration = f"{duration:.2f}s"
        else:
            duration = ""

        warning = warning or ""

        needed_width = (
            2
            + 1
            + len(self._output.remove_format(description))
            + len(warning)
            + 3
            + 3
            + len(duration)
            + bool(duration)
            + 2
        )
        available_width = self._terminal.columns

        if warning:
            warning = (
                f" <fg=default;options=dark>(<fg=default;options=bold>Skipped</>: "
                f"<fg=yellow;options=bold>{warning}</>)</>"
            )
        else:
            warning = ""

        line = f"  <fg={fg};options=bold>{icon}</><fg=default> {description}{warning}"

        if duration:
            duration_padding = available_width - needed_width + 4

            if duration_padding < 1:
                duration_padding = 1

            line += f"{duration_padding * ' '}<fg=default;options=dark>{duration}</></>"

        return line

    def _identifier_line(self, identifier: str) -> str:
        return f"<fg=default;options=dark>{identifier}</>"

    def _footer_content(self, state: State, report: Optional[TestReport] = None) -> str:
        runs = []

        if report:
            runs.append(self._title_line("black", "blue", "RUNS", state.group))

            test = TestResult.create_from_test_report(report)
            test.add_result(TestActionResult.create_from_test_report(report))
            description = test.description
            if test.parameters:
                description += " <fg=blue><b>#</b>{}</blue>".format(
                    state.parameter_set(test) or 1
                )

            runs.append(self._test_line(test.color, test.icon, description))

        tests = []
        for type_ in self._TYPES:
            tests_count = state.count_tests_in_suite_with_type(type_)
            if tests_count:
                color = self._type_color(type_)
                tests.append(
                    f"<fg={color}><fg={color};option=bold>{tests_count}</> {type_.value}</>"
                )

        if state.suite_total_tests is not None:
            pending = state.suite_total_tests - state.suite_tests_count
            if pending:
                tests.append(
                    f"<fg=default;options=dark><fg=default;options=dark,bold>{pending}</> pending</>"
                )

        if tests:
            footer = "\n".join(
                runs
                + [""]
                + [
                    f"  <fg=default;options=bold>Tests:  </><fg=default>{', '.join(tests)}</>"
                ]
            )

            return footer

        return ""

    def _write_description_line(self, state: State, test: TestResult) -> None:
        description = test.description

        if test.parameters:
            description += " <fg=blue><b>#</b>{}</blue>".format(
                state.parameter_set(test)
            )

        self._output.write_line(
            self._test_line(
                test.color,
                test.icon,
                description,
                warning=test.skip_reason if test.is_skipped() else None,
                duration=state.duration(test),
            )
        )
        if self._output.is_very_verbose():
            self._output.write_line("    " + self._identifier_line(test.identifier))

            self._write_parameters(test)

    def write_current_test(self, state: State) -> None:
        if not self._compact:
            return

        test = list(state.tests)[-1]

        symbols_on_current_line = (
            self._compact_processed % self._compact_symbols_per_line
        )

        if symbols_on_current_line >= self._terminal.columns - 4:
            symbols_on_current_line = 0

        if symbols_on_current_line == 0:
            self._output.write_line("")
            self._output.write("  ")

        self._output.write(
            f"<fg={test.compact_color};options=bold>{test.compact_icon}</>"
        )

        self._compact_processed += 1

    def _write_parameters(self, test: TestResult) -> None:
        if not test.parameters:
            return

        diff = Diff(get_terminal_size().columns)
        formatter = Formatter()
        highlighter = Highlighter(supports_utf8=self._output.supports_utf8())

        self._output.write_line("")
        for name, value in test.parameters:
            if isinstance(value, str):
                formatted_value = repr(value)
            else:
                formatted_value = diff.prettify(value)

            param_description = [
                f"    <fg=default;option=bold>{name}</><fg=default;options=dark>:</> "
            ]
            lines = highlighter.highlighted_lines(formatter.escape(formatted_value))
            param_description[0] += lines[0]
            param_description += ["    " + line for line in lines[1:]]
            self._output.write_line(param_description)

        self._output.write_line("")
