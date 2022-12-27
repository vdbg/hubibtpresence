

import re
import subprocess
import logging

# Regex for parsing btmgmt's output
RSSI_REGEX = r' ([0-9A-F:]{17}).* rssi (-?[0-9]+)'


class Collector:
    def __init__(self) -> None:
        self.devices_rssi: dict[str, int] = {}

    def run(self) -> None:
        # Piping 'hello' to stdin because otherwise btmgmt will silently fail in docker containers
        # https://www.spinics.net/lists/linux-bluetooth/msg85222.html
        result = subprocess.run(['sudo', 'btmgmt', 'find'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, input='hello', text=True)

        if result.returncode != 0:
            logging.error(f"Unable to run {result.args}; failed with error code {result.returncode}.")
            return

        devices_found: int = 0

        for match in re.findall(RSSI_REGEX, result.stdout, re.MULTILINE):
            devices_found += 1
            rssi: int = int(match[1])
            mac: str = match[0]
            rssi_previous = self.devices_rssi.get(mac, rssi)
            # for rssi a bigger value (closer to zero) is better
            self.devices_rssi[mac] = max(rssi, rssi_previous)

        if not devices_found:
            logging.warning(f"No devices found. Output: {result.stdout}")
        else:
            logging.debug(f"Found {devices_found} device(s).")

    def gather_all(self, extra_runs: int) -> None:
        no_new: int = 0
        while True:
            previous_count = len(self.devices_rssi)
            self.run()
            new_count = len(self.devices_rssi)
            if new_count != previous_count:
                logging.info(f"Found {new_count-previous_count} new device(s). Total {new_count} device(s).")
                no_new = 0
            else:
                if no_new == extra_runs:
                    logging.info(f"{new_count} device(s) found total.")
                    return
                logging.info(f"Found no new devices; {extra_runs-no_new} additional run(s) remaining.")
                no_new += 1
