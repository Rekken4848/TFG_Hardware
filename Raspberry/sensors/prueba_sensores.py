import asyncio
from bleak import BleakClient

#address = "Device 01:B6:EC:B9:01:D6 Belter_TP"
address = "01:B6:EC:B9:01:D6"

async def main():
    async with BleakClient(address) as client:
        print("Conectado: ", client.is_connected)
        print(dir(client))
        services = client.services
        for service in services:
            print(f"[Service] {service.uuid}: {service.description}")
            for char in service.characteristics:
                print(f" [Characteristic] {char.uuid}: {char.description}")

asyncio.run(main())