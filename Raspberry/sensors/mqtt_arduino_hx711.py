import paho.mqtt.client as mqtt
import requests
import json

# Configura el endpoint de tu servidor backend
BACKEND_ENDPOINT = "http://192.168.43.252:8080/weight"

def on_connect(client, userdata, flags, rc):
    print("📡 Conectado al broker MQTT con código:", rc)
    client.subscribe("hmaresc/tfg/arduino/peso")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("📥 Mensaje recibido:", payload)

        # Intenta convertir el payload a JSON
        data = json.loads(payload)

        # Llama a tu backend
        response = requests.post(BACKEND_ENDPOINT, json=data)
        print(f"📨 Enviado al backend: {response.status_code} - {response.text}")

    except Exception as e:
        print("❌ Error procesando el mensaje:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conectamos al broker local
client.connect("localhost", 1883)
client.loop_forever()