#!/usr/bin/env python3
"""Create a review issue with five immutable image previews; never publish."""
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import quote
from PIL import Image

def gh(*args, input_text=None):
    p = subprocess.run(["gh", *args], input=input_text, text=True,
                       capture_output=True, check=True)
    return p.stdout.strip()

slug = os.environ["SLUG"]
source = os.environ["SOURCE"]
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", slug):
    raise SystemExit("Invalid carousel slug")
if source not in ("public", "ready"):
    raise SystemExit("Invalid source")
if source == "public":
    paths = [Path("public") / f"{slug}_{i:02}.jpg" for i in range(1, 6)]
else:
    paths = [Path("ready") / slug / f"{i:02}.jpg" for i in range(1, 6)]
for p in paths:
    if not p.is_file() or p.stat().st_size > 8_000_000:
        raise SystemExit(f"Missing or oversized slide: {p}")
    with Image.open(p) as im:
        if im.format != "JPEG" or im.size != (1080, 1350):
            raise SystemExit(f"Invalid slide format: {p}")
repo = os.environ["GH_REPO"]
sha = os.environ["REF_SHA"]
label = "carousel-review"
# Ensure review label exists without overwriting existing label configuration.
existing = gh("label", "list", "--repo", repo, "--json", "name")
if label not in [v["name"] for v in json.loads(existing)]:
    gh("label", "create", label, "--repo", repo, "--color", "0e8a16",
       "--description", "Carousel awaiting owner approval")
# Do not create a second pending review for the same carousel.
issues = json.loads(gh("issue", "list", "--repo", repo, "--state", "open",
                       "--label", label, "--limit", "100", "--json", "body"))
marker = f"Carousel: {slug}\nSource: {source}"
if any(marker in issue["body"] for issue in issues):
    raise SystemExit("A review for this carousel is already open")
lines = [
    f"## Bildfreigabe: {slug}", "",
    "Bitte alle fünf Bilder prüfen. Wissenschaftliche Aussagen und Caption müssen",
    "vor der Freigabe ebenfalls redaktionell geprüft werden.", "",
    f"Carousel: {slug}", f"Source: {source}", f"Commit: {sha}", "",
    "### Vorschau (unveränderlicher Commit)", "",
]
for i, p in enumerate(paths, 1):
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{quote(p.as_posix(), safe='/')}"
    lines.extend([f"**Slide {i:02} / 05**", f"![Slide {i:02}]({url})", ""])
lines.extend([
    "### Entscheidung", "",
    "Nach Sichtprüfung als Repository-Eigentümer exakt `/freigeben` kommentieren.",
    "Bei Korrekturen stattdessen Wünsche kommentieren; nichts wird veröffentlicht.",
    "",
    "**Hinweis:** Diese Freigabe startet nur den Cloudinary-Upload.",
    "Die Metricool-Veröffentlichung ist noch nicht automatisiert.",
])
url = gh("issue", "create", "--repo", repo, "--title",
         f"Karussell-Freigabe: {slug}", "--label", label,
         "--body-file", "-", input_text="\n".join(lines))
print("Review created:", url)
