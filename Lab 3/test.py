##!/usr/bin/env -S /home/pi/Interactive-Lab-Hub/Lab\ 3/.venv/bin/python


# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`
import requests
import json
import board
import digitalio
import argparse
import queue
import sys
import sounddevice as sd

from vosk import Model, KaldiRecognizer

def ask_ai(question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi3:mini", "prompt": question, "stream": False}
    )
    return response.json().get('response', 'No response')

# Use it anywhere!

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

buttonA = digitalio.DigitalInOut(board.D23)    # GPIO23 (PIN 16)
buttonB = digitalio.DigitalInOut(board.D24)    # GPIO24 (PIN 18)
# Use internal pull-ups; buttons then read LOW when pressed.
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

print("Press the A button to ask questions")
while True:
    a_pressed = (buttonA.value == False)

    if a_pressed:
        try:
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, "input")
                # soundfile expects an int, sounddevice provides a float:
                args.samplerate = int(device_info["default_samplerate"])

            if args.model is None:
                model = Model(lang="en-us")
            else:
                model = Model(lang=args.model)

            if args.filename:
                dump_fn = open(args.filename, "wb")
            else:
                dump_fn = None

            with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                    dtype="int16", channels=1, callback=callback):
                print("#" * 80)
                print("Press B button to stop the recording")
                print("Press Ctrl+C to exit")
                print("#" * 80)

                rec = KaldiRecognizer(model, args.samplerate)
                store = []
                while True:
                    b_pressed = (buttonB.value == False)
                    if b_pressed:
                        print("Stopping Recording")
                        break
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        store.append(rec.Result())
                    if dump_fn is not None:
                        dump_fn.write(data)
        except KeyboardInterrupt:
            print("\nDone")
            answer = ask_ai("How should I greet users?")
            print(answer)
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ": " + str(e))
