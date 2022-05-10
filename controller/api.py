import serial
import time
import threading
import functools

def int_to_bytes(data: int) -> bytes:
  return data.to_bytes(1, byteorder="big", signed=data < 0)

# create a @synchronized annotation like the keyword in java
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

class Mode:
  SET_PIN = 0

class Traffects:

  def __init__(self, device: str, baudrate: int = 115200, tracker: bool = True, wait: bool = True):
    self.arduino = serial.Serial(port=device, baudrate=baudrate, timeout=0)
    self.state = [False, False, False]
    if tracker: threading.Thread(target=self.__write_stats).start()
    if wait: time.sleep(1) # wait 1s, arduino serial connection is not ready immediately

  def __write_stats(self):
    with open("tracker.txt", "r") as file:
      self.stats = [
        int(file.readline().replace("\n", "")),
        int(file.readline().replace("\n", "")),
        int(file.readline().replace("\n", "")),
        int(file.readline().replace("\n", "")),
        int(file.readline().replace("\n", ""))
      ]

    interval = .1

    try:
      while 1:
        time.sleep(interval)
        self.stats[4] = self.stats[4] + interval
        with open("tracker.txt", "w") as file:
          first = True
          for i in self.stats:
            if not first: file.write("\n")
            first = False
            file.write(str(int(i)))
    except KeyboardInterrupt:
      pass

  def __write(self, byte: bytes):	
    if self.stats is not None: 
      self.stats[3] = self.stats[3] + 1
    self.arduino.write(byte)
  
  def __flush(self):
    self.arduino.flush()
    pass

  def get_arduino(self) -> serial.Serial:
    return self.arduino

  @synchronized
  def step(self, data: int):
    self.__write(int_to_bytes(data))

  @synchronized
  def finish(self):
    # write 0xff which is used as the termiator byte, flush serial stream
    self.__write(b'\xff')
    self.__flush()

  @synchronized
  def send(self, mode: int, data: list[int]):
    self.step(mode)
    for current in data:
      self.step(current)
    self.finish()

  def get(self, pin: int) -> bool:
    return self.state[pin]

  def set(self, pin: int, on: bool):
    if self.state[pin] == on:
      return

    if self.stats is not None: 
      self.stats[pin] = self.stats[pin] + 1
    self.state[pin] = on

    self.send(Mode.SET_PIN, [pin, on])

  def blink(self, pin: int, period: int = .085):
      self.set(pin, True)
      threading.Timer(period, lambda: self.set(pin, False)).start()
