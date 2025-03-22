#!/usr/bin/env python3

# /// script
# requires-python = ">=3.9"
# ///

import os.path
import sys
import urllib.parse


# Get command-line arguments
page = sys.argv[1]

# Extract page name and normalize path
path = os.path.dirname(page)
if path == ".":
    path = ""
parents = path.removesuffix("$")

# Generate and print breadcrumb
desc = os.path.basename(parents)
tree = ""
classes = "breadcrumb-item breadcrumb-active"
while parents not in ("", ".", "/"):
    quoted_parents = urllib.parse.quote(parents)
    tree = f'<li class="{classes}">' + \
        f'<a href="$run(path-to-root.in.py,$path)/{quoted_parents}/index.html">{desc}</a>' + \
        f'</li>{tree}'
    classes = "breadcrumb-item"
    parents = os.path.dirname(parents)
    desc = os.path.basename(parents)
print(
    '<li class="breadcrumb-item">' + \
    '<a href="$run(path-to-root.in.py,$path)/index.html">$include(Title.in.txt)</a>' + \
    f'</li>{tree}'
)
