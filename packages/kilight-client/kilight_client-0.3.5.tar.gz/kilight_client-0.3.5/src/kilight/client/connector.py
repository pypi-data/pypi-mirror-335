from __future__ import annotations

import logging
import struct
from asyncio import (StreamReaderProtocol,
                     AbstractEventLoop,
                     StreamReader,
                     StreamWriter,
                     transports,
                     events,
                     Lock,
                     wait_for,
                     TimeoutError,
                     sleep)

from collections.abc import Callable
from dataclasses import replace
from typing import Any, Coroutine

from kilight.protocol import GetData, Request, Response, CommandResult, OutputIdentifier
from .const import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT, DEFAULT_RESPONSE_TIMEOUT
from .exceptions import ConnectionTimeoutError, ResponseTimeoutError, RequestTimeoutError, NetworkTimeoutError
from .models import DeviceState, OutputState, TemperatureState, VersionInfo

_LOGGER = logging.getLogger(__name__)

class NotifyingProtocol(StreamReaderProtocol):

    def __init__(self,
                 on_disconnected_callback: Callable[[], Coroutine[Any, Any, None]] | None = None,
                 loop: AbstractEventLoop = None):
        self._reader = StreamReader(loop=loop)
        super().__init__(self._reader, loop=loop)
        self._loop: AbstractEventLoop = loop
        self._connected: bool = False
        self._on_disconnected_callback: Callable[None] | None = on_disconnected_callback

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def reader(self) -> StreamReader:
        return self._reader

    def connection_made(self, transport: transports.Transport):
        self._connected = True
        super().connection_made(transport)

    def connection_lost(self, exc):
        self._connected = False
        super().connection_lost(exc)
        if self._on_disconnected_callback:
            self._loop.create_task(self._on_disconnected_callback())


class Connector:
    def __init__(self, host: str, port: int, **kwargs):
        self._host: str = host
        self._port: int = port
        self._connection_timeout: int = int(kwargs.get("connection_timeout", DEFAULT_CONNECTION_TIMEOUT))
        self._request_timeout: int = int(kwargs.get("request_timeout", DEFAULT_REQUEST_TIMEOUT))
        self._response_timeout: int = int(kwargs.get("response_timeout", DEFAULT_RESPONSE_TIMEOUT))
        self._operation_lock = Lock()
        self._reader: StreamReader | None = None
        self._writer: StreamWriter | None = None
        self._protocol: NotifyingProtocol | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def connection_timeout(self) -> int:
        return self._connection_timeout

    @property
    def request_timeout(self) -> int:
        return self._request_timeout

    @property
    def response_timeout(self) -> int:
        return self._response_timeout

    async def disconnect(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    async def _send_request(self, request: Request, writer: StreamWriter) -> None:
        try:
            writer.write(struct.pack("<B", request.ByteSize()))
            writer.write(request.SerializeToString())
            await wait_for(writer.drain(), timeout=self.request_timeout)
        except TimeoutError:
            raise RequestTimeoutError(self.host, self.port, self.response_timeout)

    async def _read_response(self, reader: StreamReader) -> Response:

        try:
            length: int = struct.unpack("<B", await wait_for(reader.readexactly(1), timeout=self.response_timeout))[0]
        except TimeoutError:
            raise ResponseTimeoutError(self.host, self.port, self.response_timeout)

        if length <= 0:
            raise ValueError("Received invalid message length of zero")

        response = Response()
        try:
            response.ParseFromString(await wait_for(reader.readexactly(length), timeout=self.response_timeout))
        except TimeoutError:
            raise ResponseTimeoutError(self.host, self.port, self.response_timeout)
        return response

    async def _request_and_parse_state[DataClassReturnT: DeviceState](self,
                                                                      state_to_update: DataClassReturnT,
                                                                      reader: StreamReader,
                                                                      writer: StreamWriter) -> DataClassReturnT:
        _LOGGER.debug("Requesting state info...")
        request = Request(getData=GetData.GetSystemState)
        await self._send_request(request, writer)

        _LOGGER.debug("Reading state message...")
        response = await self._read_response(reader)

        if not response.HasField("systemState"):
            raise ValueError(f"Unexpected message received instead of systemState: {response}")

        _LOGGER.debug("Read state message")

        output_b_state = None
        if response.systemState.HasField("outputB"):
            output_b_state = OutputState.from_protocol(response.systemState.outputB)

        power_supply_temperature_state = None
        if response.systemState.temperatures.HasField("powerSupply"):
            power_supply_temperature_state = TemperatureState(
                celsius=response.systemState.temperatures.powerSupply / 100
            )

        return replace(state_to_update,
                       output_a=OutputState.from_protocol(response.systemState.outputA),
                       output_b=output_b_state,
                       driver_temperature=TemperatureState(
                           celsius=response.systemState.temperatures.driver / 100
                       ),
                       power_supply_temperature=power_supply_temperature_state,
                       fan_speed=response.systemState.fan.rpm,
                       fan_drive_percentage=response.systemState.fan.outputPerThou / 10
                       )

    async def _request_and_parse_system_info[DataClassReturnT: DeviceState](self,
                                                                            state_to_update: DataClassReturnT,
                                                                            reader: StreamReader,
                                                                            writer: StreamWriter) -> DataClassReturnT:
        _LOGGER.debug("Requesting system info...")
        request = Request(getData=GetData.GetSystemInfo)
        await self._send_request(request, writer)

        _LOGGER.debug("Reading system info message...")
        response = await self._read_response(reader)

        if not response.HasField("systemInfo"):
            raise ValueError(f"Unexpected message received instead of systemInfo: {response}")

        _LOGGER.debug("Read system info message")

        return replace(state_to_update,
                       hardware_id=response.systemInfo.hardwareId,
                       model=response.systemInfo.model,
                       manufacturer_name=response.systemInfo.manufacturer,
                       firmware_version=VersionInfo.from_protocol(response.systemInfo.firmwareVersion),
                       hardware_version=VersionInfo.from_protocol(response.systemInfo.hardwareVersion)
                       )

    async def _write_output_update(self,
                                   output_id: OutputIdentifier,
                                   write_state: OutputState,
                                   reader: StreamReader,
                                   writer: StreamWriter) -> bool:
        _LOGGER.debug("Sending write request...")
        request = Request(writeOutput=write_state.to_protocol(output_id))
        await self._send_request(request, writer)

        _LOGGER.debug("Reading write request command response...")
        response: Response = await self._read_response(reader)

        if not response.HasField("commandResult"):
            raise ValueError(f"Unexpected message received instead of commandResult: {response}")

        if response.commandResult.result != CommandResult.Result.OK:
            _LOGGER.warning("Write request returned non-OK result")
            return False

        _LOGGER.debug("Write request OK")
        return True

    async def open_connection(self):
        _LOGGER.debug("Connecting to %s:%s...", self.host, self.port)

        async def on_disconnected():
            async with self._operation_lock:
                _LOGGER.debug("Disconnected from %s:%s", self.host, self.port)
                self._reader = None
                self._writer = None
                self._protocol = None

        loop = events.get_running_loop()
        try:
            transport, protocol = await wait_for(loop.create_connection(
                lambda: NotifyingProtocol(on_disconnected_callback=on_disconnected, loop=loop),
                self.host,
                self.port),
                timeout=self.connection_timeout)

            self._protocol = protocol
            self._reader = self._protocol.reader
            self._writer = StreamWriter(transport, self._protocol, self._reader, loop)
            _LOGGER.debug("Connected.")
        except TimeoutError:
            raise ConnectionTimeoutError(self.host, self.port, self.connection_timeout)

    async def _connect_and_run[ReturnT](self,
                                        lambda_to_run: Callable[[StreamReader, StreamWriter],
                                                                Coroutine[Any, Any, ReturnT]]) -> ReturnT:
        try:
            async with self._operation_lock:
                if self._protocol is None:
                    await self.open_connection()

                return await lambda_to_run(self._reader, self._writer)
        except NetworkTimeoutError as err:
            _LOGGER.error("Operation timed out")
            await self.disconnect()
            raise err

    async def read_state(self, state_to_update: DeviceState) -> DeviceState:
        async def wrapper(reader: StreamReader, writer: StreamWriter) -> DeviceState:
            return await self._request_and_parse_state(state_to_update, reader, writer)

        return await self._connect_and_run(wrapper)

    async def read_system_info_and_state(self, state_to_update: DeviceState) -> DeviceState:
        async def wrapper(reader: StreamReader, writer: StreamWriter) -> DeviceState:
            working_state = await self._request_and_parse_system_info(state_to_update, reader, writer)
            return await self._request_and_parse_state(working_state, reader, writer)

        return await self._connect_and_run(wrapper)

    async def write_update(self,
                           output_id: OutputIdentifier,
                           output_state: OutputState) -> None:
        async def write_wrapper(reader: StreamReader, writer: StreamWriter):
            await self._write_output_update(output_id, output_state, reader, writer)

        await self._connect_and_run(write_wrapper)

    async def write_update_and_read_state(self,
                                          state_to_update: DeviceState,
                                          output_id: OutputIdentifier,
                                          output_state: OutputState) -> DeviceState:
        async def write_wrapper(reader: StreamReader, writer: StreamWriter):
            await self._write_output_update(output_id, output_state, reader, writer)
            await sleep(0.1)
            return await self._request_and_parse_state(state_to_update, reader, writer)

        return await self._connect_and_run(write_wrapper)
