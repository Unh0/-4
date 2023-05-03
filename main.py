import json, os
import pyttsx3, vosk, pyaudio, requests

tts = pyttsx3.init()
voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    if voice.name == 'Microsoft David Desktop - English (UnitedStates)':
        tts.setProperty('voice', voice.id)
model = vosk.Model('vosk-model-small-ru-0.4')

record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()


nebo = {"☀": 'солнечно', '☁': 'облачно', '☂️': 'дождь', '☃️': 'снег'}
veter = {'↑️': 'северный', '↗': 'северо-восточный', '→': 'восточный', '↘️': 'юго-восточный',
         '↓️': 'южный', '↙': 'юго-западный', '️←': 'западный', '↖️': 'северо-южный'}

def pogoda():
    req = requests.get('https://wttr.in/Saint-Petersburg?format=2')
    data = req.text
    # print(data[0])
    pog = {}
    for c in data:
        if c in nebo.keys():
            pog['на улице'] = nebo[c]
    pog['температура'] = data[data.index('🌡️') + 1:data.index('C')]
    pog['ветер'] = veter[data[data.index('C') + 4]]
    pog['скорость'] = data[data.index('C') + 5:data.index('k')]
    return pog


print('start')
pwd = ''
pog = pogoda()
for text in listen():
    if text == 'закрыть':
        quit()
    elif text == 'погода':
        pog = pogoda()
        print(str(pog) + " километров в час")
        speak(str(pog) + " километров в час")
    elif text == 'ветер':
        pog = pogoda()
        print(pog['ветер'], pog['скорость'])
        speak("ветер сегодня " + pog['ветер'] + "скорость" + pog['скорость'] + " километров в час")
    elif text == 'прогулка':
        pog = pogoda()
        if int(pog['температура'][1:-1]) < 5 or int(pog['скорость']) > 15:
            speak("гулять не рекомендуется")
        else:
            speak("гулять рекомендуется")
    elif text == 'сохранить':
        pog = pogoda()
        with open('result.txt', 'w', encoding="utf-8") as f:
            f.write(requests.get('https://wttr.in/Saint-Petersburg?format=2').text)
            speak('погода сохранена')
    else:
        print(text)
