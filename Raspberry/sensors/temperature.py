import asyncio
from bleak import BleakClient
from typing import Optional

#address = "Device 01:B6:EC:B9:01:D6 Belter_TP"
address = "01:B6:EC:B9:01:D6"

async def main2():
    async with BleakClient(address) as client:
        print("Conectado: ", client.is_connected)
        services = client.services

        for service in services:
            if service.uuid == "0000fff0-0000-1000-8000-00805f9b34fb":
                print(f"Encontrado servicio vendor: {service.uuid}")
                for char in service.characteristics:
                    print(f"   Leyendo característica {char.uuid}")
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(f"   Valor: {value}")
                    except Exception as e:
                        print(f"   No se pudo leer: {e}")

def notification_handler2(sender, data):
    print(f" Notificación de {sender}: {data} (hex: {data.hex()})")

async def main3():
    async with BleakClient(address) as client:
        await client.start_notify("0000fff3-0000-1000-8000-00805f9b34fb", notification_handler)
        print("Escuchando notificaciones...")
        await asyncio.sleep(30)
        await client.stop_notify("0000fff3-0000-1000-8000-00805f9b34fb")

async def main4():
    async with BleakClient(address) as client:
        print("Conectado: ", client.is_connected)

        try:
            print("Intentando escribir a fff4 para activar notificaciones...")
            await client.write_gatt_char("0000fff4-0000-1000-8000-00805f9b34fb", bytearray([]))
        except Exception as e:
            print(f"No se pudo escribir a fff4: {e}")


        try:
            print("Intentando activar notificaciones en fff3...")
            await client.start_notify("0000fff3-0000-1000-8000-00805f9b34fb", notification_handler)
            print("Esperando notificaciones durante 30 segundos...")
            await asyncio.sleep(30)
            await client.stop_notify("0000fff3-0000-1000-8000-00805f9b34fb")
        except Exception as e:
            print(f"No se pudo activar notificaciones: {e}")

async def main5():
    async with BleakClient(address) as client:
        print("Conectado: ", client.is_connected)

        input("Toma una medición con el termómetro y pulsa Enter cuando esté lista...")

        try:
            value = await client.read_gatt_char("0000fff4-0000-1000-8000-00805f9b34fb")
            print(f"Valor leído (bruto): {value}")
            print(f"Valor en hex: {value.hex()}")
        except Exception as e:
            print(f"Error al leer característica fff4: {e}")

async def main6():
    async with BleakClient(address) as client:
        print("Conectando...")
        paired = await client.pair(protection_level=1)
        print("Emparejado: ", paired)
        input("Toma una medición con el termómetro y pulsa Enter cuando esté lista...")

        try:
            value = await client.read_gatt_char("0000fff4-0000-1000-8000-00805f9b34fb")
            print(f"Valor leido bruto: {value}")
            print(f"Valor en hex: {value.hex()}")
        except Exception as e:
            print(f"Error al leer característica fff4: {e}")

        await client.unpair()
        print("Desemparejado")

async def main7():
    async with BleakClient(address) as client:
        print("Conectado: ", client.is_connected)

        input("Toma una medición con el termómetro y pulsa Enter cuando esté lista...")

        try:
            print("Escribiendo en fff4 para activar transmisión...")
            await client.write_gatt_char("0000fff4-0000-1000-8000-00805f9b34fb", bytearray([0x01]))
        except Exception as e:
            print(f"No se pudo escribir en fff4: {e}")

        await asyncio.sleep(1)

        try:
            print("Leyendo valor de fff4...")
            value = await client.read_gatt_char("0000fff4-0000-1000-8000-00805f9b34fb")
            print(f"Valor leido (bruto): {value}")
            print(f"Valor en hex: {value.hex()}")
        except Exception as e:
            print(f"Error al leer característica fff4: {e}")

CHAR_UUIDS = [
    "0000fff3-0000-1000-8000-00805f9b34fb",
    "0000fff4-0000-1000-8000-00805f9b34fb",
    "0000fec7-0000-1000-8000-00805f9b34fb",
    "0000fec8-0000-1000-8000-00805f9b34fb",
    "0000fec9-0000-1000-8000-00805f9b34fb",
]

async def main8():
    async with BleakClient(address) as client:
        print("🔗 Conectado:", client.is_connected)
        input("📏 Toma una medición con el termómetro y pulsa Enter...")

        for uuid in CHAR_UUIDS:
            print(f"\n🔎 Probando característica: {uuid}")

            # Intentar leer
            try:
                value = await client.read_gatt_char(uuid)
                print(f"📖 Lectura: {value.hex()}")
            except Exception as e:
                print(f"❌ No se pudo leer: {e}")

            # Intentar escribir 0x01
            try:
                await client.write_gatt_char(uuid, bytearray([0x01]), response=True)
                print("✍️ Escritura 0x01 exitosa")
            except Exception as e:
                print(f"❌ No se pudo escribir: {e}")

            # Intentar activar notificaciones
            try:
                await client.start_notify(uuid, notification_handler)
                print("✅ Notificaciones activadas. Esperando 5 segundos...")
                await asyncio.sleep(5)
                await client.stop_notify(uuid)
            except Exception as e:
                print(f"❌ No se pudo activar notificaciones: {e}")

# UUID de la característica que envía la temperatura
TEMPERATURE_CHAR_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"

def parse_temperature(data: bytearray) -> float:
    """
    Extrae la temperatura desde el payload recibido.
    Asume que está en los bytes [2:4], en formato little-endian y escala 0.1.
    """
    if len(data) >= 4:
        raw_temp = int.from_bytes(data[2:4], byteorder='little')
        return raw_temp / 10.0
    return None

def notification_handler3(sender, data):
    temp = parse_temperature(data)
    if temp is not None:
        print(f"🌡️  Temperatura recibida: {temp:.1f} °C")
    else:
        print(f"❓ Datos no válidos: {data.hex()}")

async def main9():
    print("🔌 Conectando al dispositivo...")
    async with BleakClient(address) as client:
        connected = client.is_connected
        print(f"🔗 Conectado: {connected}")

        if not connected:
            return

        print(f"🔔 Suscribiéndose a notificaciones en {TEMPERATURE_CHAR_UUID}...")
        await client.start_notify(TEMPERATURE_CHAR_UUID, notification_handler)

        print("📡 Esperando datos de temperatura... (Ctrl+C para salir)")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Finalizando...")
            await client.stop_notify(TEMPERATURE_CHAR_UUID)


def parse_kelvin_temperature(data: bytearray) -> Optional[float]:
    """
    Extrae la temperatura si la trama es válida.
    La temperatura está en los bytes 6 (high) y 7 (low) -> big endian.
    La trama debe tener al menos 15 bytes.
    Byte 4 debe ser 0xFF = "medición actual válida"
    """
    if len(data) < 15:
        print("❌ Trama demasiado corta.")
        return None

    if data[4] != 0xFF:
        print(f"⚠️ Trama ignorada (byte 4 = {data[4]:02X})")
        return None

    temp_raw = (data[6] << 8) | data[7]  # big-endian
    temperature = temp_raw / 100.0  # dos decimales
    return temperature

def notification_handler(sender: int, data: bytearray):
    temp = parse_kelvin_temperature(data)
    if temp is not None:
        print(f"🌡️  Temperatura: {temp:.2f} °C")
    else:
        print(f"📭 Trama ignorada: {data.hex()}")

async def main():
    print(f"🔌 Conectando a {address}...")
    async with BleakClient(address) as client:
        connected = client.is_connected
        print(f"🔗 Conectado: {connected}")
        if not connected:
            return

        print("🔔 Escuchando notificaciones...")
        await client.start_notify(TEMPERATURE_CHAR_UUID, notification_handler)

        print("📡 Esperando datos... (Ctrl+C para salir)")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Saliendo...")
            await client.stop_notify(TEMPERATURE_CHAR_UUID)

asyncio.run(main())