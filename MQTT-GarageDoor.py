#%%
from email.errors import CloseBoundaryNotFoundDefect
import paho.mqtt.client as mqtt
import RPi.GPIO
import time
from constants import *

RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(GPIO_TRIGGER,RPi.GPIO.OUT)
RPi.GPIO.output(GPIO_TRIGGER,1)
RPi.GPIO.setup(GPIO_DOOROPEN, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(GPIO_DOORCLOSED, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

doorState = DOORSTATE_UNKNOWN # unknown
lastCheck = 0
#%%


client = mqtt.Client(client_id="RPIMQTTGARAGEDOOR")


#%%
def check_door_state(routine=False):
    global doorState
    global client
    global lastCheck
    if (routine):
        if ((time.time() - lastCheck) <= 5):
            print("Too soon - could be just starting an operation")
            return doorState
    lastCheck = time.time()
    if ((RPi.GPIO.input(GPIO_DOOROPEN) != GPIO_INPUT_DEFAULT) and (doorState != DOORSTATE_OPEN)):
        doorState = DOORSTATE_OPEN
    elif ((RPi.GPIO.input(GPIO_DOORCLOSED) != GPIO_INPUT_DEFAULT) and (doorState != DOORSTATE_CLOSED)):
        doorState = DOORSTATE_CLOSED
    elif ((doorState == DOORSTATE_OPEN) and (RPi.GPIO.input(GPIO_DOOROPEN) == GPIO_INPUT_DEFAULT)):
        doorState = DOORSTATE_UNKNOWN
    elif ((doorState == DOORSTATE_CLOSED) and (RPi.GPIO.input(GPIO_DOORCLOSED) == GPIO_INPUT_DEFAULT)):
        doorState = DOORSTATE_UNKNOWN
    else:
        return doorState # Don't publish updates if we don't need to.
    print("Updating")
    client.publish(MQTT_CMD_STATUS, MQTT_STATUS[doorState])
    return doorState
#%%

def on_connect(client, userdata, flags, rc):
    global doorState
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_CMD_TRIGGER)
    client.publish(MQTT_CMD_AVAILABILITY, MQQT_PAYLOAD_AVAILABLE)
    client.publish(MQTT_CMD_STATUS, MQTT_STATUS[check_door_state()])

#%%
def on_message(client, userdata, msg):
    global doorState
    print("Received {}, {}, {}, {}".format(msg.topic, msg.payload, msg.qos, msg.retain))
    if ((msg.payload == MQTT_PAYLOAD_TRIGGERCMD_OPEN) or (msg.payload == MQTT_PAYLOAD_TRIGGERCMD_CLOSE) or (msg.payload == MQTT_PAYLOAD_TRIGGERCMD_STOP)):
        doorState = check_door_state()
        RPi.GPIO.output(6,0)
        time.sleep(0.1)
        RPi.GPIO.output(6,1)
        if (((doorState != DOORSTATE_OPENING) and (doorState != DOORSTATE_CLOSING)) and (msg.payload == MQTT_PAYLOAD_TRIGGERCMD_STOP)):
            doorState = DOORSTATE_UNKNOWN
        elif doorState == DOORSTATE_CLOSED or doorState == DOORSTATE_STOPPED_WHILE_CLOSING:
            doorState = DOORSTATE_OPENING
        elif doorState == DOORSTATE_OPENING:
            doorState = DOORSTATE_STOPPED_WHILE_OPENING
        elif doorState == DOORSTATE_OPEN or doorState == DOORSTATE_STOPPED_WHILE_OPENING:
            doorState = DOORSTATE_CLOSING
        elif doorState == DOORSTATE_CLOSING:
            doorState = DOORSTATE_STOPPED_WHILE_CLOSING
        else:
            print("Unknown?")

    client.publish(MQTT_CMD_STATUS, MQTT_STATUS[doorState])
    print("UPDATED - {} {}".format(doorState,MQTT_STATUS[doorState]))



def on_disconnect(client,userdata,rc):
    time.sleep(60)
    client.reconnect()

#%%

client.on_connect = on_connect
client.on_message = on_message

#%%
client.connect(MQTT_BROKER, MQTT_BROKERPORT, 60)
client.loop_start()

while True:
    # client.publish(MQTT_CMD_AVAILABILITY, MQQT_PAYLOAD_AVAILABLE)
    doorState = check_door_state(True)
    print("{} {}".format(doorState,MQTT_STATUS[doorState]))
    time.sleep(10)
# %%
