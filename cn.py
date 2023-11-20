from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import pypinyin
import json
from pydub import AudioSegment

SetLogLevel(0)

if not os.path.exists("vosk-model-cn-0.22"):
	print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'vosk-model-cn-0.22' in the current folder.")
	exit (1)

wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
	print ("Audio file must be WAV format mono PCM.")
	exit (1)

model = Model("vosk-model-cn-0.22")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

workdir = './result/'
if not os.path.exists(workdir):
	os.makedirs(workdir)
threshold = 0.5

def getFilename(character):
	print(character)
	path = workdir + pypinyin.lazy_pinyin(character)[0]
	cnt = 0
	while True:
		now = path + str(cnt) + '.wav'
		if cnt == 0:
			now = path + '.wav'
		if not os.path.exists(now):
			path = now
			break
		cnt += 1
	return path
while True:
	data = wf.readframes(4000)
	if len(data) == 0:
		break
	if rec.AcceptWaveform(data):
		result = json.loads(rec.Result())
		if result["text"] == "":
			continue
		result = result['result']
		for w in result:
			if w["conf"] > threshold and len(w['word']) == 1:
				AudioSegment.from_wav(sys.argv[1])[w["start"]*1000:w["end"]*1000].export(getFilename(w["word"]), format='wav')