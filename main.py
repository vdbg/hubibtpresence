#!/usr/bin/python3

from pathlib import Path
import logging
import platform
from time import sleep
import sys
import yaml

from collector import Collector
from hubitat import Hubitat

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


def report(runs: int, devices: dict, hubitat: Hubitat) -> None:
    logging.info(f"Running bluetooth scanning up to {runs} time(s)...")

    devices_to_find: set = set(map(str.upper, devices.keys))
    collector = Collector()

    for _ in range(runs):
        collector.run()

        devices_found = collector.devices_rssi
        devices_to_remove = set()

        if logging.root.isEnabledFor(logging.DEBUG):
            for mac, rssi in sorted(devices_found.items()):
                logging.debug(f"{mac}:{rssi}")

        for device in devices_to_find:
            name = device
            data = devices[name]
            if data and "name" in data:
                name = name + " (" + data["name"] + ")"
            present: bool = False
            rssi = None
            if device in devices_found:
                minRSSI = data.get("minRSSI", -1000)
                rssi = devices_found[device]
                present = rssi > minRSSI
                if present:
                    devices_to_remove.add(device)

            logging.info(f"{'PRESENT' if present else ' ABSENT'} - {name} - RSSI={rssi} ")

            hubitatId: int = data.get("hubitatId", -1)
            if hubitatId > 0:
                hubitat.set_presence(hubitatId, present)

        for name in devices_to_remove:
            devices_to_find.remove(name)

        if not devices_to_find:
            return


CONFIG_FILE = "config.yaml"
SUPPORTED_PYTHON_MAJOR = 3
SUPPORTED_PYTHON_MINOR = 9


def main() -> None:

    if sys.version_info < (SUPPORTED_PYTHON_MAJOR, SUPPORTED_PYTHON_MINOR):
        raise Exception(f"Python version {SUPPORTED_PYTHON_MAJOR}.{SUPPORTED_PYTHON_MINOR} or later required. Current version: {platform.python_version()}.")

    try:
        with open(Path(__file__).with_name(CONFIG_FILE)) as config_file:

            config = yaml.safe_load(config_file)

            if not config:
                raise ValueError(f"Invalid {CONFIG_FILE}. See template.{CONFIG_FILE}.")

            for name in {"main", "devices"}:
                if name not in config:
                    raise ValueError(f"Invalid {CONFIG_FILE}: missing section {name}.")

            hubitat: Hubitat = None
            if "hubitat" in config:
                hubitat = Hubitat(config["hubitat"])
            else:
                logging.warn(f"Hubitat integration disabled since section is missing in {CONFIG_FILE}.")

            main_conf = config["main"]
            logging.getLogger().setLevel(logging.getLevelName(main_conf["logverbosity"]))
            loop_seconds: int = int(main_conf["wait_seconds"])
            scan_count: int = int(main_conf["scan_count"])

            devices = config["devices"]

            while True:
                report(scan_count, devices, hubitat)

                if loop_seconds <= 0:
                    exit(0)

                sleep(loop_seconds)

    except FileNotFoundError as e:
        logging.error(f"Missing {e.filename}.")
        exit(2)

    except Exception as e:
        logging.exception(e)
        exit(1)


main()
