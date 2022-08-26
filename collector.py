

import re
import subprocess
import logging

# Regex for parsing btmgmt's output
RSSI_REGEX = r' ([0-9A-F:]{17}).*rssi (-?[0-9]+)'


class Collector:
    def __init__(self) -> None:
        self.devices_found: dict[str, int] = {}

    def run(self) -> None:
        result = subprocess.run(['sudo', 'btmgmt', 'find'], stdout=subprocess.PIPE)

        if result.returncode != 0:
            logging.error(f"Unable to run {result.args}.")
            return

        for match in re.findall(RSSI_REGEX, result.stdout.decode('utf-8'), re.MULTILINE):
            rssi: int = int(match[1])
            mac: str = match[0]
            rssi_previous = self.devices_found.get(mac, rssi)
            # for rssi a bigger value (closer to zero) is better
            self.devices_found[mac] = max(rssi, rssi_previous)

    def run_times(self, times: int) -> None:
        for _ in range(times):
            self.run()

    def gather_all(self, extra_runs: int) -> None:
        no_new: int = 0
        while True:
            previous_count = len(self.devices_found)
            self.run()
            new_count = len(self.devices_found)
            if new_count != previous_count:
                logging.info(f"Found {new_count-previous_count} new device(s). Total {new_count} device(s).")
                no_new = 0
            else:
                if no_new == extra_runs:
                    logging.info(f"{new_count} device(s) found total.")
                    return
                logging.info(f"Found no new devices; {extra_runs-no_new} additional run(s) remaining.")
                no_new += 1
