import os, math, wave, struct, subprocess
from PIL import Image
os.makedirs("week1",exist_ok=True)
# Original slow ambient instrumental: layered soft chord tones and a repeating bell melody.
rate=24000
seconds=12
notes=[(196,0.12),(246.94,0.09),(293.66,0.08),(392,0.05)]
melody=[(0,392),(2.5,440),(5,369.99),(7.5,329.63),(10,392)]
with wave.open("week1/reel_ambient.wav","wb") as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
 for i in range(rate*seconds):
  t=i/rate
  envelope=min(1,t/1.4,(seconds-t)/1.8)
  v=0
  for freq,amp in notes:
   v+=amp*math.sin(2*math.pi*freq*t+0.13*math.sin(t*.3))
  for start,freq in melody:
   dt=t-start
   if 0<=dt<2.5:
    v+=.15*math.exp(-dt*1.4)*math.sin(2*math.pi*freq*dt)
  v*=max(0,envelope)*.68
  w.writeframesraw(struct.pack("<h",int(max(-1,min(1,v))*32767)))
# Visible continuous push-in + horizontal drift. Reuse atmospheric photo/text still.
subprocess.run(["ffmpeg","-y","-loop","1","-framerate","25","-i","week1/friday.jpg","-i","week1/reel_ambient.wav","-filter_complex","[0:v]scale=1440:1800,zoompan=z='min(zoom+0.0008,1.22)':x='(iw-iw/zoom)/2+35*sin(on/75)':y='(ih-ih/zoom)/2':d=300:s=720x900:fps=25,eq=brightness=0.01:saturation=1.07,format=yuv420p[v]","-map","[v]","-map","1:a","-t","12","-c:v","libx264","-preset","medium","-crf","21","-c:a","aac","-b:a","160k","-movflags","+faststart","week1/friday_reel_v2.mp4"],check=True)
print("Reel ready",os.path.getsize("week1/friday_reel_v2.mp4"))
