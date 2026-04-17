"""CLI sub-command handlers for tag management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from batchmark.tagger import TaggerError, delete_tag, list_tags, load_tag, save_tag
from batchmark.tag_formatter import format_tag_detail, format_tag_list


def add_tag_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("tag", help="Manage run tags")
    sub = p.add_subparsers(dest="tag_cmd", required=True)

    s = sub.add_parser("save", help="Save a tag")
    s.add_argument("name", help="Tag name")
    s.add_argument("branch", help="Branch name")

    sub.add_parser("list", help="List saved tags")

    sh = sub.add_parser("show", help="Show tag details")
    sh.add_argument("name", help="Tag name")

    d = sub.add_parser("delete", help="Delete a tag")
    d.add_argument("name", help="Tag name")


def run_tag_command(args: argparse.Namespace, base_dir: Path | None = None) -> int:
    kwargs = {"base": base_dir} if base_dir else {}
    try:
        if args.tag_cmd == "save":
            path = save_tag(args.name, args.branch, **kwargs)
            print(f"Tag '{args.name}' saved to {path}")
        elif args.tag_cmd == "list":
            names = list_tags(**kwargs)
            print(format_tag_list(names))
        elif args.tag_cmd == "show":
            entry = load_tag(args.name, **kwargs)
            print(format_tag_detail(entry))
        elif args.tag_cmd == "delete":
            delete_tag(args.name, **kwargs)
            print(f"Tag '{args.name}' deleted.")
    except TaggerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
