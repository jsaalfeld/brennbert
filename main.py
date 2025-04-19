import time
import threading
from config import load_config
from dynamic_import import load_class
import paho.mqtt.client as mqtt

# ---- MQTT Setup ----
mqtt_status = {"enabled": True}

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Verbunden mit Reason-Code {reason_code}")
    client.subscribe("brennofen/control")

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

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect("localhost", 1883, 60)
    start_mqtt_loop(client)
except ConnectionRefusedError:
    print("[MQTT] Verbindung fehlgeschlagen – läuft kein Broker? MQTT deaktiviert.")
    mqtt_status["enabled"] = False
    mqtt_enabled = False
else:
    mqtt_enabled = True

print("[System] Brennofen-Regelung gestartet. Warten auf MQTT-Startsignal...")

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
                client.publish("brennofen/temperature", temp)
                client.publish("brennofen/relay_status", relay_status)
        else:
            print("[Ofen] AUS – kein Heizbetrieb.")
            relay.off()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[System] Manuell beendet. Relais wird ausgeschaltet.")
    relay.off()
