"""CLI entry point for cicd-init."""

import argparse
import json
import sys

from cicd_init import __version__
from cicd_init.detect import detect_project
from cicd_init.generator import generate


def cmd_detect(args):
    """Detect and display project info."""
    config = detect_project(args.dir)
    print(json.dumps(config, indent=2, ensure_ascii=False))


def cmd_init(args):
    """Generate CI/CD config."""
    platforms = ["gitlab", "github"] if args.all else ([args.platform] if args.platform else None)
    try:
        generated = generate(
            project_dir=args.dir,
            platforms=platforms,
            dry_run=args.dry_run,
            node_version=args.node_version,
            simple=args.simple,
        )
        if generated:
            print(f"\n🎉 Done! Generated {len(generated)} file(s).")
            print("   Commit and push to enable CI/CD.")
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="cicd-init",
        description="Auto-detect frontend project and generate GitLab CI / GitHub Actions config.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Generate CI/CD config")
    init_parser.add_argument("-d", "--dir", default=".", help="Project root directory (default: current)")
    init_parser.add_argument(
        "-p", "--platform",
        choices=["gitlab", "github"],
        help="Force platform (auto-detect by default)",
    )
    init_parser.add_argument(
        "--all",
        action="store_true",
        help="Generate both GitLab CI and GitHub Actions configs",
    )
    init_parser.add_argument(
        "--simple",
        action="store_true",
        help="Generate minimal config: install + build only (no lint/test/typecheck)",
    )
    init_parser.add_argument(
        "--node-version",
        metavar="MAJOR",
        help="Override Node.js major version (e.g. 18)",
    )
    init_parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    init_parser.set_defaults(func=cmd_init)

    # detect command
    detect_parser = subparsers.add_parser("detect", help="Detect and display project info")
    detect_parser.add_argument("-d", "--dir", default=".", help="Project root directory (default: current)")
    detect_parser.set_defaults(func=cmd_detect)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
