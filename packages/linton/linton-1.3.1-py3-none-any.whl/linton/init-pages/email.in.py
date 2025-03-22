#!/usr/bin/env python3

# /// script
# requires-python = ">=3.9"
# ///

import sys
from typing import Optional


# Read command-line arguments
def maybe_argv(n: int) -> Optional[str]:
    return sys.argv[n] if len(sys.argv) > n else None


text = maybe_argv(1) or "$include(Email.in.txt)"
link_class = maybe_argv(2)
class_text = f' class="{link_class}"' if link_class else ""

print(f'<a{class_text} href="mailto:$include(Email.in.txt)">{text}</a>', end="")
