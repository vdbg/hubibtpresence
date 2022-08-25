from pathlib import Path
import re
import logging
import subprocess
import time
import yaml


# Regex for parsing btmgmt's output
RSSI_REGEX = r' ([0-9A-F:]{17}).*rssi (-?[0-9]+)'

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# TODO: upper mac addresses everywhere


def main(runs: int, devices: dict) -> None:
    logging.info(f"Running bluetooth management {runs} time(s)...")

    devices_found: dict[str, int] = {}

    for _ in range(runs):
        result = subprocess.run(['sudo', 'btmgmt', 'find'], stdout=subprocess.PIPE)

        if result.returncode != 0:
            logging.error(f"Unable to run {result.args}.")
            continue

        for match in re.findall(RSSI_REGEX, result.stdout.decode('utf-8'), re.MULTILINE):
            rssi: int = int(match[1])
            mac: str = match[0]
            rssi_previous = devices_found.get(mac, rssi)
            # for rssi a bigger value (closer to zero) is better
            devices_found[mac] = max(rssi, rssi_previous)

        if logging.root.isEnabledFor(logging.DEBUG):
            for mac, rssi in sorted(devices_found.items()):
                logging.debug(f"{mac}:{rssi}")

    for device, data in devices.items():
        name = device
        if data and "name" in data:
            name = name + " (" + data["name"] + ")"
        if device in devices_found:
            logging.info(f"Device {name} is present with RSSI value {devices_found[device]}")
        else:
            logging.info(f"Device {name} is not present")


try:
    with open(Path(__file__).with_name("config.yaml")) as config_file:

        config = yaml.safe_load(config_file)

        if not config:
            raise ValueError("Invalid config.yaml. See template.config.yaml.")

        for name in {"main", "devices", "hubitat"}:
            if name not in config:
                raise ValueError(f"Invalid config.yaml: missing section {name}.")

        main_conf = config["main"]
        logging.getLogger().setLevel(logging.getLevelName(main_conf["logverbosity"]))
        loop_seconds: int = int(main_conf["wait_seconds"])

        devices = config["devices"]

        main(3, devices)


except FileNotFoundError as e:
    logging.error("Missing config.yaml file.")
    exit(2)

except Exception as e:
    logging.exception(e)
    exit(1)
