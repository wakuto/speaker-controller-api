import re
import toml
import subprocess
from fastapi import FastAPI
import socket

# get place list
place_list = toml.load(open('./speaker_conf.toml'))['place']
print(place_list.keys())

# get sounds list
sounds_list_str = subprocess.check_output("ls ~/sound", shell=True)
pattern = b'[^\n]+'
sounds_list = re.findall(pattern, sounds_list_str)
print(sounds_list)

app = FastAPI()

# デバイスに関連付けられた場所の名前を返す
@app.get("/devices")
async def devices():
  return {"devices": list(place_list.keys())}

# return sound file list
@app.get("/sounds")
async def sounds():
  return {"sounds": sounds_list}

# {place_name}でsound_nameを再生
@app.post("/sounds/{place_name}/{sound_name}")
async def play_sound(place_name: str, sound_name: str):
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((place_list[place_name], 12345))
      s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      s.send(bytes('play ' + sound_name, 'utf-8'))
    return {"status": "OK"}
  except:
    return {"status": "Speaker play failed"}

# /stop de oto wo tomeru
@app.post("/stop")
async def stop_sound():
  # for all server
  failed = False
  for serv in set(place_list.values()):
    try:
        print(serv)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.connect((serv, 12345))
          s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

          s.send(bytes('stop', 'utf-8'))
    except:
      failed = True
  if failed:
    return {"status": "Speaker stop failed"}
  else:
    return {"status": "stop complete"}
