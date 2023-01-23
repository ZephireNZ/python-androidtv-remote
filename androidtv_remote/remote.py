import asyncio
import logging
import ssl
from dataclasses import dataclass
from typing import Callable

from androidtv_remote.util import ProtoStream

from .proto import remote_pb2 as remote

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    model: str
    vendor: str
    package_name: str
    app_version: str


class RemoteManager:
    def __init__(
        self,
        key_path: str,
        cert_path: str,
        device_info: DeviceInfo,
        host: str,
        port: int = 6466,
    ):
        self.host = host
        self.port = port
        self.key_path = key_path
        self.cert_path = cert_path
        self.connected = False
        self.device_info = device_info

    async def connect(self):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_cert_chain(
            certfile=self.cert_path,
            keyfile=self.key_path,
        )
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.VerifyMode.CERT_NONE

        _LOGGER.debug("Connecting to TV")
        reader, writer = await asyncio.open_connection(
            host=self.host,
            port=self.port,
            ssl=ssl_ctx,
        )

        self._proto = ProtoStream(reader, writer, remote.RemoteMessage)
        self.connected = True

    async def disconnect(self):
        self.connected = False
        self._proto.writer.close()
        await self._proto.writer.wait_closed()
        self._proto = None
    
    async def send_key(self, key: remote.RemoteKeyCode, direction: remote.RemoteDirection):
        _LOGGER.debug(f"Sending key press {remote.RemoteKeyCode.Name(key)}, {remote.RemoteDirection.Name(direction)}")
        await self.send(remote.RemoteMessage(
            remote_key_inject=remote.RemoteKeyInject(
                key_code=key,
                direction=direction
            )
        ))
    
    async def send(self, msg: remote.RemoteMessage):
        await self._proto.send(msg)

    async def loop(self, callback: Callable[[remote.RemoteMessage], None]):
        _LOGGER.debug("Starting connection loop")

        while self.connected:
            try:
                msg: remote.RemoteMessage = await self._proto.read()
            except IOError:
                _LOGGER.warning("Stream has been closed, triggering a disconnect.")
                await self.disconnect()
                return

            if msg.HasField("remote_ping_request"):
                _LOGGER.debug("Responding to ping")
                await self.send(
                    remote.RemoteMessage(
                        remote_ping_response=remote.RemotePingResponse(val1=msg.remote_ping_request.val1)
                    )
                )
            elif msg.HasField("remote_configure"):
                _LOGGER.debug(
                    f"""Device Info:
                    Vendor: {msg.remote_configure.device_info.vendor}
                    Model: {msg.remote_configure.device_info.model}
                    Package: {msg.remote_configure.device_info.package_name}
                    App Version: {msg.remote_configure.device_info.app_version}"""
                )

                await self.send(
                    remote.RemoteMessage(
                        remote_configure=remote.RemoteConfigure(
                            code1=622,
                            device_info=remote.RemoteDeviceInfo(
                                model=self.device_info.model,
                                vendor=self.device_info.vendor,
                                unknown1=1,
                                unknown2="1",
                                package_name=self.device_info.package_name,
                                app_version=self.device_info.app_version,
                            ),
                        )
                    )
                )
            elif msg.HasField("remote_set_active"):
                _LOGGER.debug("Set active")
                await self.send(
                    remote.RemoteMessage(
                        remote_set_active=remote.RemoteSetActive(active=622)
                    )
                )
            elif msg.HasField("remote_error"):
                _LOGGER.error(f"Error returned from remote: {msg.remote_error.message}")
            else:
                callback(msg)
        
        _LOGGER.debug("Loop finished")
