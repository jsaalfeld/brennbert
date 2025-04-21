import random
from controller.temperature_sensor import TemperatureSensor
from controller.relay_switch import RelaySwitch

class MockTemperatureSensor(TemperatureSensor):
    def __init__(self, relay: RelaySwitch, start_temp=20.0, ambient_temp=22.0):
        self.relay = relay
        self.temp = start_temp
        self.ambient = ambient_temp

    def read_temperature(self) -> float:
        delta = random.uniform(0, 0.5)

        if self.relay.is_on():
            self.temp += delta
        else:
            # Temperatur fällt Richtung Umgebungstemperatur
            if self.temp > self.ambient:
                self.temp -= delta
            else:
                # Leichtes Schwanken um Umgebungstemperatur simulieren
                self.temp += random.uniform(-0.1, 0.1)

        return round(self.temp, 2)
