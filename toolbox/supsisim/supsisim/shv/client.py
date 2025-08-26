"""
SHV client.
"""

import asyncio
from threading import Thread

from shv import RpcUrl, RpcError, SHVType, SHVBytes

try:
    from shv import SHVType
    from shv.rpcapi.client import SHVClient
    from shv.rpcdef.errors import RpcError
    from shv.rpcurl import RpcUrl

    SHV_CLIENT = SHVClient
except ImportError:
    from shv import RpcError, RpcUrl, SHVType

    print("Warning: It is suggested to use pyshv in version >=0.10.0")
    try:
        from shv import SHVClient

        SHV_CLIENT = SHVClient
    except ImportError:
        from shv import SimpleClient

        SHV_CLIENT = SimpleClient


def _start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        print("Ending connection loop...")
        for task in asyncio.all_tasks():
            task.cancel()

        print("Remaining tasks canceled...")
    loop.close()
    print("Ending connection loop, all Done")


async def _disconnect_client(client: SHV_CLIENT):
    if await _is_connected(client):
        await client.disconnect()


async def _connect_client(
    user: str, addr: str, port: str, password: str
) -> SHV_CLIENT | None:
    url: RpcUrl = RpcUrl.parse(f"tcp://{user}@{addr}:{port}?password={password}")

    print("Connection to SHV broker: ", url.to_url())
    return await SHV_CLIENT.connect(url)


async def _get_parameter_value(
    client: SHV_CLIENT, mount_point: str, device_id: str, item: str, param_name: str
) -> SHVType | None:
    call_url = f"{mount_point}/{device_id}/blocks/{param_name}/parameters/{item}"
    try:
        result = await client.call(call_url, "get")
        return result
    except RpcError as exc:
        print("Can't read parameter ", param_name)
        print(exc)
        return None


async def _set_parameter_value(
    client: SHV_CLIENT,
    mount_point: str,
    device_id: str,
    item: str,
    param_name: str,
    param_value: SHVType,
):
    call_url = f"{mount_point}/{device_id}/blocks/{param_name}/parameters/{item}"
    try:
        return await client.call(call_url, "set", param_value)
    except RpcError as e:
        print("Can't set parameter ", param_name)
        print(e)


async def _is_connected(client: SHV_CLIENT) -> bool:
    return client.client.connected


class ShvClient:
    """Representation of SHV client connection to the broker."""

    def __init__(self) -> None:
        self.asyncio_loop = asyncio.new_event_loop()
        self.asyncio_thread = Thread(
            target=_start_background_loop, args=(self.asyncio_loop,), daemon=True
        )
        self.client: SHV_CLIENT | None = None
        self.addr: str | None = None
        self.port: str | None = None
        self.user: str | None = None
        self.password: str | None = None
        self.device_id: str | None = None
        self.mount_point: str | None = None

        self.asyncio_thread.start()

    def __del__(self) -> None:
        print("Stopping SHV connection!")
        self.asyncio_loop.stop()

    def _connect(self) -> None:
        print("Connecting to broker...")
        res = asyncio.run_coroutine_threadsafe(
            _connect_client(self.user, self.addr, self.port, self.password),
            self.asyncio_loop,
        )
        try:
            client = res.result()
        except TimeoutError:
            print("Connection to the broker timeouted!")
            res.cancel()
        except Exception as exc:
            print(f"No connection to broker: {exc}")
        else:
            self.client = client
            print("Connected to broker.")

    def _disconnect(self) -> None:
        if self.client is None:
            return
        print("Disconnecting from broker...")
        asyncio.run_coroutine_threadsafe(
            _disconnect_client(self.client), self.asyncio_loop
        ).result()

        self.client = None

        print("Disconnected from broker.")

    def _get_connection(self) -> SHV_CLIENT:
        if (
            self.client is None
            or not asyncio.run_coroutine_threadsafe(
                _is_connected(self.client), self.asyncio_loop
            ).result()
        ):
            self._connect()

        return self.client

    def update_parameters_and_connect(
        self,
        addr: str,
        port: str,
        user: str,
        password: str,
        device_id: str,
        mount_point: str,
    ) -> None:
        are_values_updated = (
            self.addr != addr
            or self.port != port
            or self.user != user
            or self.password != password
            or self.device_id != device_id
            or self.mount_point != mount_point
        )

        self.addr = addr
        self.port = port
        self.user = user
        self.password = password
        self.device_id = device_id
        self.mount_point = mount_point

        if are_values_updated:
            self._disconnect()

        if self.client is None:
            self._connect()

    def is_connected(self) -> bool:
        if self.client is None:
            return False

        return asyncio.run_coroutine_threadsafe(
            _is_connected(self.client), self.asyncio_loop
        ).result()

    def get_parameter_value(self, item: str, param_name: str) -> SHVType | None:
        client = self._get_connection()
        return asyncio.run_coroutine_threadsafe(
            _get_parameter_value(
                client, self.mount_point, self.device_id, item, param_name
            ),
            self.asyncio_loop,
        ).result()

    def set_parameter_value(self, item: str, param_name: str, param_value: SHVType):
        client = self._get_connection()
        asyncio.run_coroutine_threadsafe(
            _set_parameter_value(
                client, self.mount_point, self.device_id, item, param_name, param_value
            ),
            self.asyncio_loop,
        ).result()

    def disconnect(self):
        self._disconnect()


async def _fwupdate_met_call(client: SHV_CLIENT, mount_point: str, device_id: str,
    met_name: str, arg: SHVType = None) -> SHVType | None:
    if met_name != "reset":
        call_url = f"{mount_point}/{device_id}/fwUpdate"
    else:
        call_url = f"{mount_point}/{device_id}/.device"
    try:
        if arg is not None:
            result = await client.call(call_url, met_name, arg)
        else:
            result = await client.call(call_url, met_name)
        return result
    except RpcError as exc:
        print(exc)
        return None

async def _stat_file(client: SHV_CLIENT, mount_point: str, device_id: str) -> SHVType | None:
    return await _fwupdate_met_call(client, mount_point, device_id, "stat")

async def _write_file(client: SHV_CLIENT, mount_point: str, device_id: str,
    chunk: bytes, offset: int) -> SHVType | None:
    return await _fwupdate_met_call(client, mount_point, device_id, "write", [offset, SHVBytes(chunk)])

async def _crc_file(client: SHV_CLIENT, mount_point: str, device_id: str,
    start: int, size: int) -> SHVType | None:
    return await _fwupdate_met_call(client, mount_point, device_id, "crc", [start, size])

async def _reset_dev(client: SHV_CLIENT, mount_point: str, device_id: str) -> SHVType | None:
    return await _fwupdate_met_call(client, mount_point, device_id, "reset")

class ShvFwUpdateClient(ShvClient):
    def __init__(self):
        super().__init__()

    def stat_file(self):
        ret: Optional
        client = self._get_connection()
        ret = asyncio.run_coroutine_threadsafe(
            _stat_file(client, self.mount_point, self.device_id),
            self.asyncio_loop,
        ).result()
        return ret

    def write_chunk(self, chunk: bytes, offset: int):
        client = self._get_connection()
        ret = asyncio.run_coroutine_threadsafe(
            _write_file(client, self.mount_point, self.device_id, chunk, offset),
            self.asyncio_loop,
        ).result()
        return ret

    def get_crc(self, start: int, size: int):
        client = self._get_connection()
        ret = asyncio.run_coroutine_threadsafe(
            _crc_file(
                client, self.mount_point, self.device_id, start, size),
            self.asyncio_loop,
        ).result()
        # Make it unsigned
        if ret == None:
            return None
        return ret & 0xFFFFFFFF
