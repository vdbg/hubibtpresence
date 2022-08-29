from pathlib import Path
import logging
import yaml

from collector import Collector

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def report(runs: int, devices: dict) -> None:
    logging.info(f"Running bluetooth management {runs} time(s)...")

    collector = Collector()
    collector.run_times(runs)

    devices_found = collector.devices_found

    if logging.root.isEnabledFor(logging.DEBUG):
        for mac, rssi in sorted(devices_found.items()):
            logging.debug(f"{mac}:{rssi}")

    for device, data in devices.items():
        name = device
        if data and "name" in data:
            name = name + " (" + data["name"] + ")"
        if device.upper() in devices_found:
            logging.info(f"Device {name} is PRESENT; RSSI={devices_found[device]}.")
        else:
            logging.info(f"Device {name} is ABSENT.")


def main() -> None:
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

            report(3, devices)

    except FileNotFoundError as e:
        logging.error("Missing config.yaml file.")
        exit(2)

    except Exception as e:
        logging.exception(e)
        exit(1)


main()
