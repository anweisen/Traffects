import speech_recognition as sr
from api import Traffects, Pin

r = sr.Recognizer()
api = Traffects("COM4")

def handle(text: str):
    print(text)
    if text in ["rot"]:
        api.set(Pin.RED, not api.get(Pin.RED))
    if text in ["gelb"]:
        api.set(Pin.YELLOW, not api.get(Pin.YELLOW))
    if text in ["grün"]:
        api.set(Pin.GREEN, not api.get(Pin.GREEN))
    if text in ["alle", "an"]:
        for pin in Pin.range():
            api.set(pin, True)
    if text in ["aus"]:
        for pin in Pin.range():
            api.set(pin, False)

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)

    while True:

        try:
            audio = r.listen(source, phrase_time_limit=.75)
            dest = r.recognize_google(audio, language="de-DE")
            handle(dest)
        except sr.UnknownValueError as ex:
            pass
        except Exception as ex:
            print("Error : " + ex)
