import logging
import asyncio
import re
import sys

from asyncio import Task, Event
from typing import cast, AsyncIterator

from zeroconf import ServiceListener, Zeroconf
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser, AsyncServiceInfo

from kilight.client.const import DEFAULT_DISCOVERY_SERVICE_NAME, DEFAULT_DISCOVERY_TIME
from kilight.client.models import DiscoveredDeviceInfo

_LOGGER = logging.getLogger(__name__)


class DiscoveryTool:

    class _ServiceListener(ServiceListener):
        def __init__(self, parent: "DiscoveryTool"):
            self._parent = parent

        def add_service(self, _: Zeroconf, service_type: str, name: str) -> None:
            self._parent._queue_interrogate_service(service_type, name)

        def remove_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
            """We only care about newly discovered services. Method overridden just so we don't get NotImplementedError"""

        def update_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
            """We only care about newly discovered services. Method overridden just so we don't get NotImplementedError"""

    def __init__(self,
                 service_name: str = DEFAULT_DISCOVERY_SERVICE_NAME,
                 discovery_wait_time: float = DEFAULT_DISCOVERY_TIME):
        self._service_name = service_name
        self._discovery_wait_time = discovery_wait_time
        self._zeroconf: AsyncZeroconf | None = None
        self._browser: AsyncServiceBrowser | None = None
        self._device_found_flag = Event()
        self._found_devices: list[DiscoveredDeviceInfo] = []
        self._pending_tasks: set[Task[None]] = set()

    async def __aenter__(self) -> "DiscoveryTool":
        self._zeroconf = AsyncZeroconf()
        self._browser = AsyncServiceBrowser(
            self._zeroconf.zeroconf,
            [self._service_name],
            listener=DiscoveryTool._ServiceListener(self),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self._browser is not None
        await self._browser.async_cancel()
        self._browser = None

        assert self._zeroconf is not None
        await self._zeroconf.async_close()
        self._zeroconf = None

    @property
    def found_devices(self) -> list[DiscoveredDeviceInfo]:
        return self._found_devices

    def _queue_interrogate_service(self, service_type: str, name: str):
        task = asyncio.ensure_future(self._read_service_info(service_type, name))
        self._pending_tasks.add(task)
        task.add_done_callback(self._pending_tasks.remove)

    async def find_devices(self, max_devices_to_find: int | None = None) -> AsyncIterator[DiscoveredDeviceInfo]:
        if max_devices_to_find is None:
            max_devices_to_find = float('inf')
        try:
            async with asyncio.timeout(self._discovery_wait_time):
                device_index = 0
                while device_index < max_devices_to_find:
                    if len(self._found_devices) <= device_index:
                        await self._device_found_flag.wait()
                        self._device_found_flag.clear()
                    else:
                        yield self._found_devices[device_index]
                        device_index += 1
        except TimeoutError:
            # This is a normal way to exit the search loop
            pass

    async def _read_service_info(self, service_type: str, name: str) -> None:
        info = AsyncServiceInfo(service_type, name)
        await info.async_request(self._zeroconf.zeroconf, self._discovery_wait_time)
        if info:
            hwid = None
            if b'hwid' in info.properties:
                hwid = info.properties[b'hwid'].decode("utf-8")

            self._found_devices.append(DiscoveredDeviceInfo(
                name=info.name,
                hostname=re.sub(r'\.$', '', info.server),
                port=info.port,
                hardware_id=hwid
            ))
            self._device_found_flag.set()
        else:
            _LOGGER.debug("No info found for zeroconf service %s", name)

