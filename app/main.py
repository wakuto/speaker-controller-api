import re
import toml
import subprocess
from fastapi import FastAPI

sound_dir = "/home/wakuto/sound/"

# get device list
dev_list_str = subprocess.check_output("pacmd list-sinks | grep name:", shell=True)
pattern = b'<[^>]+>'
dev_list = re.findall(pattern, dev_list_str)
dev_list = [re.sub(b'<|>', b'', x) for x in dev_list]
print(dev_list)

# get place list
place_list = toml.load(open('./speaker_conf.toml'))
print(place_list['place'].keys())

# get sounds list
sounds_list_str = subprocess.check_output("ls ~/sound", shell=True)
pattern = b'[^\n]+'
sounds_list = re.findall(pattern, sounds_list_str)
print(sounds_list)

app = FastAPI()

# デバイスに関連付けられた場所の名前を返す
@app.get("/devices")
async def devices():
  return {"devices": place_list['place'].keys()}

# return sound file list
@app.get("/sounds")
async def sounds():
  return {"sounds": sounds_list}

# {place_name}でsound_nameを再生
@app.get("/sounds/{place_name}")
async def play_sound(place_name: str, sound_name: str):
  sound_name = sound_dir + sound_name
  try:
    subprocess.Popen(["/home/wakuto/src/speaker_controller/speaker-controller", sound_name, place_list['place'][place_name]], encoding='UTF-8')
  except:
    pass
  return {"status", "OK"}
