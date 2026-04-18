"""CLI subcommand for managing annotations."""
from __future__ import annotations

import argparse

from batchmark.annotator import (
    Annotation, AnnotationError, delete_annotation,
    list_annotations, load_annotation, save_annotation,
)
from batchmark.annotation_formatter import format_annotation_detail, format_annotation_list


def add_annotation_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Manage benchmark annotations")
    sub = p.add_subparsers(dest="annotation_cmd")

    add = sub.add_parser("add", help="Add annotation")
    add.add_argument("suite")
    add.add_argument("branch")
    add.add_argument("note")
    add.add_argument("--tags", nargs="*", default=[])

    show = sub.add_parser("show", help="Show annotation")
    show.add_argument("suite")
    show.add_argument("branch")

    sub.add_parser("list", help="List all annotations")

    rm = sub.add_parser("delete", help="Delete annotation")
    rm.add_argument("suite")
    rm.add_argument("branch")


def run_annotation_command(args: argparse.Namespace, store_dir: str = ".batchmark/annotations") -> int:
    cmd = getattr(args, "annotation_cmd", None)
    if cmd == "add":
        a = Annotation(suite=args.suite, branch=args.branch, note=args.note, tags=args.tags)
        save_annotation(store_dir, a)
        print(f"Annotation saved for {args.suite}@{args.branch}")
        return 0
    if cmd == "show":
        try:
            a = load_annotation(store_dir, args.suite, args.branch)
            print(format_annotation_detail(a))
            return 0
        except AnnotationError as e:
            print(str(e))
            return 1
    if cmd == "list":
        annotations = list_annotations(store_dir)
        print(format_annotation_list(annotations))
        return 0
    if cmd == "delete":
        removed = delete_annotation(store_dir, args.suite, args.branch)
        print("Deleted." if removed else "Not found.")
        return 0 if removed else 1
    print("No annotation subcommand given.")
    return 1
