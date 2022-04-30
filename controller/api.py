from asyncio import constants
from enum import Enum
import serial
import time

def convert_data(data: int) -> bytes :
  return data.to_bytes(1, byteorder="big", signed=data < 0)

class Pin:
  GREEN = 0
  YELLOW = 1
  RED = 2

  @staticmethod
  def range():
    return [0, 1, 2]

class Traffects:

  def __init__(self, device: str, baudrate: int = 9600):
    self.arduino = serial.Serial(port=device, baudrate=baudrate, timeout=0)
    "self.send_data(-1)"
    time.sleep(3.5)

  def get_arduino(self) -> serial.Serial:
    return self.arduino

  def send(self, pin: int | Pin, on: bool):
    self.step(pin)
    self.step(on)
    self.finish()

  def step(self, data: int):
    self.arduino.write(convert_data(data))

  def finish(self):
    self.arduino.write(b'\xff')
    self.arduino.flush()
