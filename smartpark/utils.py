import paho.mqtt.client as paho
from smartpark.mqtt_device import MqttDevice


def quit_listener(on_message_callback):
    # This wouldn't work if the on_message is fired-up in the background

    def on_disconnect(client, userdata, reason_code, properties):
        exit()

    def wrapper(self, client: paho.Client, userdata, message):
        nonlocal on_disconnect

        if not hasattr(self, "quit_topic"):
            assert isinstance(self, MqttDevice), "Cannot use this decorator on a non-subscriber"
            setattr(self, "quit_topic", "quit")
            self.client.subscribe("quit")

        if client.on_disconnect is None:
            client.on_disconnect = on_disconnect

        msg = message.payload.decode()

        if msg in ["quit", "Q", "q"]:
            client.disconnect()
            client.loop_stop()
            exit()

        on_message_callback(self, client, userdata, message)
    return wrapper
