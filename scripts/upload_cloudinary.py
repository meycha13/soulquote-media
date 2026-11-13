#!/usr/bin/env python3
"""Validate and upload one finished five-slide carousel to Cloudinary."""
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from PIL import Image

def main():
    slug = os.environ["CAROUSEL_SLUG"].strip()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", slug):
        raise ValueError("Carousel slug must contain only letters, numbers, hyphens and underscores")
    source = os.environ.get("CAROUSEL_SOURCE", "public")
    if source == "ready":
        folder = Path("ready") / slug
        paths = [folder / f"{i:02}.jpg" for i in range(1, 6)]
        if not folder.is_dir() or sorted(p.name for p in folder.iterdir() if p.is_file()) != [p.name for p in paths]:
            raise ValueError(f"Expected exactly ready/{slug}/01.jpg through 05.jpg")
    elif source == "public":
        paths = [Path("public") / f"{slug}_{i:02}.jpg" for i in range(1, 6)]
        if not all(p.is_file() for p in paths):
            raise ValueError(f"Expected five images public/{slug}_01.jpg through {slug}_05.jpg")
    else:
        raise ValueError("CAROUSEL_SOURCE must be public or ready")
    for path in paths:
        if path.stat().st_size > 8_000_000:
            raise ValueError(f"{path} exceeds 8MB")
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            if im.format != "JPEG" or im.size != (1080, 1350):
                raise ValueError(f"{path} must be JPEG 1080x1350")
    cloud = os.environ["CLOUDINARY_CLOUD_NAME"]
    key = os.environ["CLOUDINARY_API_KEY"]
    secret = os.environ["CLOUDINARY_API_SECRET"]
    batch = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
    destination = f"istwirklichso/{slug}/{batch}"
    results = []
    for index, path in enumerate(paths, 1):
        params = {
            "folder": destination,
            "overwrite": "false",
            "public_id": f"{index:02}",
            "timestamp": str(int(time.time())),
        }
        signing = "&".join(f"{k}={params[k]}" for k in sorted(params))
        params["signature"] = hashlib.sha1((signing + secret).encode()).hexdigest()
        params["api_key"] = key
        boundary = "----cloudinary" + uuid.uuid4().hex
        body = bytearray()
        for name, value in params.items():
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(f"\r\n--{boundary}--\r\n".encode())
        req = urllib.request.Request(
            f"https://api.cloudinary.com/v1_1/{urllib.parse.quote(cloud, safe='')}/image/upload",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Cloudinary rejected slide {index:02} (HTTP {exc.code}); check credentials and account settings") from None
        url = payload.get("secure_url", "")
        if not url.startswith("https://res.cloudinary.com/"):
            raise RuntimeError("Cloudinary did not return a valid HTTPS media URL")
        results.append({"slide": index, "url": url})
        print(f"Uploaded slide {index:02}")
    output = Path("cloudinary-upload-results.json")
    output.write_text(json.dumps({"slug": slug, "slides": results}, indent=2) + "\n", encoding="utf-8")
    print("Upload complete. URLs are available in the workflow artifact.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        sys.exit(1)
