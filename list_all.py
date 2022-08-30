

import argparse
import logging

from collector import Collector

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)


def gather(file: str, extra: int, rssi_print: bool, rssi_min: int) -> None:
    logging.info(f"Collecting BT devices with RSSI value >= {rssi_min} to file {file}.")
    output = open(file, "w")
    collector = Collector()
    collector.gather_all(extra)
    for mac, rssi in sorted(collector.devices_rssi.items()):
        if rssi_print:
            output.write(f"{mac}, {rssi}")
        else:
            output.write(mac)
        output.write("\n")

    output.close()


parser = argparse.ArgumentParser()
parser.description = """
This app will keep scanning for BT devices until it no longer sees any new BT device for the specified number (default: 2) of times.
Note: it may report more MAC addresses than close-by devices due to devices continuously changing their random MAC address.
"""
parser.add_argument("--output", required=False, default="output.txt", type=str, help="name of output file")
parser.add_argument("--scan-extra", required=False, default=1, dest="extra", type=int, help="Number of extra btgmon scans to perform")
parser.add_argument("--print-rssi", required=False, action="store_true", dest="rssi_print", help="Include max RSSI value in the output file")
parser.add_argument("--min-rssi", required=False, default=-90, type=int, dest="rssi_min", help="Min RSSI value. Devices with a lower value are ignored.")
args = parser.parse_args()

gather(args.output, args.extra, args.rssi_print, args.rssi_min)
