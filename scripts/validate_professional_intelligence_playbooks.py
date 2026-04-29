#!/usr/bin/env python3
"""Validate Professional Intelligence playbooks.

This script validates every YAML file under `playbooks/professional-intelligence/`
against `schemas/professional-intelligence-playbook.schema.json` and performs a
few cross-field checks that are easier to express in code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/professional-intelligence-playbook.schema.json"
PLAYBOOK_DIR = ROOT / "playbooks/professional-intelligence"


def load_dependencies() -> tuple[Any, Any]:
    try:
        import yaml  # type: ignore
        import jsonschema  # type: ignore
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependency"
        print(
            f"ERR: missing Python dependency {missing!r}; install with `python3 -m pip install pyyaml jsonschema`",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    return yaml, jsonschema


def load_schema() -> dict[str, Any]:
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"ERR: missing schema: {SCHEMA_PATH.relative_to(ROOT)}", file=sys.stderr)
        raise SystemExit(2) from exc
    except json.JSONDecodeError as exc:
        print(f"ERR: invalid schema JSON: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def validate_cross_fields(path: Path, data: dict[str, Any]) -> None:
    metadata = data.get("metadata", {})
    playbook_id = metadata.get("id")
    if not isinstance(playbook_id, str) or not playbook_id:
        raise ValueError("metadata.id must be a non-empty string")

    expected_stem = path.stem
    if playbook_id != expected_stem:
        raise ValueError(f"metadata.id {playbook_id!r} must match filename stem {expected_stem!r}")

    owner_repos = metadata.get("ownerRepos", [])
    if not owner_repos or not all(isinstance(item, str) and item.startswith("SocioProphet/") for item in owner_repos):
        raise ValueError("metadata.ownerRepos must contain SocioProphet repo names")

    steps = data.get("steps", [])
    if not steps:
        raise ValueError("steps must not be empty")

    step_ids = [step.get("id") for step in steps if isinstance(step, dict)]
    if len(step_ids) != len(set(step_ids)):
        raise ValueError("step ids must be unique")

    acceptance = data.get("acceptance", {})
    required_evidence = acceptance.get("requiredEvidence", [])
    if not required_evidence:
        raise ValueError("acceptance.requiredEvidence must not be empty")

    kpis = acceptance.get("kpis", [])
    if not kpis:
        raise ValueError("acceptance.kpis must not be empty")

    policy_checks = data.get("policyChecks", [])
    if not policy_checks:
        raise ValueError("policyChecks must not be empty")

    agent_roles = data.get("agentRoles", [])
    if not agent_roles:
        raise ValueError("agentRoles must not be empty")



def main() -> int:
    yaml, jsonschema = load_dependencies()
    schema = load_schema()

    playbooks = sorted(PLAYBOOK_DIR.glob("*.yaml"))
    if not playbooks:
        print(f"ERR: no playbooks found under {PLAYBOOK_DIR.relative_to(ROOT)}", file=sys.stderr)
        return 2

    failures: list[str] = []
    for path in playbooks:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=data, schema=schema)
            validate_cross_fields(path, data)
            print(f"ok: {path.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001 - validation command should aggregate failures
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    if failures:
        print("Professional Intelligence playbook validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 2

    print("Professional Intelligence playbook validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
