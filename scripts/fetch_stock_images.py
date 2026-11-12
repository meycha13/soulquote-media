#!/usr/bin/env python3
"""Fetch approved editorial image URLs from manifest with strict host allowlist and cache."""
import json,sys,urllib.request,urllib.parse,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={"assets.science.nasa.gov","images-assets.nasa.gov","science.nasa.gov"}
for file in sorted((ROOT/"cinematic").glob("*.json")):
    manifest=json.loads(file.read_text())
    for i,slide in enumerate(manifest["slides"],1):
        url=slide.get("image_url")
        if not url:continue
        parsed=urllib.parse.urlparse(url)
        if parsed.scheme!="https" or parsed.hostname not in ALLOWED:raise ValueError("Unapproved image host: "+url)
        target=ROOT/"assets"/"stock"/(manifest["slug"]+f"_{i:02}.jpg")
        target.parent.mkdir(parents=True,exist_ok=True)
        req=urllib.request.Request(url,headers={"User-Agent":"IstWirklichSo-Editorial/1.0"})
        with urllib.request.urlopen(req,timeout=35) as response:
            blob=response.read(15_000_001)
        if len(blob)>15_000_000:raise ValueError("Image exceeds 15 MB")
        image=Image.open(io.BytesIO(blob));image.verify()
        image=Image.open(io.BytesIO(blob)).convert("RGB")
        if min(image.size)<500:raise ValueError("Image too small")
        image.save(target,quality=90,optimize=True)
        print("Verified",target.relative_to(ROOT),image.size)
