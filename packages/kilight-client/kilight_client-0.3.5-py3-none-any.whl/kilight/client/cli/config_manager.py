import logging
import logging.config
import os
from pathlib import Path

from pkg_resources import resource_filename
from configparser import ConfigParser, SectionProxy
from argparse import Namespace

from .exceptions import MissingConfigSectionError, ConfigurationError
from .. import DEFAULT_PORT
from ..const import DEFAULT_DISCOVERY_TIME, DEFAULT_DISCOVERY_SERVICE_NAME
from ...protocol import OutputIdentifier

_LOGGER = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, parsed_args: Namespace):
        self._parsed_args = parsed_args
        self._parser = ConfigParser()
        self._config_dir: Path | None = None
        self._log_config_file_path: Path | None = None
        self._host: str | None = None
        self._port: int | None = None
        self._discovery_time: float | None = None

    def load_config(self):
        config_files: list[Path] = list()
        config_files.append(resource_filename('kilight.client.cli', 'config/kilight-defaults.ini'))
        for file in self._parsed_args.config_files:
            file = Path(file)
            if file.is_absolute():
                config_files.append(file)
            else:
                config_files.append(self.config_dir / file)
        sources = self._parser.read(config_files)
        if os.path.exists(self.log_config_file):
            logging.config.fileConfig(self.log_config_file)
        else:
            logging.config.fileConfig(resource_filename('kilight.client.cli', 'config/logging.ini'))

        _LOGGER.info("Loaded config from: %s", sources)

    @property
    def config_dir(self) -> Path:
        if self._config_dir is None:
            self._config_dir = Path(self._parsed_args.config_dir)

        return self._config_dir

    @property
    def main_config_section(self) -> SectionProxy:
        if not self._parser.has_section("Main"):
            raise MissingConfigSectionError("Main")
        return self._parser["Main"]

    @property
    def discovery_config_section(self) -> SectionProxy:
        if not self._parser.has_section("Discovery"):
            raise MissingConfigSectionError("Discovery")
        return self._parser["Discovery"]

    @property
    def log_config_file(self) -> Path:
        if self._log_config_file_path is None:
            self._log_config_file_path = Path(self.main_config_section.get("LogConfigFile", fallback="logging.ini"))
            if not self._log_config_file_path.is_absolute():
                self._log_config_file_path = self.config_dir / self._log_config_file_path

        return self._log_config_file_path

    @property
    def host(self) -> str:
        if self._host is None:
            if self._parsed_args.host is not None:
                self._host = self._parsed_args.host
            elif self._parser.has_option("Main", "DefaultHostName"):
                self._host = self.main_config_section["DefaultHostName"]
            else:
                raise ConfigurationError("no specified --host, and no configured Main.DefaultHostName")

        return self._host

    @property
    def port(self) -> int:
        if self._port is None:
            if self._parsed_args.port is not None:
                self._port = self._parsed_args.port
            else:
                self._port = self.main_config_section.getint("DefaultPort", fallback=DEFAULT_PORT)

        return self._port

    @property
    def connect_timeout(self) -> int:
        return self.main_config_section.getint("ConnectTimeout", fallback=15)

    @property
    def request_timeout(self) -> int:
        return self.main_config_section.getint("RequestTimeout", fallback=15)

    @property
    def output_id(self) -> OutputIdentifier:
        if self._parsed_args.output is not None:
            output_upper = str(self._parsed_args.output).upper()
            if output_upper == 'A':
                return OutputIdentifier.OutputA
            if output_upper == 'B':
                return OutputIdentifier.OutputB
            else:
                raise ConfigurationError(f"Invalid value for --output: {self._parsed_args.output}")
        return OutputIdentifier.OutputA

    @property
    def red(self) -> int | None:
        return self._parsed_args.red

    @property
    def green(self) -> int | None:
        return self._parsed_args.green

    @property
    def blue(self) -> int | None:
        return self._parsed_args.blue

    @property
    def cold_white(self) -> int | None:
        return self._parsed_args.cold_white

    @property
    def warm_white(self) -> int | None:
        return self._parsed_args.warm_white

    @property
    def brightness(self) -> int | None:
        return self._parsed_args.brightness

    @property
    def turn_on(self) -> bool | None:
        return self._parsed_args.on

    @property
    def turn_off(self) -> bool | None:
        return self._parsed_args.off

    @property
    def as_output_args(self) -> dict:
        output_args = dict()
        if self.red is not None:
            output_args['red'] = self.red

        if self.green is not None:
            output_args['green'] = self.green

        if self.blue is not None:
            output_args['blue'] = self.blue

        if self.cold_white is not None:
            output_args['cold_white'] = self.cold_white

        if self.warm_white is not None:
            output_args['warm_white'] = self.warm_white

        if self.brightness is not None:
            output_args['brightness'] = self.brightness

        if self.turn_on:
            output_args['power_on'] = True

        if self.turn_off:
            output_args['power_on'] = False

        return output_args

    @property
    def discovery_service_name(self) -> str:
        return self.discovery_config_section.get("ServiceName", fallback=DEFAULT_DISCOVERY_SERVICE_NAME)

    @property
    def discovery_time(self) -> float:
        if self._discovery_time is None:
            if self._parsed_args.time is not None:
                self._discovery_time = self._parsed_args.time
            else:
                self._discovery_time = self.discovery_config_section.getfloat("DefaultDiscoveryTime",
                                                                              fallback=DEFAULT_DISCOVERY_TIME)

        return self._discovery_time

    @property
    def discovery_num_devices(self) -> int | None:
        return self._parsed_args.num_devices