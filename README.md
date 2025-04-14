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
