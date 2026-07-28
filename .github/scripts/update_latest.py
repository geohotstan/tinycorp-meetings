#!/usr/bin/env python3
import re, sys, os

base_dir = "last-week-in-tinycorp"
dirs = sorted(
    [
        d
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("20")
    ],
    reverse=True,
)[:4]

lines = "".join(f"- [{d}]({base_dir}/{d}/meeting-transcript.md)\n" for d in dirs)
section = f"## Latest\n\n{lines}"

with open("README.md", "r") as f:
    content = f.read()

new_content = re.sub(
    r"(<!-- LATEST_START -->).*?(<!-- LATEST_END -->)",
    r"\1\n" + section + r"\n\2",
    content,
    flags=re.DOTALL,
)

with open("README.md", "w") as f:
    f.write(new_content)
