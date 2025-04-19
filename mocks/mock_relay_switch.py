from controller.relay_switch import RelaySwitch

class MockRelaySwitch(RelaySwitch):
    def __init__(self):
        self._is_on = False

    def on(self):
        self._is_on = True
        print("MockRelay: EIN")

    def off(self):
        self._is_on = False
        print("MockRelay: AUS")

    def is_on(self) -> bool:
        return self._is_on