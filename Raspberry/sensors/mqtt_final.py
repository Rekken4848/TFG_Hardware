import paho.mqtt.client as mqtt
import requests
import json
import threading

# Endpoints del backend
TEMP_HUM_ENDPOINT = "http://192.168.43.252:8080/temhum"
WEIGHT_ENDPOINT = "http://192.168.43.252:8080/weight"

# Mapeo de tópicos a sus respectivos endpoints
TOPIC_ENDPOINT_MAP = {
    "hmaresc/tfg/arduino/temhum": TEMP_HUM_ENDPOINT,
    "hmaresc/tfg/arduino/peso": WEIGHT_ENDPOINT
}

def send_post(endpoint, data):
    try:
        response = requests.post(endpoint, json=data, timeout=5)
        print(f"📨 Enviado al backend ({endpoint}): {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error enviando al backend ({endpoint}):", e)

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
            # Enviar datos en un hilo separado
            threading.Thread(target=send_post, args=(endpoint, data)).start()
        else:
            print("⚠️ Tópico desconocido:", msg.topic)

    except Exception as e:
        print("❌ Error procesando el mensaje:", e)

# Cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker local
client.connect("localhost", 1883)
client.loop_forever()