import RPi.GPIO as GPIO
GPIO.setwarnings(False)
from controller.relay_switch import RelaySwitch

class RealRelaySwitch(RelaySwitch):
    def __init__(self, relay_pin=17):
        self.relay_pin = relay_pin

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relay_pin, GPIO.OUT)

        # Beim Start Relais auf AUS setzen (Relais offen)
        GPIO.output(self.relay_pin, GPIO.LOW)
        self._is_on = False

    def on(self):
        GPIO.output(self.relay_pin, GPIO.HIGH)  # AN = GPIO.LOW
        print("[Relay] Einschalten")
        self._is_on = True

    def off(self):
        GPIO.output(self.relay_pin, GPIO.LOW)  # AUS = GPIO.HIGH
        print("[Relay] Ausschalten")
        self._is_on = False

    def is_on(self) -> bool:
        return self._is_on

    def cleanup(self):
        GPIO.output(self.relay_pin, GPIO.LOW)
        sleep(2)
        GPIO.cleanup()

