import random
from controller.temperature_sensor import TemperatureSensor
from controller.relay_switch import RelaySwitch

class MockTemperatureSensor(TemperatureSensor):
    def __init__(self, relay: RelaySwitch, start_temp=20.0):
        self.relay = relay
        self.temp = start_temp

    def read_temperature(self) -> float:
        delta = random.uniform(0, 0.5)
        if self.relay.is_on():
            self.temp += delta
        else:
            self.temp -= delta

        self.temp = max(self.temp, 0.0)  # Temperatur kann nicht negativ werden
        return round(self.temp, 2)