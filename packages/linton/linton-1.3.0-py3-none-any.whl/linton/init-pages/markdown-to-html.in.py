#!/usr/bin/env python3
# Convert given Markdown file to HTML fragment on stdout

# /// script
# requires-python = ">=3.9"
# ///

import subprocess
import sys


subprocess.check_call(
    ["markdown", "-f", "footnote,nopants,noalphalist,nostyle,fencedcode", *sys.argv[1:]]
)
