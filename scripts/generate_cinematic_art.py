#!/usr/bin/env python3
"""Generate original cinematic astronomical illustrations using Pillow (no external API)."""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import random, math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"generated"
OUT.mkdir(parents=True,exist_ok=True)
W,H=1080,1350
def scene(n):
    rng=random.Random(2190+n)
    im=Image.new("RGB",(W,H)); px=im.load()
    for y in range(H):
        for x in range(W):
            v=(1-y/H)*.4; px[x,y]=(int(4+9*v),int(11+19*v),int(27+31*v))
    stars=Image.new("RGBA",(W,H));d=ImageDraw.Draw(stars)
    for k in range(350):
        x=rng.randrange(W);y=rng.randrange(820);r=rng.choice([1,1,1,2,3])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(190,226,255,rng.randint(90,220)))
    im=Image.alpha_composite(im.convert("RGBA"),stars)
    glow=Image.new("RGBA",(W,H));g=ImageDraw.Draw(glow)
    cx,cy=(560,390) if n!=3 else (460,390)
    if n==2:
        for k in range(95):
            angle=rng.random()*math.tau;dist=rng.random()*350
            x=cx+math.cos(angle)*dist;y=cy+math.sin(angle)*dist
            r=rng.randrange(10,75)
            g.ellipse((x-r,y-r,x+r,y+r),fill=(255,rng.randint(70,160),20,rng.randint(15,90)))
    for radius in range(250,45,-4):
        a=int(2+18*(1-radius/250)**2)
        g.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(0,194,255,a))
    if n==4:
        for k in range(105):
            x=rng.randrange(60,1020);y=rng.randrange(160,720);r=rng.randrange(8,27)
            g.ellipse((x-r,y-r,x+r,y+r),fill=(28,110,190,190),outline=(88,227,255,180),width=2)
    else:
        for radius in range(130,55,-2):
            g.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(0,160,255,55),width=3)
        g.ellipse((cx-80,cy-80,cx+80,cy+80),fill=(12,101,198,255),outline=(158,244,255,255),width=8)
        for k in range(20):
            a=rng.random()*math.tau;r=rng.randrange(95,200)
            x=cx+math.cos(a)*r;y=cy+math.sin(a)*r
            g.line((cx,cy,x,y),fill=(30,174,255,100),width=rng.randint(2,6))
    im=Image.alpha_composite(im,glow.filter(ImageFilter.GaussianBlur(16)))
    im=Image.alpha_composite(im,glow)
    if n in (1,5):
        spoon=Image.new("RGBA",(W,H));s=ImageDraw.Draw(spoon)
        s.ellipse((210,570,590,660),fill=(116,153,183,220),outline=(226,245,255,255),width=7)
        s.line((555,610,1010,525),fill=(178,207,229,245),width=23)
        s.line((555,600,1010,515),fill=(248,252,255,230),width=5)
        im=Image.alpha_composite(im,spoon)
    return im.convert("RGB")
for n in range(1,6):
    p=OUT/f"neutron_{n:02}.jpg"
    scene(n).save(p,quality=91,optimize=True)
    print(p.relative_to(ROOT))
