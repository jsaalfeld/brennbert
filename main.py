import time
import threading
from config import load_config
from dynamic_import import load_class
import paho.mqtt.client as mqtt

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

print("[System] Brennofen-Regelung gestartet.")

try:
    while True:
        if debug_mode:
            # Debug-Modus: Instead of MQTT Signals - use your Keyboard
            user_input = input("[Debug] Eingabe (on/off/skip, Enter = skip): ").strip().lower()
            if user_input == "on":
                manual_override["enabled"] = True
            elif user_input == "off":
                manual_override["enabled"] = False
            elif user_input == "skip":
                pass
            elif user_input == "":
                pass # Default = Skip

            current_enabled = manual_override["enabled"]
        else:
            # Normal Running Mode
            current_enabled = mqtt_status["enabled"]

        if current_enabled:
            temp = sensor.read_temperature()
            print(f"[Ofen] Temperatur: {temp} °C")

            if temp > 1220:
                relay.off()
            elif temp < 1210:
                relay.on()

            relay_status = "ON" if relay.is_on() else "OFF"

            if mqtt_enabled:
                ret = client.publish(mqtt_config["topics"]["temperature"], temp)
                client.publish(mqtt_config["topics"]["relay_status"], relay_status)

        else:
            print("[Ofen] AUS – kein Heizbetrieb.")
            relay.off()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[System] Manuell beendet. Relais wird ausgeschaltet.")
    relay.off()
