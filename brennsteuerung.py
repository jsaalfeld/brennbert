import time
from datetime import datetime, timedelta

class BrennofenSteuerung:
    def __init__(self, brennkurve, sensor, relais):
        self.brennkurve = brennkurve
        self.sensor = sensor
        self.relais = relais

        self.phase_index = 0
        self.phase_start = datetime.now()
        self.phase_end = None
        self.start_temp = sensor.read_temperature()
        self.active = True
        self.target_temp = None

        self._prepare_phase()

    def get_phase_name(self):
        return self.phase["phase"] if self.active else "beendet"

    def get_ist_temperature(self):
        return self.sensor.read_temperature()

    def get_soll_temperature(self):
        if not self.active:
            return None

        phase_name = self.phase["phase"]

        if phase_name == "aufheizen":
            now = datetime.now()
            elapsed = (now - self.phase_start).total_seconds()
            total = (self.phase_end - self.phase_start).total_seconds()
            return round(self.start_temp + (self.target_temp - self.start_temp) * (elapsed / total), 2)

        elif phase_name == "abkuehlen":
            elapsed = (datetime.now() - self.phase_start).total_seconds()
            cooldown_per_sec = self.cooldown_rate / 3600
            return round(self.start_temp - (elapsed * cooldown_per_sec), 2)

        elif phase_name == "haltezeit":
            return self.target_temp  # wurde vorher in prepare gesetzt

        elif phase_name == "vorlaufzeit":
            return None  # kein Temperaturziel

        return None



    def _prepare_phase(self):
        if self.phase_index >= len(self.brennkurve):
            print("[Brennofen] Brennkurve abgeschlossen.")
            self.active = False
            self.relais.off()
            return

        self.phase = self.brennkurve[self.phase_index]
        self.phase_start = datetime.now()
        name = self.phase["phase"]

        if name == "vorlaufzeit":
            self.phase_end = self.phase_start + timedelta(minutes=self.phase["duration_minutes"])

        elif name == "aufheizen":

            self.phase_end = self.phase_start + timedelta(minutes=self.phase["duration_minutes"])
    
            # Temperatur sicher auslesen
            while True:
                temp = self.sensor.read_temperature()
                if temp is not None and temp > 0:
                    self.start_temp = temp
                    break
                else:
                    print("[WARN] Ungültige Starttemperatur. Warte auf gültigen Sensorwert...")
                    time.sleep(2)  # 2 Sekunden warten und neu versuchen

            self.target_temp = self.phase["target_temp"]

        elif name == "haltezeit":
            self.phase_end = self.phase_start + timedelta(minutes=self.phase["duration_minutes"])
            self.target_temp = self.sensor.read_temperature()

        elif name == "abkuehlen":
            self.target_temp = 75.0  # später konfigurierbar
            self.cooldown_rate = self.phase["cooldown_rate_c_per_h"]
            self.start_temp = self.sensor.read_temperature()

            # Simuliere Zielzeit: wie lange braucht er, um auf Zieltemp zu fallen
            delta = self.start_temp - self.target_temp
            if delta <= 0:
                self.phase_end = self.phase_start
            else:
                duration = delta / self.cooldown_rate * 60  # Minuten
                self.phase_end = self.phase_start + timedelta(minutes=duration)

        print(f"[Brennofen] Neue Phase: {name} bis {self.phase_end.time()}")

    def tick(self):
        if not self.active:
            return

        now = datetime.now()
        temp = self.sensor.read_temperature()

        if now >= self.phase_end:
            self.phase_index += 1
            self._prepare_phase()
            return

        name = self.phase["phase"]

        if name in ["vorlaufzeit", "haltezeit"]:
            self._regel_heizen(temp, self.target_temp, tolerance=2)

        elif name == "aufheizen":
            elapsed = (now - self.phase_start).total_seconds()
            total = (self.phase_end - self.phase_start).total_seconds()
            solltemp = self.start_temp + (self.target_temp - self.start_temp) * (elapsed / total)
            self._regel_heizen(temp, solltemp, tolerance=2)

        elif name == "abkuehlen":
            elapsed = (now - self.phase_start).total_seconds()
            cooldown_per_sec = self.cooldown_rate / 3600  # °C pro Sekunde
            solltemp = self.start_temp - (elapsed * cooldown_per_sec)
            self._regel_heizen(temp, solltemp, tolerance=3)
        else:
            print(f"[WARN] Unbekannte Phase: {name}")

    def _regel_heizen(self, ist, soll, tolerance=5):
        if soll is None:
            self.relais.off()
        return

        if ist < soll - tolerance:
            self.relais.on()
        elif ist > soll + tolerance:
            self.relais.off()
