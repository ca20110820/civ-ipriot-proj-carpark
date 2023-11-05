from functools import wraps
import os

import paho.mqtt.client as paho
from smartpark.mqtt_device import MqttDevice


def quit_listener(on_message_callback):

    def wrapper(self, client: paho.Client, userdata, message):

        if not hasattr(self, "quit_topic"):
            assert isinstance(self, MqttDevice), "Cannot use this decorator on a non-MqttDevice"
            setattr(self, "quit_topic", "quit")
            self.client.subscribe("quit")

        msg = message.payload.decode()

        if msg in ["quit", "Q", "q"]:
            client.disconnect()
            client.loop_stop()

            if hasattr(self, "window"):  # For TkGUIDisplay
                try:
                    self.window.window.destroy()
                except Exception as e:
                    print(e)

            exit()

        on_message_callback(self, client, userdata, message)
    return wrapper


def store_message(file_path: str = os.path.join(os.path.dirname(__file__), "display_messages.txt")):
    def inner(on_message_callback):
        @wraps(on_message_callback)
        def wrapper(self, client: paho.Client, userdata, message):
            msg: str = message.payload.decode()

            # Message: "<available-bays>,<temperature>,<time>,<num-cars>,<num-parked-cars>,<num-un-parked-cars>"
            msg_split = msg.split(";")

            if len(msg_split) > 1:
                data = ",".join(msg_split)  # Could have standardized to comma but it's fine
                with open(file_path, 'a') as file:
                    file.write(data + "\n")

            return on_message_callback(self, client, userdata, message)
        return wrapper
    return inner
