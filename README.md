# Hubitat Bluetooth presence detection

This app allows for reporting to Hubitat the proximity of Bluetooth devices (called from here on "BT device(s)") to a specific device (called from here on "the BT scanner"), via virtual presence devices in Hubitat.

This app has been successfully tested on Tile Pro and Tile Mate trackers.

## Caveats

BT tracking is not an exact science. Here's a non-exhaustive list of issues that can impact the scanner's reliability:
* Not all BT devices advertise their existence.
* Those that do may not do so continuously (for example, phones may only advertise when in the BT settings).
* Devices may not be on all the time, or when on may regularly turn off their BT stack to conserve power.
* The strength of the BT signal (RSSI, Received Signal Strength Indicator) is affected by the environment (walls, other devices), the device's battery levels, etc.
* Some BT devices constantly randomize their MAC address for privacy reasons. If the BT device is not paired with the scanner device, the BT scanner may only see constantly changing MAC addresses from the BT device, which prevents from identifying/tracking the device.
* Some BT devices will stop advertising their presence when accessed. For example, Tile trackers will stop advertising their presence if the Tile app is opened on a nearby phone (this is also why only one phone can "Find" a given Tile at any given time).

## Pre-requisites

* A Hubitat hub.
* A device (the BT scanner) on the same LAN as the Hubitat hub that will be performing the scanning.
* The BT scanner has a BT adapter. This can be an integrated one or a USB one.
  Note: raspberry 3 and later have an integrated BT adapter.
* Linux installed on the BT scanner: while Python is cross platform, this app depends on the `btmgmt` utility that is only available on Linux.
* The `bluetoothctl` and `btmgmt` commands are installed on the BT scanner. If missing, `apt install bluez` may fix it.
* Python 3.9+ and pip3 installed on the BT scanner. Run `sudo apt-get install python3-pip` if missing.
* Passwordless `sudo` permissions for the account running the app (a `btmgmt` requirement).
* Note: app can run in a [Docker](https://www.docker.com/) container on the BT scanner (instructions below). It is however recommended to do initial setup directly on the host.

## Running the tool directly on the BT scanner

It is recommended to first run the tool directly on the BT scanner for troubleshooting and tuning:

* `git clone https://github.com/vdbg/hubibtpresence.git`
* `cd hubibtpresence`
* `pip3 install -r requirements.txt`
* `cp template.config.yaml config.yaml`
* Edit `config.yaml`. **See instructions below on how to find the MAC addresses**
* Run as interactive mode: `python3 main.py`
  `Ctrl-C` to stop.
* Run as background process: `python3 main.py > log.txt 2>&1 &`
  `kill` to stop.

## Finding the MAC address(es)

The BT scanner needs to know what MAC address(es) to monitor and what virtual presence devices in Hubitat they map to.
MAC adresses are of the form xx:xx:xx:xx:xx:xx with each x a letter between A and F or a digit. 

Your task is to end with a list of pairs (MAC address, device name).

### List all devices with stable MAC addresses

The BT scanner can only track devices with stable MAC addresses. To determine these, run the following with the BT device to monitor turned on and close to the BT scanner (same room):
* `sudo btmgmt scan`
  * If this ask for a password, make sure the current account can do [passwordless sudo](https://www.simplified.guide/linux/enable-passwordless-sudo) as the app relies on this
  * If this fails for other reasons, fix as appropriate (install package, ensure BT adapter is present, etc.)
  * If this does not return any MAC addresses, the BT scanner is not able to see any BT devices
* `git clone https://github.com/vdbg/hubibtpresence.git`
* `cd hubibtpresence`
* `pip3 install -r requirements.txt`
* `python3 list_all --output first.txt`
* Wait 15 minutes
* `python3 list_all --output second.txt`
* `comm -1 -2 first.txt second.txt > stable.txt`

The file `stable.txt` contains all BT MAC addresses that were seen in both scanning sessions, meaning devices that are more likely not to constantly randomize their MAC or to stop to advertise their presence.

### The easiest way

The easiest option is to ask directly the BT device (for example in the case of a phone, by going in the phone's settings, about section) or the app that manages it.

If the BT device MAC address is not in the previous list, you may need to do one of these:
* Turn on BT on the BT device
* Disable MAC randomization on the BT device: it is a [privacy feature](https://www.bluetooth.com/blog/bluetooth-technology-protecting-your-privacy/) meant to prevent tracking, which is what we're trying to do here
* Explicitly pair the BT device with the BT scanner. The process for pairing a device to a raspberry pi is explained [here](https://pimylifeup.com/raspberry-pi-bluetooth).


### Harder ways

If you could not figure out the MAC address the easy way, here's another option:

* From the BT scanner, run :`sudo bluetoothctl`
* From the interactive prompt: `scan on`
* type `info xx:xx:xx:xx:xx:xx` for a MAC address from the list of stable MAC addresses. Sometimes the Name, Alias or UUID will provide a clue as to what device it corresponds to.
* Type `scan off` to stop the scan, followed by `exit`

Alternatively, if there are very few devices, `sudo stdbuf -oL hcitool lescan` may be sufficient (`Ctrl-C` to stop the scan).

Notes:
* while the scan is running some devices will appear and disappear. Unfortunately this doesn't mean they go in/out of range. Not all devices constantly advertise and constantly keep the same MAC address.
* some of the tools label the MAC addresses as Public or Random. Random does not necesarily mean the address cannot be used as some devices choose a random MAC address *once* in their lifetime, meaning the random address is stable. 

### The hardest ways

Another approach is running `sudo btmgmt find | grep rssi | cut -d ' ' -f 3 | sort` once with the BT device on/near and once with the device off or away and comparing results. This can be hard when there are many BT devices with constantly changing MAC addresses in the vicinity.

## Deciding to gate presence on RSSI

RSSI is a measure of the strength of the signal between the BT scanner and the BT device.
RSSI values are negative. The closer the value is to 0, the stronger the signal is and the closer the BT device is from the BT scanner. Below is an estimate of the relationship between RSSI and distance. 

|RSSI value |Probable distance     |
|-----------|----------------------|
| >=-55     |Very close, few meters|
|-55 to -67 |Same room             |
|-67 to -80 |Adjacent room         |
|-80 to -90 |Few rooms away        |
| <= -90    |Neighbors' house      |

Note: RSSI is not only affected by distance, but also by the environment (presence and type of walls, interferences, ...) and by the characteristics of the BT device (battery level, type of antenna, ...).

The app can optionally treat the device present or absent based on the RSSI value, when the `minRSSI` value is provided in `config.yaml`.    

## Running in a Docker container

It is recommended to test/tune the scanner before moving to containers. Once testing is completed:


```
sudo docker run -d \
  --name hubibtpresence \
  --restart always \
  --memory=100m \
  -v path_to_your/config.yaml:/app/config.yaml \
  --privileged --net=host \
  vdbg/hubibtpresence:latest
```

With:
* `path_to_your/config.yaml`: the full path to the properly configured config.yaml
* `vdbg/hubibtpresence:latest` replace with your image name if you built the image locally, otherwise leave as is
* `--privileged --net=host`: required options for the app to be able to access the BT scanner's BT adapter from the container

Note: when the app within the container is performing its scans (every 3 minutes by default), the host won't be able to use BT anymore. For example `sudo btmgmt find` on the host will return `Unable to start discovery. status 0x0a (Busy)` during this time.
