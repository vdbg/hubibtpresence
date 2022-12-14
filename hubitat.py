import logging

# https://github.com/danielorf/pyhubitat
from pyhubitat import MakerAPI


class Device:
    def __init__(self, conf: dict) -> None:
        self.name: str = f"'{conf['label']}' ({conf['id']})"
        attributes = conf.get("attributes", dict())
        self.presence = attributes.get('presence', None)


class Hubitat:
    def __init__(self, conf: dict):
        hub = f"{conf['url'].rstrip('/')}/apps/api/{conf['appid']}"
        logging.info(f"Connecting to hubitat Maker API app {hub}")
        self._api = MakerAPI(conf["token"], hub)
        self._devices_cache: dict[int, Device] = None

    def get_all_devices(self) -> dict[int, Device]:
        if self._devices_cache is None:
            logging.debug("Refreshing all devices cache")
            self._devices_cache = {int(x["id"]): Device(x) for x in self._api.list_devices_detailed() if x["type"] == "Virtual Presence"}
            for device in self._devices_cache.values():
                logging.debug(f"Found Hubitat virtual presence device {device.name}.")

        return self._devices_cache

    def set_presence(self, id: int, arrived: bool) -> None:
        command: str = 'arrived' if arrived else 'departed'
        state: str = 'present' if arrived else 'not present'
        device: Device = self.get_all_devices().get(id, None)
        if not device:
            logging.warn(f"Device {id} not found in Hubitat.")
            return
        if state == device.presence:
            logging.info(f"Presence for {device.name} hasn't changed.")
            return
        logging.info(f"Sending command {command} to Hubitat device {device.name} that was previously {device.presence}")
        self._api.send_command(id, command)
        device.presence = state
