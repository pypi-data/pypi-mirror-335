# Drayton Wiser Hub API Async v1.6.6

This repository contains a simple API which queries the Drayton Wiser Heating sysystem used in the UK.

The API functionality provides the following functionality to control the wiser heating system for 1,2 and 3 channel heat hubs
The API also supports Smart Plugs and initial basic functionality for Shutter and Lights

## Requirements

Requires a minimum of Python v3.10

## Installation

## 1. Find your HeatHub Secret key

Reference [https://it.knightnet.org.uk/kb/nr-qa/drayton-wiser-heating-control/#controlling-the-system](https://it.knightnet.org.uk/kb/nr-qa/drayton-wiser-heating-control/#controlling-the-system)

1. Press the setup button on your HeatHub, the light will start flashing
Look for the Wi-Fi network (SSID) called **‘WiserHeatXXXXXX’** where XXXXXX is last 6 digits of the MAC address
2. Connect to the network from a Windows/Linux/Mac/Android/iPhone machine
3. Execute the secret url :-)
   * Open a browser to url `http://192.168.8.1/secret`

   This will return a string which is your system secret, store this somewhere. If you are running the test script simply put this value , with the ip address of the hub, in your wiserkeys.params

4. Press the setup button on the HeatHub again and it will go back to normal operations
5. Copy the secret and save it somewhere.

## 3. Find Your HEATHUB IP

Using your router, or something else, identify the IP address of your HeatHub, it usually identifies itself as the same ID as the ``WiserHeatXXXXXX``

Alternatively see the test_api_discovery.py file for how to use the api to discover your hub

## 4. Add values in you params.py to run tests

Create a file called params.py and place two lines, one with the wiser IP or hostname and the other with the secret key.
e.g.

```code
HOST="192.168.0.22"
KEY="ABCDCDCDCCCDCDC"
```

## 5. Run the sample

To help understand the api simply look at the test sample code ```tests/test_api_properties.py```, ```tests/test_api_methods.py``` or ```tests/test_api_discovery.py``` and the fully commented code.

## 6. Documentation

Documentation available in [info.md](https://github.com/msp1974/wiserHeatAPIv2/blob/master/docs/info.md) in the docs directory and within comments in the code

## Changelog

### v1.6.6
* Added: support SSL redirect on hub for future firmware

### v1.6.5
* Fix: improve status handling of hot water for hw climate mode

### v1.6.4
* Fix: fix issue of default extra config values not being provided

### v1.6.3
* Fix: fix error in temp validator from websocket schedule data that errored if a slot was set to off

### v1.6.2
* Refactor: Removed unused imports causing error in python3.13
* Fix: Add equipment data during deviuce build process

### v1.6.1
* Added: support for temperature and humidity sensors

### v1.6.0
* Refactored how devices are enumerated
* BREAKING CHANGE - threshold sensor is now a device attribute and not its own device
* Added: support for 2 gang light switches
* Added: support for threshold and UI configuration as device attributes
* Added: support for PTC devices
* Added: UUID now exists for all devices (for future use)
* Added: New attributes and stored extra config for Hot Water to support HW Climate automation in HA integration
* Added: Control of interacts with room climate for binary sensors

### v1.5.19
* Fixed error when BoilerInterface does not provide DeviceId field
* Fixed not supporting non ascii characters in schedule names
* Added ButtonPanel device support

### v1.5.18

* Better handle client response exeption and fit into retry routing

### v1.5.17

* Fixed error setting opentherm endpoint for fw above 4.32.46
* Added support for CFMT devices

### v1.5.16

* Added support for v2 opentherm endpoint for fw above 4.32.46

### v1.5.15

* Added additonal functions for v2 hub lights, equipments etc
* Added support for WindowDoor sensors
* Added support for Boiler Interface device

### v1.5.14

* Fix presets not using defined boost temp
* Set return value of energy sensors to None if not provided by hub
* Updated headers for hub query

### v1.5.13

* Updates to support v2 hub functions - @LGO44
* Add connection timeout to new retry function
* Increase http timeout from 10s to 20s

### v1.5.12

* Improve performance of hub read and retries
* Fix error is no status endpoint

### v1.5.11

* Improve error management
* Add additional debug logging

### v1.5.10

* Add retry routine to prevent hub response errors

### v1.5.9

* Force schedules endpoint to use http/1.0

### v1.5.8

* Handle chunked encoding if sent by the hub

### v1.5.7

* Fixed issue whereby lower target temp for passive mode was not being set correctly
* Added support for smoke alarm

### v1.5.6

* Added improved error handling for json decode errors

### v1.5.5

* Added addtional v2 hub attributes and switches

### v1.5.4

* Fixed issue whereby json conversion errors due to control characters in string

### v1.5.2

* Revert to aiohttp and fix errors with v3.9.x that caused move to httpx

### v1.5.1

* Fix nuances with httpx

### v1.5.0

* Move to httpx instead of aiohttp

### v1.4.0

* Add PowerTagE support
* Add new v2 hub cloud parameters
* Add new v2 hub capabilities info
* Add v2 hub equipment data to relevant devices
* Add tilt support for shutters
* Fix issue where non ASCII chars removed

### v1.3.9

* Fix for hub firmware bug whereby Away Mode Affects HotWater is turned off when cancelling overrides if no overrides exist.

### v1.3.8

* Correct relative modulation level opentherm parameter magnitude

### v1.3.7

* Amend battery to return None for voltage and percent if battery data not present

### 1.3.6

* Add new status class
* Fix error if passive mode room device offline

### v1.3.5

* Correct async error in extra_config

### v1.3.4

* Current temperature now returns none for room if TRV signal lost.

### v1.3.3

* Fixed issue in passive mode so that it works with 3 channel hub and different rooms on different channels

### v1.3.2

* Fixed issue ot maintaining some parameters after hub update
* Improved handling of extra config json errors
* Amended current_target_temp to use DisplayedSetPoint instead of CurrentSetPoint as this displays incorrectly in Eco mode

### 1.3.1

* Away mode overrides passive mode functions

### 1.3.0

* Rework passive mode functionality (may break previous code if using passive mode)

### 1.2.2

* Improve logic defining is_passive_mode property

### 1.2.1

* Code refactoring
* Added is_passive_mode property
* Corrected bug in passive mode automation to determine target temp

### 1.2.0

* Breaking Change - changes to passive mode from on or off to disabled, passive manual and passive follow schedule
* Support boost in passive mode
* Add additional opentherm parameters
* Fix not clearing overrides when enabling passive mode

### 1.1.1

* Fix issue setting on/off schedule - issue #349

### 1.1.0

* Added room passive mode automation control

### 1.0.2

* Fixed error in boost_all_rooms using old temp validation type (no longer supported)
* Fixed error in validating temps from yaml file

### 1.0.1

* Added endpoint parameter to set_opentherm_parameter

### 1.0.0

* Moved to stable build version
* Amended timeout error text
* Improved error handling for setting schedules
* Added temp sensor support for heating actuator
* Added support for network diagnostics
* Added support for non standard port
* Add boiler parameters to opentherm
* Support setting opentherm parameters

### 0.1.8

* Add url to exception messages
* Fix for unicode decode error

### 0.1.7

* Fixed error intiallising WiserUFHController class
* Made python3.9 compatible

### 0.1.6

* Remove debuggin print lines
* Remove session close on endpoint error

### 0.1.5

* Add ALL as special day option in schedule file for setting schedules from file

### 0.1.4

* Fix incorrect id used for schedule assignment in electrical devices

### 0.1.3

* Fixed issue in schedule.get_by_name

### 0.1.2

* Fixed calling wrong enpoint id for lights and shutters

### 0.1.0

* Initial asyncio release
