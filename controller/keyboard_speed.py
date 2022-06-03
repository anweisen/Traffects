from pynput.keyboard import Key, Listener
from api import Traffects, Pin
import numpy
import threading
import time

api = Traffects("COM4")

global counter, tracker, period, timer
counter = 0
tracker = list()
timer = .25
period = 1.25

def on_release(key):
    global counter
    counter = counter + 1

def check():
    global counter, tracker
    tracker.insert(0, counter)
    counter = 0

    while len(tracker) > period:
        del tracker[-1]

    sum = numpy.sum(tracker)
    pm = 60 / period * timer * sum

    #print(pm)

    pins = set()
    blink = set()
    if pm >= 1:
        pins.add(Pin.GREEN)
    if pm >= 15:
        pins.add(Pin.YELLOW)
    if pm >= 30:
        pins.add(Pin.RED)
    if pm >= 35:
        blink.add(Pin.RED)
    if pm >= 40:
        blink.add(Pin.YELLOW)
    if pm >= 50:
        blink.add(Pin.GREEN)

    for pin in Pin.range():
        if pin in blink:
            api.blink(pin)
        else:
            api.set(pin, pin in pins)


def loop():
    while True:
        time.sleep(timer)
        check()

threading.Thread(target=loop).start()

with Listener(on_release=on_release) as listener:
    listener.join()
