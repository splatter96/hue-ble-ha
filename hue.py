import asyncio
import struct
from bleak import BleakClient

LIGHT_UUID = "932c32bd-0002-47a2-835a-a8d455b859dd"
BRIGHTNESS_UUID = "932c32bd-0003-47a2-835a-a8d455b859dd"
TEMPERATURE_UUID = "932c32bd-0004-47a2-835a-a8d455b859dd"

class HueLightInstance:
    def __init__(self, mac: str) -> None:
        self.client = BleakClient(mac)
        self.connected = False

    async def _write(self, uuid: str, data: bytes) -> None:
        if not self.connected:
            await self.connect()

        await self.client.write_gatt_char(uuid, data)

    async def _read(self, uuid: str) -> bytearray:
        if not self.connected:
            await self.connect()

        return await self.client.read_gatt_char(uuid)

    async def connect(self) -> None:
        await self.client.connect(timeout=20)
        await asyncio.sleep(1)
        self.connected = True

    async def set_brightness(self, brightness: int) -> None:
        await self._write(BRIGHTNESS_UUID, struct.pack("B", brightness))

    async def get_brightness(self) -> int:
        ret_val = await self._read(BRIGHTNESS_UUID)
        val = struct.unpack("B", ret_val)
        return val[0]

    async def turn_on(self) -> None:
        await self._write(LIGHT_UUID, b"\x01")

    async def turn_off(self) -> None:
        await self._write(LIGHT_UUID, b"\x00")

    async def is_on(self) -> bool:
        ret_val = await self._read(LIGHT_UUID)
        val = struct.unpack("B", ret_val)
        return val[0]==1

async def main():
    address = "CB:E0:41:A5:E6:42"

    light = HueLightInstance(address)

    for i in range(10, 250, 10):
        await light.set_brightness(i)
        await asyncio.sleep(0.1)

        bright = await light.get_brightness()
        print(bright)

    await light.turn_off()
    await asyncio.sleep(2)
    await light.turn_on()
    is_on = await light.is_on()
    print(is_on)

if __name__ == "__main__":
    asyncio.run(main())
