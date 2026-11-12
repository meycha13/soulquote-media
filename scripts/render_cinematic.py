#!/usr/bin/env python3
"""Cinematic Science carousel renderer. Local assets only; no remote image scraping."""
import json, os, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
ROOT=Path(__file__).resolve().parents[1]
W,H=1080,1350
NAVY=(11,31,59); CREAM=(245,237,224); TURQ=(0,194,199); YELLOW=(255,185,0)
def font(size,bold=False):
    names=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for n in names:
        if Path(n).exists(): return ImageFont.truetype(n,size)
    return ImageFont.load_default()
def wrap(draw,text,f,maxwidth):
    words=text.split(); lines=[]; line=""
    for word in words:
        trial=(line+" "+word).strip()
        if draw.textbbox((0,0),trial,font=f)[2]>maxwidth and line:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines
def render(slide,idx,total,slug):
    image=Image.new("RGB",(W,H),NAVY)
    art=slide.get("image")
    if art:
        path=(ROOT/art).resolve()
        if not path.is_relative_to(ROOT/"assets") or not path.is_file():raise ValueError("image must exist under assets/: "+str(art))
        photo=Image.open(path).convert("RGB")
        image=ImageOps.fit(photo,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.42))
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    # Dark gradient over lower 60%, ensuring contrast on bright photos.
    for y in range(H):
        alpha=int(30+185*(y/H)**1.65)
        d.line((0,y,W,y),fill=(5,13,29,alpha))
    image=Image.alpha_composite(image.convert("RGBA"),overlay)
    d=ImageDraw.Draw(image)
    d.rounded_rectangle((64,72,425,132),radius=12,fill=(0,20,36,215))
    d.text((82,84),"IST WIRKLICH SO?",font=font(32,True),fill=CREAM)
    d.text((898,84),f"{idx:02}/{total:02}",font=font(35,True),fill=CREAM)
    d.rounded_rectangle((68,772,1012,1198),radius=30,fill=(6,21,43,218))
    tag=slide.get("tag","WISSENSCHAFT").upper()
    d.text((102,808),tag,font=font(31,True),fill=TURQ)
    title=slide["title"]
    size=65
    while size>=40:
        f=font(size,True); lines=wrap(d,title,f,860)
        if len(lines)<=3:break
        size-=3
    y=875
    for line in lines:
        d.text((100,y),line,font=f,fill=CREAM,stroke_width=0);y+=size+13
    body=slide.get("body","")
    bf=font(32)
    bodylines=wrap(d,body,bf,860)
    y=max(1054,y+12)
    for line in bodylines[:3]:
        if y>1160:break
        d.text((103,y),line,font=bf,fill=CREAM);y+=42
    d.line((95,1233,985,1233),fill=TURQ,width=5)
    d.text((98,1260),"@istwirklichso",font=font(28,True),fill=TURQ)
    dest=ROOT/"public"/f"{slug}_{idx:02}.jpg";dest.parent.mkdir(parents=True,exist_ok=True)
    image.convert("RGB").save(dest,quality=91,optimize=True)
    print(dest.relative_to(ROOT))
def main():
    p=(ROOT/sys.argv[1]).resolve()
    if not p.is_relative_to(ROOT/"cinematic") or p.suffix!=".json":raise ValueError("manifest must be in cinematic/")
    data=json.loads(p.read_text(encoding="utf-8"))
    slug=data["slug"]
    if not slug.replace("-","").replace("_","").isalnum():raise ValueError("invalid slug")
    slides=data["slides"]
    if len(slides)!=5:raise ValueError("exactly five slides required")
    for i,s in enumerate(slides,1):render(s,i,5,slug)
if __name__=="__main__":main()
