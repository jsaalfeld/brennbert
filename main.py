import time
import threading
from config import load_config
from dynamic_import import load_class
import paho.mqtt.client as mqtt
from brennsteuerung import BrennofenSteuerung
from csv_logger import CSVLogger

csv_logger = CSVLogger()

# ---- MQTT Setup ----
mqtt_status = {"enabled": True}
mqtt_connected_flag = {"status": False}

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Verbunden mit Reason-Code {reason_code}")
    mqtt_connected_flag = {"status": True}
    client.subscribe(mqtt_config["topics"]["control"])

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] Nachricht empfangen auf {msg.topic}: {payload}")
    if payload.lower() == "off":
        mqtt_status["enabled"] = False
    elif payload.lower() == "on":
        mqtt_status["enabled"] = True

def start_mqtt_loop(client):
    thread = threading.Thread(target=client.loop_forever)
    thread.daemon = True
    thread.start()

# ---- Load Program ----

cfg = load_config()
debug_mode = cfg.get("debug_mode", False)
manual_override = {"enabled": True}

RelayClass = load_class(cfg["relay_switch"]["class"])
relay = RelayClass()

SensorClass = load_class(cfg["temperature_sensor"]["class"])
sensor = SensorClass(relay)

mqtt_config = cfg.get("mqtt", {})
mqtt_enabled = mqtt_config.get("enabled", False)

if mqtt_enabled:
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    # Some brokers (i.e. for local testing) allow empty username and password
    user = mqtt_config.get("username") or None
    pw = mqtt_config.get("password") or None
    if user and pw:
        client.username_pw_set(user, pw)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(mqtt_config.get("host", "localhost"), mqtt_config.get("port", 1883), 60)
        start_mqtt_loop(client)
    except ConnectionRefusedError:
        print("[MQTT] Verbindung fehlgeschlagen – läuft der Broker?")
        mqtt_enabled = False
else:
    print("[MQTT] Deaktiviert laut Konfiguration.")

# ---- Brennkurve laden ----
programm_name = cfg["programm"]
brennkurve = cfg["programme"][programm_name]["brennkurve"]

# ---- Brennofensteuerung starten ----
steuerung = BrennofenSteuerung(brennkurve, sensor, relay)

print("[System] Brennofen-Regelung gestartet.")

try:
    while steuerung.active:
        steuerung.tick()
        ist = steuerung.get_ist_temperature()
        phase = steuerung.get_phase_name()
        csv_logger.log(phase, ist)
        soll = steuerung.get_soll_temperature()
        soll_text = f"{soll:.2f} °C" if soll is not None else "–"

        print(f"[Ofen] Phase: {phase:12} | Ist: {ist:.2f} °C | Soll: {soll_text}")

        time.sleep(1)

    print("[Ofen] Programm beendet.")
except KeyboardInterrupt:
    print("\n[System] Manuell beendet. Relais wird ausgeschaltet.")
    relay.off()
