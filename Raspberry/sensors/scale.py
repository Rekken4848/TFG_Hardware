import asyncio
from bleak import BleakScanner
from typing import Optional

# Dirección MAC de la báscula Kryos
MAC_ADDRESS = "5C:CA:D3:6B:4F:12"
DEVICE_NAME = "Chipsea-BLE"

# Prefijo esperado de la trama: FFF0
TRAMA_HEADER = b'\xFF\xF0'

def parse_hexa_to_binary(byte: int) -> str:
    return format(byte, '08b')


def get_weight_from_data(data: bytes) -> float:
    # Verifica el logo FFF0
    if data[0:2] != b'\xFF\xF0':
        print("⚠️ Trama no comienza con FFF0. Ignorada.")
        return None

    version = data[2]
    properties = data[3]
    byte4 = data[4]
    byte5 = data[5]

    # Peso bruto: little endian
    raw_weight = (byte5 << 8) | byte4

    bits = parse_hexa_to_binary(properties)
    decimal_bits = bits[3:5]  # bits 4 y 3
    unit_bits = bits[5:7]     # bits 2 y 1

    # Decimal point
    decimals = {
        '00': 2,
        '01': 0,
        '10': 1
    }.get(decimal_bits)

    if decimals is None:
        print("⚠️ No se pudo interpretar la posición decimal.")
        return None

    # Unidad
    unit = {
        '00': 'kg',
        '01': 'jin',
        '10': 'lb',
        '11': 'st:lb'
    }.get(unit_bits)

    if unit is None:
        print("⚠️ Unidad desconocida.")
        return None

    weight = raw_weight / (10 ** decimals)

    print(f"📏 Peso detectado: {weight:.2f} {unit}")
    return weight


async def scan_kryos2(mac_target="5c:ca:d3:6b:4f:12"):
    print("🔍 Escaneando dispositivos BLE...")
    scanner = BleakScanner()

    def detection_callback(device, advertisement_data):
        if device.address.lower() == mac_target.lower():
            manufacturer_data = advertisement_data.manufacturer_data
            for _, raw in manufacturer_data.items():
                try:
                    data = bytes(raw)
                    if data.startswith(b'\xff\xf0'):
                        print(f"\n📡 Trama recibida de {device.address}: {data.hex()}")
                        weight = get_weight_from_data(data)
                        if weight is not None:
                            print(f"✅ Peso final: {weight:.2f}")
                            loop.stop()
                except Exception as e:
                    print(f"❌ Error procesando trama: {e}")

    scanner.register_detection_callback(detection_callback)

    await scanner.start()
    try:
        await asyncio.sleep(15.0)  # Escanea hasta que se encuentre o se acabe el tiempo
    finally:
        await scanner.stop()

async def scan_kryos3(mac_target="5c:ca:d3:6b:4f:12"):
    print("🔍 Escaneando dispositivos BLE durante 10s...")

    devices = await BleakScanner.discover(timeout=10.0)

    for device in devices:
        if device.address.lower() == mac_target.lower():
            print(f"\n📡 Dispositivo detectado: {device.name} ({device.address})")

            manufacturer_data = device.metadata.get("manufacturer_data", {})
            for _, raw in manufacturer_data.items():
                try:
                    data = bytes(raw)
                    print(f"📦 Trama recibida: {data.hex()}")
                    if data.startswith(b'\xff\xf0'):
                        weight = get_weight_from_data(data)
                        if weight is not None:
                            print(f"✅ Peso final: {weight:.2f}")
                            return
                except Exception as e:
                    print(f"❌ Error procesando trama: {e}")

    print("⚠️ No se recibió ninguna trama válida de la báscula.")

async def scan_kryos(mac_target="5c:ca:d3:6b:4f:12"):
    print("🔍 Escaneando dispositivos BLE durante 10s...")

    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(10)
    await scanner.stop()

    devices = await scanner.get_discovered_devices()

    for device in devices:
        if device.address.lower() == mac_target.lower():
            print(f"\n📡 Dispositivo detectado: {device.name} ({device.address})")

            # Intenta obtener datos del anuncio manufacturer
            adv = device.details.get("props", {}) if hasattr(device, "details") else {}

            # Ver si contiene manufacturer data
            if "ManufacturerData" in adv:
                for _, raw in adv["ManufacturerData"].items():
                    try:
                        data = bytes(raw)
                        print(f"📦 Trama recibida: {data.hex()}")
                        if data.startswith(b'\xff\xf0'):
                            weight = get_weight_from_data(data)
                            if weight is not None:
                                print(f"✅ Peso final: {weight:.2f}")
                                return
                    except Exception as e:
                        print(f"❌ Error procesando trama: {e}")
            else:
                print("⚠️ No se encontró ManufacturerData.")

    print("⚠️ No se recibió ninguna trama válida de la báscula.")

def extract_weight2(data: bytes) -> Optional[float]:
    """
    Procesa la trama y devuelve el peso como float (con decimales)
    """
    if len(data) < 6:
        print("⚠️ Trama demasiado corta.")
        return None

    if not data.startswith(TRAMA_HEADER):
        print("⚠️ Trama ignorada (no empieza con FFF0)")
        return None

    version = data[2]
    properties = data[3]
    byte4 = data[4]
    byte5 = data[5]

    raw_weight = (byte5 << 8) | byte4

    binary_props = parse_hexa_to_binary(properties)

    # Bits 3-4: punto decimal
    decimal_bits = binary_props[3:5]
    # Bits 5-6: unidad
    unit_bits = binary_props[5:7]

    decimals = {
        '00': 2,
        '01': 0,
        '10': 1
    }.get(decimal_bits)

    units = {
        '00': 'kg',
        '01': 'jin',
        '10': 'lb',
        '11': 'st:lb'
    }.get(unit_bits)

    if decimals is None or units is None:
        print("⚠️ No se pudo interpretar la trama correctamente.")
        return None

    weight = raw_weight / (10 ** decimals)
    print(f"✅ Peso detectado: {weight:.{decimals}f} {units}")
    return weight


def handle_detection(device, advertisement_data):
    """
    Callback que se ejecuta al recibir un paquete BLE.
    """
    if device.address.lower() != MAC_ADDRESS.lower():
        return

    print(f"\n📡 Trama detectada de {device.name} ({device.address})")

    manufacturer_data = advertisement_data.manufacturer_data
    if not manufacturer_data:
        print("⚠️ No hay manufacturer data en esta trama.")
        return

    for _, data in manufacturer_data.items():
        print(f"📦 Datos crudos: {data.hex()}")
        extract_weight(bytes(data))


async def main2():
    print("🔍 Escaneando báscula Kryos (BLE Broadcast)... Presiona Ctrl+C para salir.\n")
    scanner = BleakScanner()
    scanner.register_detection_callback(handle_detection)

    await scanner.start()
    try:
        while True:
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("🛑 Escaneo detenido por el usuario.")
    finally:
        await scanner.stop()

async def main3():
    print("🔍 Escaneando dispositivos BLE durante 10 segundos...\n")
    devices = await BleakScanner.discover(timeout=10)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        print(f"📡 Dispositivo detectado: {device.name} ({device.address})")

        manufacturer_data = device.metadata.get("manufacturer_data", {})
        if not manufacturer_data:
            print("⚠️ No hay manufacturer data.")
            continue

        for _, data in manufacturer_data.items():
            print(f"📦 Trama recibida: {data.hex()}")
            extract_weight(bytes(data))

def parse_weight_data(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    # Eliminamos la verificación de longitud y mostramos los bytes uno a uno
    for i, b in enumerate(data):
        print(f"Byte {i:02d}: 0x{b:02X}")

    if len(data) < 20:
        print("⚠️ Trama demasiado corta.")
        return

    if data[0:2] != b'\xFF\xF0':
        print("⚠️ Trama no válida (logo incorrecto)")
        return

    # Byte 3: propiedades
    propiedades = data[3]
    bin_props = format(propiedades, '08b')  # binario con ceros a la izquierda
    unidades_bits = bin_props[2:4]  # bits 2 y 3
    decimales_bits = bin_props[4:6]  # bits 4 y 5

    unidades_dict = {
        '00': 'kg',
        '01': 'jin',
        '10': 'lb',
        '11': 'st:lb'
    }
    decimales_dict = {
        '00': 2,
        '01': 0,
        '10': 1
    }

    unidades = unidades_dict.get(unidades_bits, 'desconocido')
    decimales = decimales_dict.get(decimales_bits, 2)

    peso_raw = int.from_bytes(data[5:7], byteorder='little')  # bytes 4 y 5 (little endian)
    peso = peso_raw / (10 ** decimales)

    print(f"⚖️ Peso detectado: {peso:.{decimales}f} {unidades}")

async def main4():
    print("🔍 Escaneando dispositivos BLE durante 10 segundos...\n")
    devices = await BleakScanner.discover(timeout=10)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        print(f"📡 Dispositivo detectado: {device.name} ({device.address})")

        # manufacturer_data ya no está en metadata → se accede desde .details
        # En Linux, Bleak usa BlueZ, y los datos están en device.details["props"]
        adv_data = device.details.get("props", {}).get("ManufacturerData")

        if not adv_data:
            print("⚠️ No se encontró ManufacturerData en detalles.")
            continue

        for _, value in adv_data.items():
            data_bytes = bytes(value)
            print(f"📦 Trama cruda: {data_bytes.hex()}")
            parse_weight_data(data_bytes)

async def main5():
    print("🔍 Escaneando dispositivos BLE durante 10 segundos...\n")
    devices = await BleakScanner.discover(timeout=10)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        print(f"📡 Dispositivo detectado: {device.name} ({device.address})")

        manufacturer_data = device.metadata.get("manufacturer_data", {})
        if not manufacturer_data:
            print("⚠️ No hay manufacturer data.")
            continue

        for key, data in manufacturer_data.items():
            # Aquí es donde debes añadir el código para imprimir y analizar la trama
            print(f"Manufacturer ID: 0x{key:04X}, Data ({len(data)} bytes): {data.hex()}")
            if len(data) < 20:
                print("⚠️ Trama demasiado corta para analizar")
                continue

            # Comprobamos logo esperado en los dos primeros bytes
            if data[0] == 0xFF and data[1] == 0xF0:
                print("🧪 Logo correcto FFF0 detectado")
                # Aquí puedes llamar a tu función que parsea la trama, por ejemplo:
                extract_weight(bytes(data))
            else:
                print(f"⚠️ Logo incorrecto: {data[0]:02X}{data[1]:02X}")

TARGET_MAC = "5C:CA:D3:6B:4F:12".lower()
buffer = []

def detection_callback(device, advertisement_data):
    if device.address.lower() != TARGET_MAC:
        return

    print(f"\n📡 Dispositivo detectado: {device.name} ({device.address})")

    manufacturer_data = advertisement_data.manufacturer_data
    if not manufacturer_data:
        print("⚠️ No hay manufacturer data.")
        return

    for key, value in manufacturer_data.items():
        print(f"🛠️ Manufacturer ID: 0x{key:04X}")
        print(f"📦 Trama cruda ({len(value)} bytes): {value.hex()}")

        if len(value) < 10:
            print("⚠️ Trama demasiado corta.")
            return

        # Aquí podrías intentar extraer el peso si el formato es conocido
        # Solo como ejemplo:
        if value[0] == 0xFF and value[1] == 0xF0:
            print("✅ Trama válida encontrada (firma FFF0)")

def print_separator():
    print("\n" + "-" * 40 + "\n")

async def main6():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)

    print("🔍 Escaneando dispositivos BLE durante 10 segundos...")
    await scanner.start()
    await asyncio.sleep(10)
    await scanner.stop()

    print_separator()
    print("✅ Escaneo finalizado.")

def extract_weight3(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 13:
        print("⚠️ Trama demasiado corta.")
        return

    # Posición tentativa del peso en bytes 11 y 12 (basado en pruebas anteriores)
    weight_raw = data[11] << 8 | data[12]
    weight = weight_raw / 100.0

    print(f"⚖️ Peso estimado: {weight:.2f} kg")

async def main7():
    print("🔍 Escaneando dispositivos BLE durante 10 segundos...\n")
    devices = await BleakScanner.discover(timeout=10)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        print(f"📡 Dispositivo detectado: {device.name} ({device.address})")

        # Obtenemos los datos de manufacturer desde los 'details'
        advertisement = device.details.get("props") or device.details
        raw_data = None

        if "ManufacturerData" in advertisement:
            mdata = advertisement["ManufacturerData"]
            # Normalmente es un dict {company_id: bytes}
            for _, v in mdata.items():
                raw_data = bytes(v)
                break

        if raw_data:
            print(f"📦 Trama cruda: {raw_data.hex()}")
            extract_weight(raw_data)
        else:
            print("⚠️ No se encontró ManufacturerData")

import struct

def extract_weight4(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 9:
        print("⚠️ Trama demasiado corta.")
        return

    # Probar float32 desde bytes 4 a 7 (índices 4,5,6,7)
    raw_float_bytes = data[4:8]
    weight = struct.unpack("<f", raw_float_bytes)[0]

    print(f"⚖️ Peso estimado: {weight:.2f} kg")

def extract_weight5(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 8:
        print("⚠️ Trama demasiado corta.")
        return

    print("🔬 Posibles floats en la trama:")
    for i in range(len(data) - 3):
        chunk = data[i:i+4]
        value = struct.unpack("<f", chunk)[0]
        print(f"  Bytes {i}-{i+3}: {chunk.hex()} → {value:.2f}")

def extract_weight6(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 8:
        print("⚠️ Trama demasiado corta.")
        return

    posibles_pesos = []
    for i in range(len(data) - 3):
        chunk = data[i:i+4]
        try:
            value = struct.unpack("<f", chunk)[0]
            if 20 <= value <= 200:  # Rango razonable para peso humano
                posibles_pesos.append((i, value))
        except:
            continue

    if posibles_pesos:
        # Escoge el más probable (ej. el mayor, si hay varios)
        idx, peso = sorted(posibles_pesos, key=lambda x: x[1], reverse=True)[0]
        print(f"🎯 Peso encontrado en bytes {idx}-{idx+3}: {peso:.2f} kg")
    else:
        print("❌ No se encontró un valor de peso razonable en la trama.")

def extract_weight7(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 6:
        print("⚠️ Trama demasiado corta para contener peso.")
        return

    peso_bytes = data[4:6]
    peso_raw = int.from_bytes(peso_bytes, byteorder='little')  # Peso codificado

    # Asumimos que viene en decigramos (10 gramos por unidad)
    peso_kg = peso_raw / 100.0

    print(f"⚖️ Peso estimado: {peso_kg:.2f} kg (raw: {peso_raw})")

def extract_weight8(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    if len(data) < 6:
        print("⚠️ Trama demasiado corta para contener peso.")
        return

    # Comprobar logo en bytes 0 y 1
    logo = data[0:2]
    if logo != b'\xff\xf0':
        print(f"⚠️ Logo incorrecto: esperado ff f0, obtenido {logo.hex()}")
        # Puedes decidir continuar o no aquí

    byte3 = data[3]
    print(f"Byte 3 (propiedades): 0x{byte3:02x} ({bin(byte3)})")

    # Extraer unidades (bits 6 y 5)
    unidades_bits = (byte3 >> 5) & 0b11
    unidades_map = {0: 'kg', 1: 'jin', 2: 'lb', 3: 'st:lb'}
    unidad = unidades_map.get(unidades_bits, 'desconocida')

    # Extraer posición decimal (bits 4 y 3)
    decimales_bits = (byte3 >> 3) & 0b11
    decimales_map = {0: 2, 1: 0, 2: 1}
    decimales = decimales_map.get(decimales_bits, 2)  # Por defecto 2 decimales

    # Extraer peso (byte 5 primero, luego byte 4)
    peso_raw = (data[5] << 8) + data[4]

    peso = peso_raw / (10 ** decimales)

    print(f"Unidad: {unidad}")
    print(f"Decimales: {decimales}")
    print(f"Peso crudo: {peso_raw}")
    print(f"Peso ajustado: {peso:.{decimales}f} {unidad}")

def extract_weight9(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")

    # Buscar logo FF F0
    logo_index = data.find(b'\xff\xf0')
    if logo_index == -1:
        print("⚠️ No se encontró el logo FF F0 en la trama.")
        return

    print(f"Logo FF F0 encontrado en índice {logo_index}")

    # Asegurarse que haya suficientes bytes después para analizar
    if len(data) < logo_index + 6:
        print("⚠️ Trama demasiado corta después del logo.")
        return

    byte3 = data[logo_index + 3]
    print(f"Byte 3 (propiedades): 0x{byte3:02x} ({bin(byte3)})")

    unidades_bits = (byte3 >> 5) & 0b11
    unidades_map = {0: 'kg', 1: 'jin', 2: 'lb', 3: 'st:lb'}
    unidad = unidades_map.get(unidades_bits, 'desconocida')

    decimales_bits = (byte3 >> 3) & 0b11
    decimales_map = {0: 2, 1: 0, 2: 1}
    decimales = decimales_map.get(decimales_bits, 2)

    peso_raw = (data[logo_index + 5] << 8) + data[logo_index + 4]
    peso = peso_raw / (10 ** decimales)

    print(f"Unidad: {unidad}")
    print(f"Decimales: {decimales}")
    print(f"Peso crudo: {peso_raw}")
    print(f"Peso ajustado: {peso:.{decimales}f} {unidad}")

def extract_weight10(data: bytes):
    print(f"🧪 Analizando trama de {len(data)} bytes: {data.hex()}")
    for i in range(len(data)-1):
        val = (data[i+1] << 8) + data[i]
        # Pruebo 0, 1 y 2 decimales para ver si es cercano a 65
        for decimals in (0,1,2):
            peso = val / (10 ** decimals)
            if 10 < peso < 100:  # rango posible para peso humano
                print(f"Bytes {i}-{i+1}: 0x{data[i+1]:02x}{data[i]:02x} → {peso:.{decimals}f} kg (decimales={decimals})")

def extract_weight(data: bytes):
    # Bytes 2 y 3: peso con 1 decimal
    peso_crudo = (data[3] << 8) + data[2]  # MSB byte 3, LSB byte 2
    peso = peso_crudo / 10  # 1 decimal
    return peso

async def main():
    print("🔍 Escaneando dispositivos BLE durante 10 segundos...\n")
    devices = await BleakScanner.discover(timeout=10)

    for device in devices:
        if device.address.lower() != MAC_ADDRESS.lower():
            continue

        print(f"📡 Dispositivo detectado: {device.name} ({device.address})")

        advertisement = device.details.get("props") or device.details
        raw_data = None

        if "ManufacturerData" in advertisement:
            mdata = advertisement["ManufacturerData"]
            for _, v in mdata.items():
                raw_data = bytes(v)
                break

        if raw_data:
            print(f"📦 Trama cruda: {raw_data.hex()}")
            print(f"{extract_weight(raw_data)}")
        else:
            print("⚠️ No se encontró ManufacturerData")

if __name__ == "__main__":
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #try:
    #    loop.run_until_complete(scan_kryos())
    #except KeyboardInterrupt:
    #    print("\n⛔ Escaneo interrumpido por el usuario.")