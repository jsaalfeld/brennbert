# brennbert 🔥

**brennbert** is an open-source kiln controller designed for electric pottery kilns.  
It allows precise control of the heating process via a simple relay switch, temperature sensor, and a web interface for defining firing profiles.

---

## Features

- ✅ Simple **ON/OFF relay control** for kiln heating elements  
- 🌡️ Temperature readout via **MAX31855** and K-type thermocouple  
- 📈 Define custom **heating curves** and **firing durations** via web interface  
- 🌍 Optional **MQTT integration** for temperature and status reporting  
- 🧠 Runs on a **Raspberry Pi Zero W**, or any other Pi with GPIO support

---

## Hardware Assumptions

- **Relay** to switch the kiln’s heating elements (`ON` / `OFF`)
- **MAX31855** thermocouple amplifier to read the current kiln temperature
- Kiln has a physical **power level knob** (potentiometer), but power is switched fully via relay (not dimmable)
- **HW-482** Relays for overriding the ON-OFF Settings

---

### 🧠 Raspberry Pi ↔ MAX31855

| Raspberry Pi GPIO (BCM) | Physical Pin | MAX31855 Pin | Description                     |
|--------------------------|--------------|---------------|---------------------------------|
| 3.3V                     | Pin 1        | VCC           | Power supply for MAX31855       |
| GND                      | Pin 6        | GND           | Ground                          |
| GPIO11 (SCLK)            | Pin 23       | CLK           | SPI clock                       |
| GPIO9 (MISO)             | Pin 21       | DO            | SPI data from sensor            |
| GPIO24 (CS)              | Pin 18       | CS            | Chip select for MAX31855        |

- 🧪 **Important**: The MAX31855 only works with **3.3V**, not 5V!
- 📏 Ensure the **thermocouple wires** are connected correctly (T+ / T–).
- A wrong polarity will give incorrect readings (e.g. stuck at 0 °C).

---

### ⚡ Raspberry Pi ↔ HW-482 Relay Module

| Raspberry Pi GPIO (BCM) | Physical Pin | HW-482 Pin | Description                         |
|--------------------------|--------------|-------------|-------------------------------------|
| 5V                       | Pin 2        | VCC (+)     | Power supply for the relay module   |
| GND                      | Pin 6        | GND (–)     | Ground                              |
| GPIO17                   | Pin 11       | SIG (S)     | Signal pin to control the relay     |

- This relay module is **active LOW**, meaning:
  - `GPIO.LOW` → Relay **ON**
  - `GPIO.HIGH` → Relay **OFF**

---

### 🔌 Relay Output (to kiln)

| Relay Output | Description                          |
|--------------|--------------------------------------|
| COM          | 5V supply or common switching point  |
| NO           | Connect to the kiln's control wire   |

- ⚠️ Using the **NO (Normally Open)** pin is safer — the kiln is off by default when the Pi boots.

---

## ✅ Safe Boot Behavior

- Relay is OFF (kiln disconnected) when Pi powers up
- Relay only turns ON when explicitly activated via GPIO
- Temperature readout is blocked until a valid sensor signal is available

---

## Debug & Development

Just clone the project and have a somewhat recent version of Python 3 (3.6 and above) installed.

Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To test the MQTT Capabilietes, just start a local instance of mosquitto:

```bash
mkdir -p mosquitto

echo "listener 1883
allow_anonymous true" > mosquitto/mosquitto.conf

podman run -it -d --name=muecke -p 1883:1883 \
  -v $(pwd)/mosquitto:/mosquitto/config \
  eclipse-mosquitto

podman exec -it muecke mosquitto_sub -h localhost -t "#" -v
```

---

## Web Interface

The web UI allows you to:

- Start/stop the kiln
- View current temperature
- Define and schedule custom firing curves
- Monitor firing progress in real-time

---

## Planned Features

- [ ] REST & MQTT API for integration with home automation (e.g. Home Assistant)
- [ ] Web-based curve editor
- [ ] Firing log export (CSV/JSON)
- [ ] Safety watchdog (e.g. max temperature limit, stuck relay detection)


---

## License

This project is licensed under the **GNU AGPLv3**.  
For commercial licensing, please contact: `brennbert@kleintued.de`

---

## Credits

Made with love, clay, and a bit of structured chaos by the folks at [kleintüd](https://kleintued.de) 🏺🌿
