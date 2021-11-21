# Home Assistant Control of Garage Door via MQTT
I want to control my Garage Door using a relay module and Raspberry Pi.

I found Remote GPIO to be overly simplistic and problematic. I found that the relay would trigger when Home Assistant would first connect to the Raspberry Pi (thus opening the door - not desirable), plus it wouldn't handle disconnections/reconnections at all.

This is a very simple script (currently in prototype) to control a garage door using a Raspberry Pi, communicating with Home Assistant via MQTT.

## Parts
1. Raspberry Pi, running Python 3.7
2. A 5V Relay Module (Such as https://www.ebay.com.au/itm/303882904351?hash=item46c0d5231f:g:O~gAAOSwaZhgJbuf&frcectupt=true)
3. Two reed switches to detect when door open and closed (Such as https://www.jaycar.com.au/security-alarm-reed-switch/p/LA5072)

## Connection
GPIO Connection is configurable in [constants.py](constants.py). I used the following pins because the default pullup/pulldown resistors suited my configuration.

The relay board I have is "default high" which means I need to basically put "0" out to turn the relay on, and "1" to turn it off. That's configurable too.

1. Relay VCC to [5V Power on Raspberry Pi](https://pinout.xyz/pinout/5v_power)
2. Relay Ground to [Ground on Raspberry Pi](https://pinout.xyz/pinout/ground)
3. Relay IN to [GPIO 6 on Raspberry Pi](https://pinout.xyz/pinout/pin31_gpio6)
4. One wire to Reed Switch (Door Open) to [GPIO 23 on Raspberry Pi](https://pinout.xyz/pinout/pin18_gpio23)
5. One wire to Reed Switch (Door Open) to [Ground on Raspberry Pi](https://pinout.xyz/pinout/ground)
6. One wire to Reed Switch (Door Closed) to [GPIO 24 on Raspberry Pi](https://pinout.xyz/pinout/pin18_gpio24)
7. One wire to Reed Switch (Door Closed) to [Ground on Raspberry Pi](https://pinout.xyz/pinout/ground)

## Connection to Garage Door
Most garage doors will have a terminal block for a physical switch. You'll have to find this part out yourself.

Connect the normally open and common contacts of the relay to the switch. 

The script will turn the relay on and then almost immediately turn it off, simulating a button press.

## Home Assistant Configuration
You need the MQTT broker installed. Install and configure the add-on.

Add the Garage Door to your configuration.yaml:
```yaml
cover:
  - platform: mqtt
    name: "Garage Door"
    availability:
      - topic: "homeassistant/cover/garagedoor/available"
    payload_available: "online"
    payload_not_available: "offline"
    state_topic: "homeassistant/cover/garagedoor"
    command_topic: "homeassistant/cover/garagedoor/set"
    payload_open: "OPEN"
    payload_close: "CLOSE"
    payload_stop: "STOP"
    state_open: "OPEN"
    state_closed: "CLOSED"
    state_opening: "OPENING"
    state_closing: "CLOSING"
    state_stopped: "STOPPED"
    optimistic: false
    retain: true
```
