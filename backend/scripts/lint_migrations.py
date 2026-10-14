"""Write the PostgreSQL SQL of each new revision to a directory for squawk.

A contract migration (rule M-5, release N+1) is allowed to drop what release N
stopped using. It says so with a module-level `squawk_ignore = ["rule", ...]`,
which becomes a squawk-ignore-file header on that revision's SQL only.
"""
import argparse
import io
import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", help="revision already on the base branch; omit to lint every revision")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    os.environ["DB_TYPE"] = "postgres"
    backend_dir = Path(__file__).resolve().parent.parent
    config = Config(str(backend_dir / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)

    revisions = list(scripts.iterate_revisions("heads", args.since or "base"))
    if args.since:
        revisions = [r for r in revisions if r.revision != args.since]
    args.out.mkdir(parents=True, exist_ok=True)

    for revision in reversed(revisions):
        buffer = io.StringIO()
        config.output_buffer = buffer
        start = revision.down_revision or "base"
        command.upgrade(config, f"{start}:{revision.revision}" if start != "base" else revision.revision, sql=True)
        ignored = getattr(revision.module, "squawk_ignore", [])
        header = f"-- squawk-ignore-file {', '.join(ignored)}\n" if ignored else ""
        (args.out / f"{revision.revision}.sql").write_text(header + buffer.getvalue())

    print(f"{len(revisions)} revision(s) written to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
