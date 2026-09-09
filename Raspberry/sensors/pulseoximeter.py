import asyncio
from bleak import BleakClient
from typing import Optional, Tuple

# Configuración del pulsioxímetro
MAC_ADDRESS = "64:69:4e:a3:b6:77"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

buffer = bytearray()

def is_valid_pulse_frame(data: bytearray) -> bool:
    return (
        len(data) == 19 and           # Exactamente 19 bytes
        data[0] != 0xAA and           # No empieza con 0xAA
        data[-1] == 0x00              # Termina en 0x00
    )

def parse_pulse_data2(data: bytearray) -> Optional[tuple[int, int]]:
    """
    Extrae oxígeno (byte 16) y pulsaciones (byte 17)
    """
    if not is_valid_pulse_frame(data):
        return None

    oxygen = int(data[15])  # byte 16
    pulse = int(data[16])   # byte 17
    return oxygen, pulse

def parse_pulse_data3(data: bytearray) -> Optional[Tuple[int, int]]:
    if len(data) != 19:
        return None
    if data[0] == 0xAA or data[-1] != 0x00:
        return None
    oxygen = data[16]
    pulse = data[17]
    return oxygen, pulse

def parse_pulse_data2(data: bytearray) -> Optional[Tuple[int, int]]:
    # Verifica las condiciones de trama válida
    if (
        len(data) == 19 and
        not data[0] == 0xAA and
        data[-1] == 0x00
    ):
        print(f"🧪 Trama válida: {[hex(b) for b in data]}")

        # Extrae bytes 15 y 16 (índices 14 y 15)
        oxygen = data[15]
        pulse = data[16]

        print(f"   → Posible oxígeno: {oxygen}%")
        print(f"   → Posible pulso: {pulse} bpm")
        return oxygen, pulse
    else:
        print("⚠️ Trama descartada")
        return None

def parse_pulse_data(data: bytearray) -> Optional[Tuple[int, int]]:
    if (
        len(data) == 19 and
        not data[0] == 0xAA and
        data[-1] == 0x00
    ):
        oxigeno = data[15]
        pulso = data[16]

        #print(f"🧪 Trama válida: {[hex(b) for b in data]}")
        #print(f"   → Posible oxígeno: {oxigeno}%")
        #print(f"   → Posible pulso: {pulso} bpm")

        # Filtra valores absurdos
        if 60 <= oxigeno <= 100 and 30 <= pulso <= 200:
            return oxigeno, pulso
        else:
            print("⚠️ Valores fuera de rango clínico. Ignorados.")
    else:
        #print("⚠️ Trama descartada")
        a = 3
    return None

def handle_notification2(_: int, data: bytearray):
    print(f"📡 Trama recibida: {data.hex()}")
    result = parse_pulse_data(data)
    if result:
        oxygen, pulse = result
        print(f"Saturación O₂: {oxygen}% - Pulso: {pulse} BPM")
    else:
        print("⚠️ Trama descartada")

def handle_notification3(_: int, data: bytearray):
    global buffer

    buffer += data
    print(f"📡 Fragmento recibido: {data.hex()}")

    # Si el buffer acumula al menos 19 bytes
    while len(buffer) >= 19:
        frame = buffer[:19]

        # Procesamos y luego recortamos el buffer
        result = parse_pulse_data(frame)
        if result:
            oxygen, pulse = result
            print(f"✅ Saturación O₂: {oxygen}% - Pulso: {pulse} BPM")
        else:
            print(f"⚠️ Trama descartada: {frame.hex()}")

        buffer = buffer[1:]  # Avanza 1 byte para encontrar tramas válidas sucesivas

def handle_notification(_: int, data: bytearray):
    global buffer

    buffer += data
    print(f"📡 Fragmento recibido: {data.hex()}")

    # Si el buffer acumula al menos 19 bytes
    while len(buffer) >= 19:
        frame = buffer[:19]

        # Procesamos y luego recortamos el buffer
        result = parse_pulse_data(frame)
        if result:
            oxygen, pulse = result
            print(f"✅ Saturación O₂: {oxygen}% - Pulso: {pulse} BPM")
        
        buffer = buffer[1:]  # Avanza 1 byte para encontrar tramas válidas sucesivas

async def main2():
    async with BleakClient(MAC_ADDRESS) as client:
        if client.is_connected:
            print("✅ Conectado al pulsioxímetro OL-750")
            await client.start_notify(CHARACTERISTIC_UUID, handle_notification)
            print("⏳ Esperando notificaciones... Presiona Ctrl+C para salir")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Finalizando...")
                await client.stop_notify(CHARACTERISTIC_UUID)
        else:
            print("❌ No se pudo conectar al dispositivo")

async def main():
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Conectado al pulsioxímetro OL-750")
        await client.start_notify(CHARACTERISTIC_UUID, handle_notification)
        print("⏳ Esperando notificaciones... Presiona Ctrl+C para salir")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Interrupción recibida, cerrando...")
        finally:
            await client.stop_notify(CHARACTERISTIC_UUID)

if __name__ == "__main__":
    asyncio.run(main())