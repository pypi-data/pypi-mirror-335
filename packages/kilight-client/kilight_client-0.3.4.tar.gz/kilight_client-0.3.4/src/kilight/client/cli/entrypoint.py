import argparse
import asyncio
import logging
import os
import sys

from argparse import ArgumentParser, Namespace, ArgumentTypeError
from pprint import pprint

from kilight.client.exceptions import KiLightException
from kilight.client.discovery import DiscoveryTool
from .config_manager import ConfigManager
from .device_manager import DeviceManager
from .exceptions import ConfigurationError


def byte_value_type(arg):
    """ Ensures an int is between 0 and 255 """
    try:
        val = int(arg)
    except ValueError:
        raise ArgumentTypeError("Argument must be an integer")
    if val < 0:
        raise ArgumentTypeError("Argument must be >= 0")
    if val > 255:
        raise ArgumentTypeError("Argument must be <= 255")
    return val


async def turn_on_func(device_manager: DeviceManager) -> int:
    await device_manager.device.update_state()
    await device_manager.device.write_output(device_manager.config.output_id, power_on=True)
    return 0

async def turn_off_func(device_manager: DeviceManager) -> int:
    await device_manager.device.update_state()
    await device_manager.device.write_output(device_manager.config.output_id, power_on=False)
    return 0

async def set_output_func(device_manager: DeviceManager) -> int:
    await device_manager.device.update_state()
    await device_manager.device.write_output(device_manager.config.output_id, **device_manager.config.as_output_args)
    return 0

async def get_state_func(device_manager: DeviceManager) -> int:
    await device_manager.device.update_state()
    pprint(device_manager.device.state)
    return 0

async def find_devices_func(config_manager: ConfigManager) -> int:
    async with DiscoveryTool(config_manager.discovery_service_name,
                             config_manager.discovery_time) as discovery_tool:
        print('\nDevices on Network:')
        async for service in discovery_tool.find_devices(config_manager.discovery_num_devices):
            print(f'\t - Device {service.hardware_id} listening at {service.hostname}:{service.port}')
        return 0


def parse_args():
    parser = ArgumentParser(description="Client tool for communicating with KiLight devices.",
                            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-c", "--conf",
                        nargs="+",
                        help="Config files to load. Later files override earlier ones. Search starts in "
                             "directory specified by --config-dir. Default: %(default)s",
                        default=["kilight.ini", "secrets.ini"],
                        dest="config_files")
    parser.add_argument("--config-dir",
                        help="Base directory to find config files in. Defaults to current working directory "
                             "(%(default)s)",
                        default=os.getcwd(),
                        dest="config_dir")
    parser.add_argument("-H", "--host",
                        help="Hostname to connect to. Uses config file Main.DefaultHostName value if not specified.",
                        dest="host")
    parser.add_argument("-P", "--port",
                        help="Port to connect to. Uses config file Main.DefaultPort value if not specified.",
                        dest="port",
                        type=int)
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    subparsers.required = True
    subparser_list = []

    find_devices_cmd = subparsers.add_parser("find", help="Find devices on the network using Zeroconf.")
    find_devices_cmd.add_argument("-t", "--time",
                                  help="Time to wait for devices to respond, in seconds. "
                                       "Uses config file Discovery.DefaultDiscoveryTime value if not specified.",
                                  dest="time",
                                  type=float)
    find_devices_cmd.add_argument("-n", "--num-devices",
                                  help="Max number of devices to find. Defaults to unlimited.",
                                  dest="num_devices",
                                  type=int)
    find_devices_cmd.set_defaults(func=find_devices_func, no_device_manager=True)
    subparser_list.append(find_devices_cmd)

    turn_on_cmd = subparsers.add_parser("on", help="Turn on the light.")
    turn_on_cmd.add_argument("-o", "--output",
                                  help="Select which output to turn on. Defaults to Output %(default)s.",
                                  dest="output",
                                  default="A",
                                  choices=["A", "B"])
    turn_on_cmd.set_defaults(func=turn_on_func)
    subparser_list.append(turn_on_cmd)


    turn_off_cmd = subparsers.add_parser("off", help="Turn off the light.")
    turn_off_cmd.add_argument("-o", "--output",
                                  help="Select which output to turn off. Defaults to Output %(default)s.",
                                  dest="output",
                                  default="A",
                                  choices=["A", "B"])
    turn_off_cmd.set_defaults(func=turn_off_func)
    subparser_list.append(turn_off_cmd)

    get_state_cmd = subparsers.add_parser("get", help="Get the current state of the light.")
    get_state_cmd.set_defaults(func=get_state_func)
    subparser_list.append(get_state_cmd)

    set_output_cmd = subparsers.add_parser("set", help="Set light values.")
    set_output_cmd.add_argument("-o", "--output",
                             help="Select which output to set values of. Defaults to Output %(default)s.",
                             dest="output",
                             default="A",
                             choices=["A", "B"])
    set_output_cmd.add_argument("-r", "--red",
                                help="Set the value of the red channel. Valid range: 0 - 255",
                                dest="red",
                                type=byte_value_type)
    set_output_cmd.add_argument("-g", "--green",
                                help="Set the value of the green channel. Valid range: 0 - 255",
                                dest="green",
                                type=byte_value_type)
    set_output_cmd.add_argument("-b", "--blue",
                                help="Set the value of the blue channel. Valid range: 0 - 255",
                                dest="blue",
                                type=byte_value_type)
    set_output_cmd.add_argument("-w", "--coldWhite",
                                help="Set the value of the cold white channel. Valid range: 0 - 255",
                                dest="cold_white",
                                type=byte_value_type)
    set_output_cmd.add_argument("-W", "--warmWhite",
                                help="Set the value of the warm white channel. Valid range: 0 - 255",
                                dest="warm_white",
                                type=byte_value_type)
    set_output_cmd.add_argument("-B", "--brightness",
                                help="Set the overall brightness value. Valid range: 0 - 255",
                                dest="brightness",
                                type=byte_value_type)
    set_output_cmd_on_off_group = set_output_cmd.add_mutually_exclusive_group()
    set_output_cmd_on_off_group.add_argument("-O", "--on",
                                help="Turn the light on.",
                                dest="on",
                                action="store_true")
    set_output_cmd_on_off_group.add_argument("-N", "--off",
                                help="Turn the light off.",
                                dest="off",
                                action="store_true")
    set_output_cmd.set_defaults(func=set_output_func)
    subparser_list.append(set_output_cmd)

    parser.epilog = 'Detailed command help:\n'

    for subcmd in subparser_list:
        parser.epilog += subcmd.format_help()[7:]
        parser.epilog += '\n'

    return parser.parse_args()


async def run(args: Namespace, config: ConfigManager) -> int:
    log = logging.getLogger()
    try:
        if "no_device_manager" in args and args.no_device_manager:
            return await args.func(config)

        async with DeviceManager(config) as device_manager:
            return await args.func(device_manager)
    except KiLightException as err:
        log.error(str(err), exc_info=True)
        return 3
    except Exception as unexpected_error:
        log.error("Unexpected error: %s", unexpected_error, exc_info=True)
        return 2

def entrypoint():
    # noinspection PyBroadException
    exit_code = 0
    try:
        parsed_args = parse_args()
        config_manager = ConfigManager(parsed_args)
        config_manager.load_config()
        exit_code = asyncio.run(run(parsed_args, config_manager))
    except (KeyboardInterrupt, InterruptedError):
        print("\nBye")
    except ConfigurationError as config_error:
        print("\n" + str(config_error), file=sys.stderr)
        exit_code = 1
    except Exception as unhandled_error:
        print(f"\nUnexpected error: {unhandled_error}", file=sys.stderr)
        exit_code = 2
    return exit_code