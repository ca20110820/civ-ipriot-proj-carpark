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
