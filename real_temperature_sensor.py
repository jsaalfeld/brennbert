import time
import board
import digitalio
import adafruit_max31855
from controller.temperature_sensor import TemperatureSensor

class RealTemperatureSensor(TemperatureSensor):
    def __init__(self, relay=None, cs_pin=24): #Relay to None, to keep the mock connected to the relay
        spi = board.SPI()
        cs = digitalio.DigitalInOut(getattr(board, f"D{cs_pin}"))
        self.sensor = adafruit_max31855.MAX31855(spi, cs)

    def read_temperature(self) -> float:
        try:
            return round(self.sensor.temperature, 2)
        except RuntimeError as e:
            print("[TempSensor] Fehler beim Auslesen:", e)
            return -99.0
