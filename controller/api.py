from asyncio import constants
from enum import Enum
import serial
import time
import threading
import functools

def convert_data(data: int) -> bytes :
  return data.to_bytes(1, byteorder="big", signed=data < 0)

# Create a @synchronized annotation like the keyword in java
def synchronized(wrapped):
  lock = threading.Lock()
  @functools.wraps(wrapped)
  def _wrap(*args, **kwargs):
      with lock:
          return wrapped(*args, **kwargs)
  return _wrap

class Pin:
  GREEN = 0
  YELLOW = 1
  RED = 2

  @staticmethod
  def range():
    return [Pin.GREEN, Pin.YELLOW, Pin.RED]

class Traffects:

  def __init__(self, device: str, baudrate: int = 9600, tracker: bool = True):
    self.arduino = serial.Serial(port=device, baudrate=baudrate, timeout=0)
    self.state = [False, False, False]
    if tracker: threading.Thread(target=self._write_stats).start()
    time.sleep(1) # wait 1s, arduino serial connection is not ready immediately

  def _write_stats(self):
    file = open("tracker.txt", "r")
    self.stats = [
      int(file.readline().replace("\n", "")),
      int(file.readline().replace("\n", "")),
      int(file.readline().replace("\n", ""))
    ]

    try:
      while 1:
        file = open("tracker.txt", "w")
        first = True
        for i in self.stats:
          if not first: file.write("\n")
          first = False
          file.write(str(i))
        file.close()
        time.sleep(1)
    except KeyboardInterrupt:
      pass

  def get_arduino(self) -> serial.Serial:
    return self.arduino

  @synchronized
  def send(self, pin: int, on: bool):
    if self.stats is not None and self.state[pin] != on: 
      self.stats[pin] = self.stats[pin] + 1

    self.state[pin] = on
    self.step(pin)
    self.step(on)
    self.finish()

  @synchronized
  def step(self, data: int):
    self.arduino.write(convert_data(data))

  @synchronized
  def finish(self):
    self.arduino.write(b'\xff')
    self.arduino.flush()

  def get(self, pin: int) -> bool:
    return self.state[pin]

  def blink(self, pin: int, period: int = .085):
      self.send(pin, True)
      threading.Timer(period, lambda: self.send(pin, False)).start()
