from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
import logging
import ssl

from androidtv_remote2.util import ProtoStream

from .proto import remote_pb2 as remote

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    model: str
    vendor: str
    package_name: str
    app_version: str


class CallbackListener(ABC):
    """An interface for callback functions."""

    @abstractmethod
    def on_connection_lost(self, exception: Exception) -> None:
        """Called when client is disconnected unexpectedly."""

    @abstractmethod
    def on_authentication_error(self) -> None:
        """Called when client certificate is rejected by server."""

    @abstractmethod
    def on_connected(self) -> None:
        """Called when client has connected successfully."""

    @abstractmethod
    def on_disconnected(self) -> None:
        """Called when client has disconnected on purpose."""

    @abstractmethod
    def on_message(self, msg: remote.RemoteMessage) -> None:
        """Called when a message is received by the client."""


class RemoteManager:
    def __init__(
        self,
        key_path: str,
        cert_path: str,
        device_info: DeviceInfo,
        listener: CallbackListener,
        host: str,
        port: int = 6466,
    ):
        self.host = host
        self.port = port
        self.key_path = key_path
        self.cert_path = cert_path
        self.connected = False
        self.device_info = device_info
        self.is_on = False
        self.listener = listener

    async def connect(self) -> bool:
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

        try:
            msg: remote.RemoteMessage = await self._proto.read()
        except ssl.SSLError:
            _LOGGER.exception("Authentication failed")
            self.disconnect(wait=False)
            self.listener.on_authentication_error()
            return False
        except OSError as e:
            _LOGGER.exception("Failed to connect")
            self.disconnect(wait=False)
            self.listener.on_connection_lost(e)
            return False

        if not msg.HasField("remote_configure"):
            _LOGGER.warning("Did not receive config message")

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

        self.connected = True
        self.listener.on_connected()
        return True

    async def disconnect(self):
        await self._disconnect(True)
        self.listener.on_disconnected()

    async def _disconnect(self, wait: bool = False):
        self.connected = False
        try:
            self._proto.writer.close()
            if wait:
                await self._proto.writer.wait_closed()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.warning("Failed to disconnect connection")
        finally:
            self._proto = None

    async def send_key(
        self,
        key: "remote.RemoteKeyCode | str",
        direction: remote.RemoteDirection = remote.SHORT,
    ):
        if isinstance(key, str):
            key = remote.RemoteKeyCode.Value(key)

        _LOGGER.debug(
            f"Sending key press {remote.RemoteKeyCode.Name(key)}, {remote.RemoteDirection.Name(direction)}"
        )
        await self.send(
            remote.RemoteMessage(
                remote_key_inject=remote.RemoteKeyInject(
                    key_code=key, direction=direction
                )
            )
        )

    async def send(self, msg: remote.RemoteMessage):
        try:
            await self._proto.send(msg)
        except OSError as e:
            _LOGGER.warning("Stream has been closed, triggering a disconnect.")
            await self._disconnect(wait=False)
            self.listener.on_connection_lost(e)
            return

    async def loop(self):
        _LOGGER.debug("Starting connection loop")

        while self.connected:
            try:
                msg: remote.RemoteMessage = await self._proto.read()
            except OSError as e:
                _LOGGER.warning("Stream has been closed, triggering a disconnect.")
                await self._disconnect(wait=False)
                self.listener.on_connection_lost(e)
                return

            if msg.HasField("remote_ping_request"):
                _LOGGER.debug("Responding to ping")
                await self.send(
                    remote.RemoteMessage(
                        remote_ping_response=remote.RemotePingResponse(
                            val1=msg.remote_ping_request.val1
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
            elif msg.HasField("remote_start"):
                self.is_on = msg.remote_start.started

            self.listener.on_message(msg)

        _LOGGER.debug("Loop finished")
