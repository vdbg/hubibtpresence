from pathlib import Path
import argparse
import logging
import yaml

from collector import Collector

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def main(runs: int, devices: dict) -> None:
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
            logging.info(f"Device {name} is present with RSSI value {devices_found[device]}")
        else:
            logging.info(f"Device {name} is not present")


def report() -> None:
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


def gather(file: str, count: int) -> None:
    logging.info(f"Collecting BT devices in range to file {file}")
    output = open(file, "w")
    collector = Collector()
    collector.gather_all(count)
    for mac, rssi in sorted(collector.devices_found.items()):
        output.write(mac)
        output.write("\n")

    output.close()


parser = argparse.ArgumentParser()
parser.add_argument("--action", choices=("report", "gather"), dest="action", default="report", help="report: report state of devices Hubitat; gather: find all BT devices")
parser.add_argument("--output", required=False, default="output.txt", type=str, help="name of output file when action is gather")
parser.add_argument("--btmgmt-count", required=False, default=5, dest="count", type=int, help="Number of additional btgmon calls to perform when action is gather")
parser.add_argument("--print-rssi", required=False, action="store_true", dest="rssi", help="Include max RSSI values in the output file")
args = parser.parse_args()

if args.action == "report":
    report()
if args.action == "gather":
    gather(args.output, args.count)
