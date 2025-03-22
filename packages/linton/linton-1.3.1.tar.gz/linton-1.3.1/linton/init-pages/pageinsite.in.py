#!/usr/bin/env python3

# /// script
# requires-python = ">=3.9"
# ///

import os.path
import sys


# Get command-line arguments
page = sys.argv[1]

pagename = os.path.dirname(page)
if pagename != "":
    print(f": {pagename}", end="")
