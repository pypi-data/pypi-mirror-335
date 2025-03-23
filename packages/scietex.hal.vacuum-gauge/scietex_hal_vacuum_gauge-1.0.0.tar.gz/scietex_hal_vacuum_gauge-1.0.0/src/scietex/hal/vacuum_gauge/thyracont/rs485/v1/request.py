"""
Thyracont RS485 Version 1 Request Module.

This module defines a custom Modbus Protocol Data Unit (PDU) for Thyracont's RS485 protocol,
extending `pymodbus.pdu.ModbusPDU`. It encapsulates Thyracont-specific requests, which consist of a
single-character command and up to 6 bytes of data, and integrates with a Modbus slave context via
the `parse_command` utility. The class handles encoding, decoding, and executing these requests,
emulating the communication behavior of a Thyracont vacuum gauge (e.g., MTM9D) over RS485.

Classes:
    ThyracontRequest: A custom Modbus PDU class for Thyracont RS485 requests, supporting command
        execution and response generation.
"""

from typing import Optional
from pymodbus.pdu import ModbusPDU
from pymodbus.datastore import ModbusSlaveContext

from .emulation_utils import parse_command


class ThyracontRequest(ModbusPDU):
    """
    Thyracont custom protocol request.

    A custom Modbus PDU class for Thyracont's RS485 protocol, designed to handle single-character
    commands (e.g., "M", "s") and associated data payloads (up to 6 bytes). It extends `ModbusPDU`
    to support encoding, decoding, and asynchronous execution of requests against a Modbus slave
    context, using `parse_command` from `emulation_utils` to process the request and generate a
    response.

    Attributes
    ----------
    function_code : int
        The function code, derived from the first byte of the command (default 0 if no command).
    rtu_frame_size : int
        The size of the data payload in bytes (up to 6).
    command : str
        The single-character command (e.g., "T", "M"), extracted from the input `command`.
    data : str
        The data payload as a string, decoded from up to 6 bytes of input `data`.
    dev_id : int
        The device (slave) ID, inherited from `ModbusPDU`.
    transaction_id : int
        The transaction ID, inherited from `ModbusPDU`.
    registers : list
        A list of response bytes, set after execution (not used in request encoding).

    Methods
    -------
    __init__(command: Optional[str] = None, data: Optional[bytes] = None, slave=1, transaction=0)
        -> None
        Initializes the request with command, data, slave ID, and transaction ID.
    encode() -> bytes
        Encodes the request data into bytes.
    decode(data: bytes) -> None
        Decodes a byte string into the request’s data attribute.
    update_datastore(context: ModbusSlaveContext) -> ModbusPDU
        Executes the request against a Modbus slave context and returns a response PDU.
    """

    function_code = 0
    rtu_frame_size = 0

    def __init__(
        self,
        command: Optional[str] = None,
        data: Optional[bytes] = None,
        slave=1,
        transaction=0,
    ) -> None:
        """
        Initialize an ThyracontRequest instance.

        Sets up the request with a command, data payload, slave ID, and transaction ID. The command
        is limited to its first character, and the data is decoded from up to 6 bytes into a string.
        The `function_code` is derived from the command’s first byte.

        Parameters
        ----------
        command : Optional[str], optional
            The command string (e.g., "T", "M"); only the first character is used. Defaults to None,
            resulting in an empty command ("").
        data : Optional[bytes], optional
            The data payload in bytes (e.g., b"123456"); limited to 6 bytes and decoded to a string.
            Defaults to None, resulting in an empty data string ("").
        slave : int, optional
            The device (slave) ID. Defaults to 1.
        transaction : int, optional
            The transaction ID. Defaults to 0.
        """
        super().__init__(dev_id=slave, transaction_id=transaction)
        self.command: str = ""
        if command is not None and len(command) > 0:
            self.command = command[0]
        self.function_code = self.command.encode()[0] if self.command else 0
        self.__data: str = ""
        self.rtu_frame_size = 0
        if data is not None:
            self.data = data[:6].decode()

    @property
    def data(self) -> str:
        """Data property."""
        return self.__data

    @data.setter
    def data(self, new_data: str) -> None:
        self.__data = new_data[:6]
        self.rtu_frame_size = len(self.__data)

    def encode(self) -> bytes:
        """
        Encode the request data into bytes.

        Converts the `data` attribute (a string) into a byte string for transmission. The command
        is not included in the encoded output, as it’s handled separately by the framer.

        Returns
        -------
        bytes
            The encoded data payload (e.g., b"123456").
        """
        return self.data.encode()

    def decode(self, data: bytes) -> None:
        """
        Decode a byte string into the request’s data attribute.

        Updates the `data` attribute by decoding the input bytes into a string. The command is not
        modified, as it’s assumed to be set during initialization or handled by the framer.

        Parameters
        ----------
        data : bytes
            The byte string to decode (e.g., b"123456").
        """
        self.data = data.decode()

    async def update_datastore(self, context: ModbusSlaveContext) -> ModbusPDU:
        """
        Execute the request against a Modbus slave context and return a response PDU.

        Processes the request by calling `parse_command` with the command and data, then constructs
        a response `ThyracontRequest` instance with the resulting data. The response includes the
        original command, slave ID, and transaction ID, and stores the response bytes in the
        `registers` attribute as a list.

        Parameters
        ----------
        context : ModbusSlaveContext
            The Modbus slave context containing the holding register store to update or read from.

        Returns
        -------
        ModbusPDU
            An `ThyracontRequest` instance representing the response, with `registers` set to the
            list of response bytes.
        """
        data: bytes = parse_command(context, self.command, self.data)
        response = ThyracontRequest(
            self.command,
            data,
            slave=self.dev_id,
            transaction=self.transaction_id,
        )
        response.registers = list(data)
        return response
