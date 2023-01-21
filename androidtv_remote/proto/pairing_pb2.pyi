from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
ROLE_TYPE_INPUT: RoleType
ROLE_TYPE_OUTPUT: RoleType
ROLE_TYPE_UNKNOWN: RoleType
UNRECOGNIZED: RoleType

class PairingConfiguration(_message.Message):
    __slots__ = ["client_role", "encoding"]
    CLIENT_ROLE_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    client_role: RoleType
    encoding: PairingEncoding
    def __init__(self, encoding: _Optional[_Union[PairingEncoding, _Mapping]] = ..., client_role: _Optional[_Union[RoleType, str]] = ...) -> None: ...

class PairingConfigurationAck(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PairingEncoding(_message.Message):
    __slots__ = ["symbol_length", "type"]
    class EncodingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ENCODING_TYPE_ALPHANUMERIC: PairingEncoding.EncodingType
    ENCODING_TYPE_HEXADECIMAL: PairingEncoding.EncodingType
    ENCODING_TYPE_NUMERIC: PairingEncoding.EncodingType
    ENCODING_TYPE_QRCODE: PairingEncoding.EncodingType
    ENCODING_TYPE_UNKNOWN: PairingEncoding.EncodingType
    SYMBOL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNRECOGNIZED: PairingEncoding.EncodingType
    symbol_length: int
    type: PairingEncoding.EncodingType
    def __init__(self, type: _Optional[_Union[PairingEncoding.EncodingType, str]] = ..., symbol_length: _Optional[int] = ...) -> None: ...

class PairingMessage(_message.Message):
    __slots__ = ["pairing_configuration", "pairing_configuration_ack", "pairing_option", "pairing_request", "pairing_request_ack", "pairing_secret", "pairing_secret_ack", "protocol_version", "request_case", "status"]
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    PAIRING_CONFIGURATION_ACK_FIELD_NUMBER: _ClassVar[int]
    PAIRING_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    PAIRING_OPTION_FIELD_NUMBER: _ClassVar[int]
    PAIRING_REQUEST_ACK_FIELD_NUMBER: _ClassVar[int]
    PAIRING_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PAIRING_SECRET_ACK_FIELD_NUMBER: _ClassVar[int]
    PAIRING_SECRET_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_CASE_FIELD_NUMBER: _ClassVar[int]
    STATUS_BAD_CONFIGURATION: PairingMessage.Status
    STATUS_BAD_SECRET: PairingMessage.Status
    STATUS_ERROR: PairingMessage.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_OK: PairingMessage.Status
    UNKNOWN: PairingMessage.Status
    UNRECOGNIZED: PairingMessage.Status
    pairing_configuration: PairingConfiguration
    pairing_configuration_ack: PairingConfigurationAck
    pairing_option: PairingOption
    pairing_request: PairingRequest
    pairing_request_ack: PairingRequestAck
    pairing_secret: PairingSecret
    pairing_secret_ack: PairingSecretAck
    protocol_version: int
    request_case: int
    status: PairingMessage.Status
    def __init__(self, protocol_version: _Optional[int] = ..., status: _Optional[_Union[PairingMessage.Status, str]] = ..., request_case: _Optional[int] = ..., pairing_request: _Optional[_Union[PairingRequest, _Mapping]] = ..., pairing_request_ack: _Optional[_Union[PairingRequestAck, _Mapping]] = ..., pairing_option: _Optional[_Union[PairingOption, _Mapping]] = ..., pairing_configuration: _Optional[_Union[PairingConfiguration, _Mapping]] = ..., pairing_configuration_ack: _Optional[_Union[PairingConfigurationAck, _Mapping]] = ..., pairing_secret: _Optional[_Union[PairingSecret, _Mapping]] = ..., pairing_secret_ack: _Optional[_Union[PairingSecretAck, _Mapping]] = ...) -> None: ...

class PairingOption(_message.Message):
    __slots__ = ["input_encodings", "output_encodings", "preferred_role"]
    INPUT_ENCODINGS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_ENCODINGS_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_ROLE_FIELD_NUMBER: _ClassVar[int]
    input_encodings: _containers.RepeatedCompositeFieldContainer[PairingEncoding]
    output_encodings: _containers.RepeatedCompositeFieldContainer[PairingEncoding]
    preferred_role: RoleType
    def __init__(self, input_encodings: _Optional[_Iterable[_Union[PairingEncoding, _Mapping]]] = ..., output_encodings: _Optional[_Iterable[_Union[PairingEncoding, _Mapping]]] = ..., preferred_role: _Optional[_Union[RoleType, str]] = ...) -> None: ...

class PairingRequest(_message.Message):
    __slots__ = ["client_name", "service_name"]
    CLIENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    client_name: str
    service_name: str
    def __init__(self, client_name: _Optional[str] = ..., service_name: _Optional[str] = ...) -> None: ...

class PairingRequestAck(_message.Message):
    __slots__ = ["server_name"]
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    server_name: str
    def __init__(self, server_name: _Optional[str] = ...) -> None: ...

class PairingSecret(_message.Message):
    __slots__ = ["secret"]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: bytes
    def __init__(self, secret: _Optional[bytes] = ...) -> None: ...

class PairingSecretAck(_message.Message):
    __slots__ = ["secret"]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: bytes
    def __init__(self, secret: _Optional[bytes] = ...) -> None: ...

class RoleType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
