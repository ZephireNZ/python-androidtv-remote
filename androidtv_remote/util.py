import logging
from asyncio import StreamReader, StreamWriter
from types import FunctionType
from typing import Callable, TypeVar

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.message import Message

_LOGGER = logging.getLogger(__name__)


class ProtoStream:
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        msg_func: Callable[[], Message],
    ):
        self.reader = reader
        self.writer = writer
        self.msg_func = msg_func

    async def send(self, msg: Message):
        size = msg.ByteSize()
        self.writer.write(_VarintBytes(size))
        self.writer.write(msg.SerializeToString())
        await self.writer.drain()

    async def read(self) -> Message:
        length_buf = bytearray()

        while True:
            buf = await self.reader.read(1)
            length_buf.append(buf[0])
            if buf[0] & 0x80 == 0:  # Check MSB for end of VarInt
                break

        length: int
        length, _ = _DecodeVarint32(length_buf, 0)

        _LOGGER.debug(f"Expecting message of length {length}")

        msg = self.msg_func()

        raw_bytes = await self.reader.read(length)

        msg.ParseFromString(raw_bytes)

        return msg
