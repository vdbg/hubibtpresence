# Hubitat Bluetooth presence detection

This app allows for reporting to Hubitat the proximity of Bluetooth devices (called from here on "BT device(s)") to a specific device (called from here on "the BT scanner"), via virtual presence devices in Hubitat.

## Caveats

This is not an exact science. Here's a non-exhaustive list of issues that can impact the scanner's reliability:
* Not all BT devices advertise their existence.
* Those that do may not do so continuously (for example, phones may only advertise when in the BT settings).
* Devices may not be on all the time, or when on may regularly turn off their BT component to conserve power.
* The strength of the BT signal (RSSI, Received Signal Strength Indicator) is affected by the environment (walls, other devices), the device's battery levels, etc.
* Some BT devices constantly randomize their MAC address for privacy reasons. If the BT device is not paired with the scanner device, the BT scanner may only get random non-static (constantly changes) MAC addresses from the BT device, which prevents from identifying/tracking the device.
* Some BT devices will stop advertising their presence when accessed. For example, Tile trackers will stop advertising their presence if the Tile app is opened on a nearby phone (this is also why only one phone can "Find" a given Tile at any given time).

## Pre-requisites

* A Hubitat hub.
* A linux device on the same LAN as the Hubitat hub that will be performing the scanning.
* The BT scanner has a BT adapter. This can be an integrated one or a USB one.
  Note: raspberry 3 and later have an integrated BT adapter.
* The `bluetoothctl` and `btmgmt` commands are available on the scanner device. 
  If missing, `apt install bluez` may fix it.

## Finding the mac address(es)

The BT scanner needs to know what mac address(es) to monitor and what virtual presence devices in Hubitat they map to.
MAC adresses are of the form xx:xx:xx:xx:xx:xx with each x a letter between A and F or a digit. 

Your task is to end with a list of pairs (mac address, device name).

### List all devices with stable MAC addresses

The BT scanner can only track devices with stable mac addresses. To determine these:
* From the BT scanner, run: `python3 list_all --output first.txt`
* Wait 15 minutes
* Run: `python3 list_all --output second.txt`
* Run: `comm -1 -2 before.txt after.txt`

The resulting list is all BT mac addresses that were seen in both scanning sessions, meaning devices that are more likely not to randomize their mac or to stop to advertise their presence.

### The easiest way

The easiest option is to ask directly the BT device (for example in the case of a phone, by going in the phone's settings, about section) or the app that manages it.

If this address is not in the previous list, you may need to do one of these:
* Turn on BT on the BT device
* Disable MAC randomization on the BT device: a [privacy feature](https://www.bluetooth.com/blog/bluetooth-technology-protecting-your-privacy/) meant to prevent tracking, which is what we're trying to do here
* Explicitly pair the BT device with the BT scanner. The process for pairing a device to a raspberry pi is explained [here](https://pimylifeup.com/raspberry-pi-bluetooth).


### Harder ways

If that's not possible, here's a manual way to figure the mac adresses that may be of interest:

* From the BT scanner, run: `sudo stdbuf -oL hcitool lescan`
* `Ctrl-C` to stop the scan.

Or, for a more interactive way:
* From the BT scanner, run :`sudo bluetoothctl`
* From the interactive prompt: `scan on`
* type `info xx:xx:xx:xx:xx:xx` for a given mac address that showed up. Sometimes the Name, Alias or UUID will provide a clue as to what device it corresponds to.
* Type `scan off` to stop the scan, followed by `exit`

Note: while the scan is running some devices will appear and disappear. Unfortunately this doesn't mean they go in/out of range. Not all devices constantly advertise and constantly keep the same MAC address.

### The hardest ways

Another approach is running `sudo btmgmt find | grep rssi | cut -d ' ' -f 3 | sort` once with the BT device on/near and once with the device off or away and comparing results. This can be hard when there are many BT devices with random MAC addresses in the vicinity.

## Deciding to integeate with or without RSSI

RSSI is a measure of the strength of the signal between the BT scanner and the BT device.
RSSI values are negative. The closer the value is to 0, the stronger the signal is and the closer the BT device is from the BT scanner. Below is an estimate of the relationship RSSI to distance. 

|RSSI value |Probable distance     |
|-----------|----------------------|
| >=-55     |Very close, few meters|
|-55 to -67 |Same room             |
|-67 to -80 |Same house            |
|-80 to -90 |Neighbors             |
| <= -90    |Even further          |

Note: RSSI is not only affected by distance, but also by the environment (presence and type of walls, interferences, ...) and by the characteristics of the BT device (battery level, type of antenna, ...).

The app can treat the device present or absent based on the RSSI value.
This can be useful to differentiate BT device in the same room as BT scanner vs. in the same house vs. no-where near the BT scanner.   

