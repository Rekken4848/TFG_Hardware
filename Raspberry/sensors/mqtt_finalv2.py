import asyncio
from bleak import BleakScanner
import paho.mqtt.client as mqtt
import requests
import json
import threading
import time
from typing import Optional

TEMP_HUM_ENDPOINT = "http://192.168.43.252:8080/temhum"
FOOD_WEIGHT_ENDPOINT = "http://192.168.43.252:8080/weight"
BODY_WEIGHT_ENDPOINT = "http://192.168.43.252:8080/bodyweight"

TOPIC_ENDPOINT_MAP = {
    "hmaresc/tfg/arduino/temhum": TEMP_HUM_ENDPOINT,
    "hmaresc/tfg/arduino/peso": FOOD_WEIGHT_ENDPOINT
}

MAC_ADDRESS = "5C:CA:D3:6B:4F:12"
DEVICE_NAME = "Chipsea-BLE"
SCAN_INTERVAL = 5


# ===== Funciones comunes =====

def send_post(endpoint, data):
    try:
        response = requests.post(endpoint, json=data, timeout=5)
        print(f"📨 Enviado al backend ({endpoint}): {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error enviando al backend ({endpoint}): {e}")


# ===== Manejador MQTT =====

def on_connect(client, userdata, flags, rc):
    print("📡 Conectado al broker MQTT con código:", rc)
    for topic in TOPIC_ENDPOINT_MAP:
        client.subscribe(topic)
        print(f"✅ Suscrito al tópico: {topic}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"📥 Mensaje recibido en {msg.topic}: {payload}")

        data = json.loads(payload)
        endpoint = TOPIC_ENDPOINT_MAP.get(msg.topic)

        if endpoint:
            threading.Thread(target=send_post, args=(endpoint, data)).start()
        else:
            print("⚠️ Tópico desconocido:", msg.topic)
    except Exception as e:
        print("❌ Error procesando el mensaje:", e)


# ===== Funciones BLE =====

def extract_weight(data: bytes) -> float:
    """Extrae el peso desde los datos del anuncio BLE."""
    if len(data) >= 4:
        peso_crudo = (data[3] << 8) + data[2]
        return peso_crudo / 10  # Convertir a kg con un decimal
    return 0.0


async def leer_peso_ble() -> Optional[float]:
    """Escanea BLE y devuelve el peso si es válido."""
    devices = await BleakScanner.discover(timeout=5)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        advertisement = device.details.get("props") or device.details
        raw_data = None

        if "ManufacturerData" in advertisement:
            mdata = advertisement["ManufacturerData"]
            for _, v in mdata.items():
                raw_data = bytes(v)
                break

        if raw_data:
            return extract_weight(raw_data)
    return None


async def bucle_ble():
    """Bucle infinito para leer el peso BLE y enviarlo si es >= 10kg."""
    print("🔁 Iniciando lectura de báscula BLE...\n")
    while True:
        peso = await leer_peso_ble()
        if peso is not None:
            print(f"⚖️ Peso BLE detectado: {peso:.1f} kg")
            if peso >= 10:
                data = {"body_weight": peso}
                threading.Thread(target=send_post, args=(BODY_WEIGHT_ENDPOINT, data)).start()
            else:
                print("🔕 Peso menor a 10kg, no se envía.")
        else:
            print("⚠️ No se pudo leer la báscula BLE.")
        time.sleep(SCAN_INTERVAL)


# ===== Lanzador Principal =====

def iniciar_mqtt():
    """Inicializa y lanza el cliente MQTT."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.loop_forever()


if __name__ == "__main__":
    try:
        # Hilo para MQTT
        mqtt_thread = threading.Thread(target=iniciar_mqtt)
        mqtt_thread.start()

        # Ejecutar bucle BLE en el hilo principal
        asyncio.run(bucle_ble())
    except KeyboardInterrupt:
        print("\n🛑 Programa finalizado por el usuario.")