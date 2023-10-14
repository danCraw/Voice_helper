from pathlib import Path

from pyaudio import PyAudio, paInt16
import json
import webbrowser
from fuzzywuzzy import process
from vosk import Model, KaldiRecognizer

model = Model("model")
rate = 16000
rec = KaldiRecognizer(model, rate)
p = PyAudio()
stream = p.open(format=paInt16, channels=1, rate=rate, input=True, frames_per_buffer=8000)
stream.start_stream()


def load_commands_dict(path: Path):
    with open(path, 'r') as file:
        # Загружаем содержимое файла в переменную
        return json.load(file)


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']


search_cmds = load_commands_dict(Path('search_commands.json'))
open_cmds = load_commands_dict(Path('open_commands.json'))
cmds_dict = {'найди': search_cmds, 'включи': open_cmds}

for text in listen():
    print(text)
    found_command, match_percent = process.extractOne(text, list(cmds_dict.keys()))
    print(found_command, match_percent)

    if match_percent > 30:
        command_dict = cmds_dict[found_command]
        requested_command = text
        try:
            requested_command = text.replace(found_command, '')
        except KeyError as e:
            pass
        if command_dict == search_cmds:
            webbrowser.open('http://www.google.com/search?q=' + requested_command)
