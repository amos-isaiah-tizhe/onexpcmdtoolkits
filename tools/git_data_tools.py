#!/usr/bin/env python3
"""Run toolkit data helpers from a single entry point."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = {
    'build': 'build_git_json.py',
    'extract': 'extract_git_commands.py',
    'merge-file': 'merge_git_from_file.py',
    'merge-snapshots': 'merge_git_from_snapshots.py',
    'recover-snapshots': 'recover_from_snapshots.py',
}


def run_script(name: str, args: list[str]) -> int:
    script = ROOT / SCRIPTS[name]
    if not script.exists():
        raise FileNotFoundError(f'Script not found: {script}')

    cmd = [sys.executable, str(script)] + args
    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Utility wrapper for Git command JSON extraction and recovery tools.'
    )
    parser.add_argument(
        'command',
        choices=list(SCRIPTS.keys()),
        help='Tool to run',
    )
    parser.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help='Additional arguments passed to the selected script',
    )

    parsed = parser.parse_args()
    return run_script(parsed.command, parsed.args)


if __name__ == '__main__':
    raise SystemExit(main())
