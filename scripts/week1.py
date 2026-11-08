import os, io, math, textwrap, urllib.request, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H=1080,1350
os.makedirs("week1",exist_ok=True)
photos=[
"https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=1400&q=88",
"https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1400&q=88",
"https://images.unsplash.com/photo-1500534623283-312aade485b7?w=1400&q=88",
"https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=1400&q=88",
"https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1400&q=88",
"https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=1400&q=88"]
def font(size):
 for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"]:
  if os.path.exists(p): return ImageFont.truetype(p,size)
 return ImageFont.load_default()
def background(n):
 try:
  req=urllib.request.Request(photos[n%len(photos)],headers={"User-Agent":"Mozilla/5.0"})
  with urllib.request.urlopen(req,timeout=25) as r: im=Image.open(io.BytesIO(r.read())).convert("RGB")
  scale=max(W/im.width,H/im.height); nw,nh=int(im.width*scale),int(im.height*scale)
  im=im.resize((nw,nh),Image.Resampling.LANCZOS)
  im=im.crop(((nw-W)//2,(nh-H)//2,(nw+W)//2,(nh+H)//2))
 except Exception as e:
  print("photo fallback",n,str(e)); im=Image.new("RGB",(W,H),(22,35,62))
  d=ImageDraw.Draw(im)
  for y in range(H):
   d.line((0,y,W,y),fill=(18+int(y/H*42),32+int(y/H*30),62+int(y/H*22)))
 return ImageEnhance.Color(im).enhance(.72)
def make(name,heading,body,n):
 im=background(n).convert("RGBA")
 shade=Image.new("RGBA",(W,H),(5,12,28,0)); d=ImageDraw.Draw(shade)
 for y in range(H):
  alpha=int(55+115*(1-abs(y-H*.52)/(H*.52)))
  d.line((0,y,W,y),fill=(4,12,28,max(35,min(175,alpha))))
 im=Image.alpha_composite(im,shade)
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((70,390,1010,990),radius=32,fill=(8,18,35,135))
 def write(txt,y,size,maxw,spacing=20):
  f=font(size); words=txt.split(); lines=[]; line=""
  for word in words:
   cand=(line+" "+word).strip()
   if d.textbbox((0,0),cand,font=f)[2]>maxw and line: lines.append(line);line=word
   else: line=cand
  if line:lines.append(line)
  height=len(lines)*(size+spacing)
  for j,s in enumerate(lines):
   box=d.textbbox((0,0),s,font=f); tw=box[2]-box[0]
   d.text(((W-tw)//2,y+j*(size+spacing)),s,font=f,fill=(255,246,226,255))
  return height
 hh=write(heading,460,57,830,17)
 write(body,485+hh+38,34,820,18)
 d.text((W//2-100,1250),"S O U L Q U O T E",font=font(20),fill=(242,231,214,230))
 im.convert("RGB").save("week1/"+name+".jpg",quality=91,optimize=True)
posts=[
("monday",["You are allowed to grow","at your own pace."],0),
("tuesday",[
["5 Things You Can Stop Apologizing For","Your peace does not need permission."],
["Taking time to rest","Rest is a need, not something you have to earn."],
["Setting a boundary","Saying no can be an act of self-respect."],
["Changing your mind","Growth sometimes means choosing a different path."],
["Having feelings","Your emotions deserve compassion, not shame."],
["Being yourself","You do not owe anyone a smaller version of you."]],1),
("thursday",[
["4 Signs You Are Growing Stronger","Even if you cannot see it yet."],
["You pause before reacting","You give yourself room to respond with intention."],
["You ask for what you need","Your voice matters, even when it shakes."],
["You let some things go","Not every battle deserves your energy."],
["You trust your own pace","You no longer measure every step against others."],
["Strength can be gentle","Save this for a day when you forget how far you have come."]],2),
("friday",["You don't have to have it all figured out.","Just take the next gentle step."],3)]
make("monday",*posts[0][1],0)
for day,slides,index in [posts[1],posts[2]]:
 for i,(h,b) in enumerate(slides):make(f"{day}_{i+1:02d}",h,b,index+i)
make("friday",*posts[3][1],5)
subprocess.run(["ffmpeg","-y","-loop","1","-framerate","25","-i","week1/friday.jpg","-t","9","-vf","scale=1080:1350,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","23","-movflags","+faststart","week1/friday.mp4"],check=True)
print("generated",os.listdir("week1"))
