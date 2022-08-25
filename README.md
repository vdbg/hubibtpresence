# Hubitat Bluetooth presence detection

This app allows for reporting to Hubitat the proximity of Bluetooth (BT) devices to a specific device (called from here on "the scanner device"), via virtual presence devices in Hubitat.

## Caveats

This is not an exact science. Here's a non-exhaustive list of issues that can impact the reliability:
* Not all BT devices advertise their existence.
* Those that do may not do so continuously (for example, phones may only advertise when in the BT settings).
* Those that do continuously may not be on continuously (for example, may go to sleep to save on battery).
* The strength of the BT signal (RSSI, Received Signal Strength Indicator) is affected by the environment, the device's battery levels, etc.

## Pre-requisites

* A Hubitat hub.
* A linux device on the same LAN as the Hubitat hub that will be performing the scanning.
* The scanner device has a BT adapter. This can be an integrated one or a USB one.
  Note: raspberry 3 and later have an integrated one.
* The `bluetoothctl` and `btmgmt` commands are available on the scanner device. 
  If missing, `apt install bluez` may fix it.

## Setup

### Determining the device(s) mac addresses

These are of the form xx:xx:xx:xx:xx:xx with each x a digit or a letter between A and F. 

The app needs to know what mac addresse(s) to report and what virtual presence devices in Hubitat they map to.
If your location has a large number of BT devices, figuring out these mappings can be hard. 

The easiest option may asking directly the BT device (e.g., going in the phone's settings for a phone)
or the app that manages it.

If that's not possible, here's the manual & hard way to figure these out:

* From the scanner device, run `sudo bluetoothctl`
* From the interactive prompt, type `scan on`
* Note the MAC addresses of the device(s) of interest
  * Sometimes the device manufacturer is nice and provide the name. Older versions of Tile did just that. Newers don't appear to.
  * While the scan is running some devices will appear and disappear. Unfortunately this doesn't mean they go in/out of range. Not all devices reliably advertise.
* Type `scan off` to stop the scan, followed by `exit`

You should end with a list of pairs (mac address, device name).

## Deciding with or without RSSI

The app can treat the device present or absent based on the presence   

## App

sudo btmgmt find

## Background research

Tried multiple approaches, such as using gattlib, [bluescan](https://pypi.org/project/bluescan/) & [pybluez](https://github.com/pybluez/pybluez) packages. The only method that yielded satisfactory results
was using the btmgmt command line application.
Also tried some code [here](https://github.com/dagar/bluetooth-proximity), [here](https://github.com/ewenchou/bluetooth-proximity) and [here](https://github.com/noelportugal/tilefinder)

 

Julie's Lanyard
Greg Bag

[NEW] Device E0:C0:E1:0C:DF:B1 Tile == Sam Wallet????
[NEW] Device CB:29:34:B5:C1:55 Tile
[NEW] Device D5:6E:93:8F:14:19 Tile


sudo apt install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev

Bluescan: promissing?


Javascript. Potentially what I need but very old



running in docker:
https://medium.com/george-adams-iv/using-raspberry-pi-3-s-bluetooth-in-docker-e9cdf6062d6a


https://github.com/geowa4/rpi/blob/master/docker/rpi-blue-python/Dockerfile


This guy worked a shit ton to get the RSSI value!!
https://askubuntu.com/questions/902598/how-do-we-get-rssi-values-from-bluetooth-beacons-estimote-to-be-specific-in-li





gatttool -b E0:C0:E1:0C:DF:B1 -t random --interactive

[DEL] Device CB:29:34:B5:C1:55 Tile
[DEL] Device D5:6E:93:8F:14:19 Tile
[DEL] Device E0:C0:E1:0C:DF:B1 Tile



[NEW] Device CB:29:34:B5:C1:55 Tile
[NEW] Device E0:C0:E1:0C:DF:B1 Tile

[bluetooth]# info D5:6E:93:8F:14:19
Device D5:6E:93:8F:14:19 (random)
        Name: Tile
        Alias: Tile
        Paired: no
        Trusted: no
        Blocked: no
        Connected: no
        LegacyPairing: no
        UUID: Tile, Inc.                (0000feed-0000-1000-8000-00805f9b34fb)
        ServiceData Key: 0000feed-0000-1000-8000-00805f9b34fb
        ServiceData Value:
  02 00 a1 1d a1 17 7f 40 93 a2                    .......@..
        RSSI: -68


[bluetooth]# info E0:C0:E1:0C:DF:B1
Device E0:C0:E1:0C:DF:B1 (random)
        Name: Tile
        Alias: Tile
        Paired: no
        Trusted: no
        Blocked: no
        Connected: no
        LegacyPairing: no
        UUID: Tile, Inc.                (0000feed-0000-1000-8000-00805f9b34fb)
        ServiceData Key: 0000feed-0000-1000-8000-00805f9b34fb
        ServiceData Value:
  02 00 d1 a9 a0 be c4 a2 2c 47                    ........,G
        RSSI: -55

[bluetooth]# info D5:6E:93:8F:14:19
Device D5:6E:93:8F:14:19 (random)
        Name: Tile
        Alias: Tile
        Paired: no
        Trusted: no
        Blocked: no
        Connected: no
        LegacyPairing: no
        UUID: Tile, Inc.                (0000feed-0000-1000-8000-00805f9b34fb)
        ServiceData Key: 0000feed-0000-1000-8000-00805f9b34fb
        ServiceData Value:
  02 00 2e de 97 ec 01 ce 07 c5                    ..........
        RSSI: -70



2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'SamBag' (42c8c607de974372).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'Greg Backpack' (5324c7262da7c1c2).
2022-08-23 16:40:10,134 - root - INFO - Tracking tile 'Milou' (5839811d6d7fb754).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'MilouBig' (5879382075875559).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'Julie's lanyard' (9c7151b967b44c6b).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'SamWallet' (bbbeb9f37ccd4e55).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'Greg Bag' (bc1f34efaa184c11).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'GregS21' (p!44300b88a6a74a8354cadd9fb04f1a74).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'SevenOf9' (p!5c5247a6f1e90446138b411675d4c7ca).
2022-08-23 16:40:10,134 - root - WARNING - Not tracking tile 'David’s iPhone' (p!8cfd90904694762c85d2b6cbefadcae7).
2022-08-23 16:40:10,135 - root - WARNING - Not tracking tile 'iPhone' (p!98b5e498b3cd57245adb5ed155e50e8b).
2022-08-23 16:40:10,135 - root - WARNING - Not tracking tile 'ElevenOf27' (p!ff1bf6560aeb5c809ba5b93e5dc3edb4).


