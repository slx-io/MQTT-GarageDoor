import paho.mqtt.client as mqtt
import RPi.GPIO
import time


RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(6,RPi.GPIO.OUT)
RPi.GPIO.output(6,1)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("homeassistant/cover/garagedoor/set")
    client.publish("homeassistant/cover/garagedoor/available","online")
    client.publish("homeassistant/cover/garagedoor",check_state())

def on_message(client, userdata, msg):
    print("Received {}, {}, {}, {}".format(msg.topic, msg.payload, msg.qos, msg.retain))
    if (msg.payload == b'TRIGGER'):
        doorState = check_state()
        if ((doorState == b'CLOSED') or (doorSTate == b'CLOSING')):
            client.publish("homeassistant/cover/garagedoor", b'OPENING')
        else:
            client.publish("homeassistant/cover/garagedoor", b'CLOSING')
        print("Turn On")
        RPi.GPIO.output(6,0)
        time.sleep(0.1)
        RPi.GPIO.output(6,1)
        # client.publish("homeassistant/cover/garagedoor", b'ON')
        # print("Back to Off")

    elif (msg.payload == b'OFF'):
        print("Turn Off")
        client.publish("homeassistant/cover/garagedoor", b'OFF')
        RPi.GPIO.output(6,1)
    else:
        print(msg)

def on_disconnect(client,useerdata,rc):
    time.sleep(60)
    client.reconnect()

client = mqtt.Client()
client.connect("172.28.0.129",1883,60)

client.on_connect = on_connect
client.on_message = on_message

def check_state():
        return b"CLOSED"

while True:
    client.loop(1.0)
    print("Poll here for status")