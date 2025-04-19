class RelaySwitch:
    def on(self):
        """Relais einschalten"""
        raise NotImplementedError

    def off(self):
        """Relais ausschalten"""
        raise NotImplementedError

    def is_on(self) -> bool:
        """Status abfragen"""
        raise NotImplementedError