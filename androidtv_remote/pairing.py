from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
import asyncio
import ssl
import logging
from hashlib import sha256
from androidtv_remote import WrongPINError
from cryptography.hazmat.primitives import serialization

from androidtv_remote.const import PROTOCOL_VERSION

from .proto import pairing_pb2 as pairing


_LOGGER = logging.getLogger(__name__)

class PairingManager:
    def __init__(
        self,
        key_path: str,
        cert_path: str,
        host: str,
        port: int = 6467,
    ):
        self.host = host
        self.port = port
        self.key_path = key_path
        self.cert_path = cert_path

        with open(self.cert_path, "rb") as f:
            self.cert = x509.load_pem_x509_certificate(f.read())

    async def start_pairing(self, client_name = "python-androidtv-remote"):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_cert_chain(
            certfile=self.cert_path, 
            keyfile=self.key_path,
        )
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.VerifyMode.CERT_NONE

        _LOGGER.debug("Connecting to TV")
        self.reader, self.writer = await asyncio.open_connection(
            host=self.host, 
            port=self.port, 
            ssl=ssl_ctx,
        )

        ssl_socket: ssl.SSLSocket = self.writer.get_extra_info("ssl_object")
        self.server_cert = x509.load_der_x509_certificate(
            ssl_socket.getpeercert(binary_form=True)
        )

        _LOGGER.debug("Sending pair request")
        await self._send(pairing.PairingMessage(
            protocol_version=PROTOCOL_VERSION,
            status=pairing.PairingMessage.STATUS_OK,
            pairing_request=pairing.PairingRequest(
                service_name="python-androidtv-remote",
                client_name=client_name,
            ),
        ))

        _LOGGER.debug("Awaiting request ack")
        ack = await self._read()
        if ack.status != pairing.PairingMessage.STATUS_OK:
            raise ConnectionError(f"Failed to start pairing: {ack.status}")

        _LOGGER.debug("Sending options")
        await self._send(pairing.PairingMessage(
            protocol_version=PROTOCOL_VERSION,
            status=pairing.PairingMessage.STATUS_OK,
            pairing_option=pairing.PairingOption(
                preferred_role=pairing.ROLE_TYPE_INPUT,
                input_encodings=[pairing.PairingEncoding(
                    type=pairing.PairingEncoding.ENCODING_TYPE_HEXADECIMAL,
                    symbol_length=6
                )]
            )
        ))

        _LOGGER.debug("Awaiting options ack")
        ack = await self._read()
        if ack.status != pairing.PairingMessage.STATUS_OK:
            raise ConnectionError(f"Failed to agree options: {ack.status}")
        
        _LOGGER.debug("Sending configuration")
        await self._send(pairing.PairingMessage(
            protocol_version=PROTOCOL_VERSION,
            status=pairing.PairingMessage.STATUS_OK,
            pairing_configuration=pairing.PairingConfiguration(
                client_role=pairing.ROLE_TYPE_INPUT,
                encoding=pairing.PairingEncoding(
                    type=pairing.PairingEncoding.ENCODING_TYPE_HEXADECIMAL,
                    symbol_length=6
                )
            )
        ))

        _LOGGER.debug("Awaiting configuration ack")
        ack = await self._read()
        if ack.status != pairing.PairingMessage.STATUS_OK:
            raise ConnectionError(f"Failed to agree configuration: {ack.status}")
    
    async def send_secret(self, code: str):
        encoded = self.encode_secret(code)

        await self._send(pairing.PairingMessage(
            protocol_version=PROTOCOL_VERSION,
            status=pairing.PairingMessage.STATUS_OK,
            pairing_secret=pairing.PairingSecret(
                secret=encoded
            )
        ))

        _LOGGER.debug("Awaiting secret ack")
        ack = await self._read()
        if ack.status != pairing.PairingMessage.STATUS_OK:
            raise WrongPINError()



    def encode_secret(self, code: str) -> bytes:
        code_bytes = bytes.fromhex(code)

        

        cert_numbers: rsa.RSAPublicNumbers = self.cert.public_key().public_numbers()
        server_cert_numbers: rsa.RSAPublicNumbers = self.server_cert.public_key().public_numbers()

        hash = sha256()
        hash.update(abs(cert_numbers.n).to_bytes(2048//8, byteorder='big').lstrip(b'\x00'))
        hash.update(abs(cert_numbers.e).to_bytes(2048//8, byteorder='big').lstrip(b'\x00'))
        hash.update(abs(server_cert_numbers.n).to_bytes(2048//8, byteorder='big').lstrip(b'\x00'))
        hash.update(abs(server_cert_numbers.e).to_bytes(2048//8, byteorder='big').lstrip(b'\x00'))
        hash.update(bytes.fromhex(code[2:]))

        result = hash.digest()

        if result[0] != code_bytes[0]:
            raise WrongPINError()
        
        return result
        

    
    async def _send(self, msg: pairing.PairingMessage):
        self.writer.write(msg.ByteSize().to_bytes(1, byteorder='big'))
        await self.writer.drain()

        self.writer.write(msg.SerializeToString())
        await self.writer.drain()
    
    async def _read(self) -> pairing.PairingMessage:
        length = int.from_bytes(await self.reader.read(1), byteorder='big', signed=False)
        _LOGGER.debug(f"Expecting message of length {length}")

        raw_bytes = await self.reader.read(length)

        msg = pairing.PairingMessage()
        msg.ParseFromString(raw_bytes)

        return msg

        
