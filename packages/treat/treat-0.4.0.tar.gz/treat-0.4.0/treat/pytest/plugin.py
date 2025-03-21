import argparse
import sys

from shutil import get_terminal_size
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Sequence

import pytest

from _pytest.config import Config
from _pytest.nodes import Collector
from _pytest.nodes import Item
from _pytest.reports import CollectReport
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from cleo.formatters.formatter import Formatter
from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from cleo.io.outputs.stream_output import StreamOutput
from cleo.ui.exception_trace import ExceptionTrace

from treat import test
from treat.mock.mockery import Mockery
from treat.utils.diff import Diff

from ..ui.coverage_reporter import Coverage
from .terminal_reporter import TerminalReporter


if TYPE_CHECKING:
    from _pytest._code.code import ExceptionInfo
    from _pytest._code.code import ExceptionRepr
    from _pytest.python import PyCollector


def validate_min_coverage(num_str):
    try:
        value = int(num_str)
    except ValueError:
        try:
            value = float(num_str)
        except ValueError:
            raise argparse.ArgumentTypeError("An integer or float value is required.")
    if value > 100:
        raise argparse.ArgumentTypeError("The maximum value is 100.")
    return value


def pytest_addoption(parser):
    group = parser.getgroup("cov", "coverage reporting")

    group.addoption(
        "--coverage",
        action="append",
        default=[],
        metavar="SOURCE",
        nargs="?",
        const=True,
        dest="cov_source",
        help="Path or package name to measure during execution (multi-allowed). "
        "Use --coverage= to not do any source filtering and record everything.",
    )

    group.addoption(
        "--min-coverage",
        action="store",
        metavar="MIN",
        type=validate_min_coverage,
        help="Set the minimum required coverage percentage, and fail if not met.",
    )


@pytest.fixture()
def mockery():
    mockery = Mockery()

    yield mockery

    mockery.close()


@pytest.mark.tryfirst
def pytest_load_initial_conftests(early_config, parser, args):
    options = early_config.known_args_namespace

    io = IO(StringInput(""), StreamOutput(sys.stdout), StreamOutput(sys.stderr))
    coverage = None
    if options.cov_source:
        coverage = Coverage(io, source=early_config.known_args_namespace.cov_source)
        coverage.start()

    early_config.pluginmanager.register(TreatPlugin(io, coverage), "treatplugin")


class DeferredXdistPlugin:
    def pytest_xdist_node_collection_finished(self, node, ids):
        terminal_reporter: TerminalReporter = node.config.pluginmanager.getplugin(
            "terminalreporter"
        )
        if terminal_reporter:
            terminal_reporter.state.suite_total_tests = len(ids)
            terminal_reporter._count = len(ids)


def is_xdist_worker(request_or_session) -> bool:
    return hasattr(request_or_session.config, "workerinput")


def is_xdist_controller(request_or_session) -> bool:
    return (
        not is_xdist_worker(request_or_session)
        and hasattr(request_or_session.config.option, "dist")
        and request_or_session.config.option.dist != "no"
    )


class TreatPlugin:
    def __init__(self, io: "IO", coverage: "Coverage" = None) -> None:
        self._coverage = coverage
        self._io = io

    def pytest_pycollect_makeitem(
        self, collector: "PyCollector", name: str, obj: object
    ):
        # Avoid test() from being picked up by pytest
        if obj is test:
            return []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_make_collect_report(self, collector: Collector):
        outcome = yield

        report = outcome.get_result()
        assert isinstance(report, CollectReport)
        report.excinfo = report.call.excinfo

    def pytest_runtest_makereport(self, item: Item, call: CallInfo[None]) -> TestReport:
        report = TestReport.from_item_and_call(item, call)

        runs_with_xdist = is_xdist_worker(item.session) or is_xdist_controller(
            item.session
        )

        callspec = item.callspec if hasattr(item, "callspec") else None
        parameters = callspec.params if callspec else {}
        exception = call.excinfo

        description = item.obj.__doc__
        if description is not None:
            description_parts = description.strip().split("\n", 1)
            description = description_parts[0]
            description = description.strip()

        report.__dict__.update(
            {
                "description": description,
                "parameters": parameters if not runs_with_xdist else {},
                "exception": exception if not runs_with_xdist else None,
            }
        )

        return report

    def pytest_deselected(self, items: Sequence[Item]) -> None:
        if len(items) > 0:
            pluginmanager = items[0].config.pluginmanager
            terminal_reporter = pluginmanager.getplugin("terminalreporter")
            if (
                hasattr(terminal_reporter, "state")
                and terminal_reporter.state.suite_total_tests is not None
                and terminal_reporter.state.suite_total_tests > 0
            ):
                terminal_reporter.state.suite_total_tests -= len(items)

    def pytest_runtestloop(self, session):
        reporter = session.config.pluginmanager.getplugin("terminalreporter")
        if reporter:
            reporter.state.suite_total_tests = len(session.items)

    @pytest.mark.trylast
    def pytest_configure(self, config):
        current_reporter = config.pluginmanager.getplugin("terminalreporter")
        config.pluginmanager.unregister(current_reporter)
        terminal_reporter = TerminalReporter(
            current_reporter.config, coverage=self._coverage
        )
        config.pluginmanager.register(terminal_reporter, "terminalreporter")

        if config.pluginmanager.hasplugin("xdist"):
            config.pluginmanager.register(DeferredXdistPlugin())

    def pytest_internalerror(
        self,
        excrepr: "ExceptionRepr",
        excinfo: "ExceptionInfo[BaseException]",
    ) -> Optional[bool]:
        io = StreamOutput(sys.stdout)
        io.set_verbosity(Verbosity.VERY_VERBOSE)
        trace = ExceptionTrace(excinfo.value)

        trace.render(io)

    # Better diffs display
    def pytest_assertrepr_compare(
        self, config: Config, op: "str", left: Any, right: Any
    ):
        if op != "==":
            return

        diff = Diff(width=max(get_terminal_size().columns, 88) - 4)
        output = diff.terminal_diff(left, right)

        formatter = Formatter(config.get_terminal_writer().hasmarkup)

        return [
            formatter.format(
                "<fg=red;options=bold>{}</> <fg=default;options=dark>==</> <fg=green;options=bold>{}</>".format(
                    formatter.escape(repr(left)), formatter.escape(repr(right))
                )
            ),
            "",
        ] + [formatter.format(o) for o in output]
