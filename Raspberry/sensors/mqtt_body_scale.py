import asyncio
from bleak import BleakScanner
from typing import Optional
import requests
import time

MAC_ADDRESS = "5C:CA:D3:6B:4F:12"
DEVICE_NAME = "Chipsea-BLE"

BACKEND_ENDPOINT = "http://192.168.43.252:8080/bodyweight"

SCAN_INTERVAL = 5  # en segundos


def extract_weight(data: bytes) -> float:
    """Extrae el peso desde los datos del anuncio BLE."""
    if len(data) >= 4:
        peso_crudo = (data[3] << 8) + data[2]
        peso = peso_crudo / 10  # 1 decimal
        return peso
    return 0.0


async def leer_peso_una_vez() -> Optional[float]:
    """Escanea BLE y extrae el peso si está disponible."""
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
            peso = extract_weight(raw_data)
            return peso

    return None


async def loop_peso():
    """Bucle infinito para leer el peso y enviarlo si es válido."""
    print("🔁 Iniciando bucle de lectura BLE...\n")

    while True:
        peso = await leer_peso_una_vez()

        if peso is not None:
            print(f"⚖️  Peso detectado: {peso:.1f} kg")

            if peso >= 10:
                data = {"body_weight": peso }
                try:
                    response = requests.post(BACKEND_ENDPOINT, json=data, timeout=5)
                    print(f"📨 Enviado al backend: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"❌ Error al enviar al backend: {e}")
            else:
                print("🔕 Peso menor a 10kg, no se envía.")
        else:
            print("⚠️ No se pudo leer el peso esta vez.")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(loop_peso())
    except KeyboardInterrupt:
        print("\n🛑 Finalizado por el usuario.")