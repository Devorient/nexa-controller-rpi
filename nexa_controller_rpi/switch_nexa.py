import logging
import time
from typing import Optional
from multiprocessing import Process, Queue

# import RPi.GPIO as GPIO
class GPIO(object):
  BOARD = 'adfa'
  OUT = 'adfad'
  @classmethod
  def output(cls, pin, bool):
    pass

  @classmethod
  def setmode(cls, mode):
    pass
  
  @classmethod
  def setup(cls, pin, dir):
    pass

  @classmethod
  def cleanup(cls):
    pass

class MetaNexaSwitcher(type):
  _instance : Optional[type] = None
  def __call__(cls, data_pin):
    if cls._instance is None:
      cls._instance = super(MetaNexaSwitcher, cls).__call__(data_pin)
    else:
      cls._instance._data_pin = data_pin
    return cls._instance

class NexaSwitcher(metaclass=MetaNexaSwitcher):
  def __init__(self, data_pin):
    self._data_pin = data_pin
    self._tx_queue = Queue(10)
    self._tx_process = Process(target=self.tx_task)
    self._tx_process.start()
    logging.info("Created NexaSwitcher for data PIN #{}".format(data_pin))

  def tx_task(self):
    code, on_off = self._tx_queue.get()
    self.switch(code, on_off)

  def sleep_T(self, T_num):
    time.sleep(T_num * 250 / 1000000.0)

  def send_physical_bit(self, bit_value):
    if bit_value:
      GPIO.output(self._data_pin, True)
      self.sleep_T(1)
      GPIO.output(self._data_pin, False)
      self.sleep_T(1)
    else:
      GPIO.output(self._data_pin, True)
      self.sleep_T(1)
      GPIO.output(self._data_pin, False)
      self.sleep_T(5)

  def send_bit(self, bit_value):
    self.send_physical_bit(bit_value)
    self.send_physical_bit(not bit_value)

  def send_sync(self):
    GPIO.output(self._data_pin, True)
    self.sleep_T(1)
    GPIO.output(self._data_pin, False)
    self.sleep_T(10)

  def send_pause(self):
    GPIO.output(self._data_pin, True)
    self.sleep_T(1)
    GPIO.output(self._data_pin, False)
    self.sleep_T(40)

  def send_on_off(self, on_off, tx_code):
    self.send_sync()

    # transmitter code
    binary_number_string = format(tx_code, '026b')
    for digit in binary_number_string:
      bit = digit == '1'
      self.send_bit(bit)

    # group code
    self.send_bit(True)

    # on/off bit, on = 0, off = 1
    self.send_bit(not on_off)

    # Channel bits. Proove/Anslut = 00, Nexa = 11.
    self.send_bit(True)
    self.send_bit(True)

    # Unit bits. Device to be turned on or off.
    # Nexa Unit #1 = 11, #2 = 10, #3 = 01.
    self.send_bit(True)
    self.send_bit(True)

    self.send_pause()

  def switch(self, tx_code, on_off):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self._data_pin, GPIO.OUT)
    for _ in range(0, 5):
      self.send_on_off(on_off, tx_code)

    # Send the signal one more time,
    # sometimes it happens not to be decoded correctly
    time.sleep(1)
    for _ in range(0, 5):
      self.send_on_off(on_off, tx_code)

    GPIO.output(self._data_pin, False)  # Make sure that we do not leave PIN in 'on' state
    GPIO.cleanup()
  
  def queue_switch(self, tx_code, on_off):
    self._tx_queue.put((tx_code, on_off))