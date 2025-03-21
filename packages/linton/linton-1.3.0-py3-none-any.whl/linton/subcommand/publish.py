"""Linton 'publish' subcommand

© Reuben Thomas <rrt@sc3d.org> 2024-2025
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import os
import shutil
import subprocess

from linton.warnings_util import die


def run(args: argparse.Namespace) -> None:
    """'publish' command handler"""
    # Check output either does not exist, or is an empty directory, unless
    # --force given.
    if os.path.exists(args.output) and not (
        os.path.isdir(args.output) and len(os.listdir(args.output)) == 0
    ):
        if not args.force:
            die(f"output {args.output} is not an empty directory")
        shutil.rmtree(args.output)

    # Render the project files to the output
    subprocess.check_output(["nancy", args.document_root, args.output])

    # Check links unless disabled.
    output_dir = args.output
    if not output_dir.endswith("/"):
        output_dir += "/"
    if not args.no_check_links:
        subprocess.check_call(["linkchecker", output_dir])


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "publish",
        help="convert a directory of Markdown files and other resources into a web site",
        epilog="The output DIRECTORY cannot be a subdirectory of the input directory.",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="overwrite output directory even if it is not empty",
    )
    parser.add_argument(
        "--base-url",
        metavar="URL",
        help="base URL of web site relative to root of server [default: %(default)s]",
        default="/",
    )
    parser.add_argument(
        "--no-check-links",
        action="store_true",
        help="don't check hyperlinks in the generated site",
    )
    parser.add_argument(
        "document_root", metavar="DIRECTORY", help="directory containing source files"
    )
    parser.add_argument("output", metavar="DIRECTORY", help="output directory")
    parser.set_defaults(func=run)
