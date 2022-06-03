from api import Traffects, Pin
from pynput.keyboard import Key, Listener
import random

api = Traffects("COM8")

def on_press(key):
    pin = random.choice(Pin.range())

    api.blink(pin)

with Listener(on_press=on_press) as listener:
    listener.join()