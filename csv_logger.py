import csv
import os
from datetime import datetime

class CSVLogger:
    def __init__(self, prefix="brennverlauf", directory="logs"):
        os.makedirs(directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{prefix}_{timestamp}.csv"
        self.filepath = os.path.join(directory, filename)

        self._init_file()

    def _init_file(self):
        with open(self.filepath, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "phase", "temperature_c"])

    def log(self, phase, temperature):
        with open(self.filepath, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec='seconds'),
                phase,
                round(temperature, 2) if temperature is not None else "N/A"
            ])
