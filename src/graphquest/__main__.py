"""CLI entry point (V3 §4.1 — thin shell, all logic via the SDK).

Usage:
    uv run python -m graphquest <command>

Commands: clone | graphify | reverse | debug | benchmark | all
The CLI only parses args and prints results; it contains no business logic.
"""

from __future__ import annotations

import argparse

from graphquest import GraphQuestSDK

_COMMANDS = ("clone", "graphify", "reverse", "debug", "benchmark", "all")


def main(argv: list[str] | None = None) -> int:
    """Parse the command and dispatch to the SDK."""
    parser = argparse.ArgumentParser(prog="graphquest", description=__doc__)
    parser.add_argument("command", choices=_COMMANDS)
    args = parser.parse_args(argv)

    with GraphQuestSDK() as sdk:
        _dispatch(sdk, args.command)
        print(f"cost so far: ${sdk.total_cost_usd:.4f}")
    return 0


def _dispatch(sdk: GraphQuestSDK, command: str) -> None:
    """Run one CLI command against the SDK facade."""
    raise NotImplementedError("Phase 2: wire commands to SDK methods")


if __name__ == "__main__":
    raise SystemExit(main())
