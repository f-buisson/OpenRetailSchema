# SPDX-License-Identifier: Apache-2.0
"""Reusable conformance checks for vendor-neutral read connectors.

Adapter tests provide a synthetic factory; this module owns the common contract
assertions so future POS connectors do not reimplement them differently.
"""
from __future__ import annotations

from connectors.capabilities import validate_capability_manifest
from connectors.operations import (
    COMMON_READ_OPERATIONS,
    UndeclaredOperationError,
    UnsupportedOperationError,
)


def exercise_read_connector(testcase, factory) -> None:
    """Exercise one connector against the common read-operation contract.

    ``factory(operation)`` must return ``(connector, expected, calls)`` using
    synthetic transport data. ``operation`` is ``None`` for checks that must not
    reach transport. Supported operations must return ``expected``. Explicitly
    unsupported operations must fail before transport.
    """
    connector, _, calls = factory(None)
    validate_capability_manifest(connector.manifest)

    declarations = connector.manifest["capabilities"]
    missing = COMMON_READ_OPERATIONS.difference(declarations)
    testcase.assertEqual(missing, set(), "all common reads must be declared explicitly")

    for operation in sorted(COMMON_READ_OPERATIONS):
        support = declarations[operation]["support"]
        connector, expected, calls = factory(operation)
        if support == "supported":
            testcase.assertEqual(connector.read(operation), expected)
        elif support == "unsupported":
            with testcase.assertRaises(UnsupportedOperationError):
                connector.read(operation)
            testcase.assertEqual(calls, [], "unsupported operations must not reach transport")
        else:  # manifest validation should make this unreachable
            testcase.fail(f"invalid support declaration for {operation}")

    connector, _, calls = factory(None)
    with testcase.assertRaisesRegex(ValueError, "unknown_common_read_operation"):
        connector.read("conformance.unknown")
    testcase.assertEqual(calls, [], "unknown operations must not reach transport")


def assert_undeclared_operation_fails_closed(testcase, manifest: dict) -> None:
    """Reusable negative check for manifests that omit a common operation."""
    from connectors.operations import require_read_operation

    missing = next((op for op in COMMON_READ_OPERATIONS if op not in manifest["capabilities"]), None)
    if missing is None:
        testcase.fail("fixture must omit at least one common read operation")
    with testcase.assertRaises(UndeclaredOperationError):
        require_read_operation(manifest, missing)
