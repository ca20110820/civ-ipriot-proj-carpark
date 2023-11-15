from abc import abstractmethod
from typing import Any, Iterable
from functools import wraps
import paho.mqtt.client as paho
import threading
import tkinter as tk
import pprint

from smartpark.utils import quit_listener, create_path_if_not_exists
from smartpark.mqtt_device import MqttDevice
from smartpark.logger import class_logger
from smartpark.project_paths import LOG_DIR, DATA_DIR


def store_message(file_path: str):
    """Store Messages/Data Received from Car Park.

    Decorator for the MQTT on_message() callback.
    """
    def inner(on_message_callback):
        @wraps(on_message_callback)
        def wrapper(self, client: paho.Client, userdata, message):
            msg: str = message.payload.decode()

            # Message: "<available-bays>,<temperature>,<time>,<num-cars>,<num-parked-cars>,<num-un-parked-cars>"
            msg_split = msg.split(";")

            if len(msg_split) > 1:
                data = ",".join(msg_split)

                create_path_if_not_exists(file_path)

                with open(file_path, 'a') as file:
                    file.write(data + "\n")

            return on_message_callback(self, client, userdata, message)
        return wrapper
    return inner


class Display(MqttDevice):
    """Base Class for Displays. It follows the Subscriber pattern.
    """
    def __init__(self, config: dict, display_topic: str, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.display_topic = display_topic  # Display topic from Car Park class

        self.client.subscribe(self.display_topic)
        self.client.on_message = self.on_message

    @abstractmethod
    def start_listening(self, *args, **kwargs):
        """Override and Implement the Event Loop. This method can contain implementation for 'show'"""
        pass

    @abstractmethod
    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        """Override and Implement the Callback as a Subscriber to Car Park"""
        pass


class WindowedDisplay:
    """Displays values for a given set of fields as a simple GUI window. Use .show() to display the window; use
    .update() to update the values displayed.
    """

    DISPLAY_INIT = '– – – – –'
    SEP = ':'  # field name separator

    def __init__(self, title: str, display_fields: Iterable[str]):
        """Creates a Windowed (tkinter) display to replace sense_hat display. To show the display (blocking) call
        .show() on the returned object.

        Parameters
        ----------
        title : str
            The title of the window (usually the name of your carpark from the config)
        display_fields : Iterable
            An iterable (usually a list) of field names for the UI. Updates to values must be presented in a dictionary
            with these values as keys.
        """
        self.window = tk.Tk()
        self.window.title(f'{title}: Parking')
        self.window.geometry('1400x600')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):

            # create the elements
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field+self.SEP, font=('Arial', 50))
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            # position the elements
            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    def show(self):
        """Display the GUI. Blocking call."""
        self.window.mainloop()

    def update(self, updated_values: dict):
        """Update the values displayed in the GUI. Expects a dictionary with keys matching the field names passed to
        the constructor.
        """
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[self.gui_elements[field].cget('text').rstrip(self.SEP)])
        self.window.update()


@class_logger(LOG_DIR / 'display' / 'tk_display' / 'display.log', 'tk_display_logger')
class TkGUIDisplay(Display):
    fields = ['Available Bays',
              'Temperature',
              'Datetime',
              'Number of Cars',
              'Num Parked Cars',
              'Num Un-parked Cars'
              ]  # determines what fields appear in the UI

    def __init__(self, config: dict, display_topic: str, window_title: str = "<Title>"):
        super().__init__(config, display_topic)

        self.window = WindowedDisplay(window_title, TkGUIDisplay.fields)

    def start_listening(self):
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()
        self.logger.info(f"Fired-up Non-blocking thread for {self.__class__.__name__}")

        self.window.show()

    @quit_listener
    @store_message(DATA_DIR / "display_messages.txt")
    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        data = message.payload.decode()

        # ["<available-bays>", "<temperature>", "<time>", "<num-cars>", "<num-parked-cars>", "<num-un-parked-cars>"]
        msg_str = data.split(';')

        self.logger.info(f"Message Received - {msg_str}")

        field_values = dict(zip(TkGUIDisplay.fields, [
            f'{msg_str[0]}',
            f'{float(msg_str[1]):.2f}℃',
            f'{msg_str[2]}',
            f'{msg_str[3]}',
            f'{msg_str[4]}',
            f'{msg_str[5]}'
        ]))

        # When you get an update, refresh the display.
        self.window.update(field_values)


@class_logger(LOG_DIR / 'display' / 'console_display' / 'display.log', 'console_display_logger')
class ConsoleDisplay(Display):
    def __init__(self, config: dict, display_topic: str, *args, **kwargs):
        super().__init__(config, display_topic, *args, **kwargs)

    def start_listening(self):
        self.logger.info(f"Started Listening ...")
        self.client.loop_forever()

    @quit_listener
    @store_message(DATA_DIR / "display_messages.txt")
    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        data = message.payload.decode()  # "<Entry|Exit>,<temperature>"

        # ["<available-bays>", "<temperature>", "<time>", "<num-cars>", "<num-parked-cars>", "<num-un-parked-cars>"]
        msg_str = data.split(';')

        self.logger.info(f"Message Received - {msg_str}")

        print("Available Parking Bays:", msg_str[0])
        print("Temperature:", msg_str[1])
        print("Time:", msg_str[2])
        print("Number of Cars:", msg_str[3])
        print("Number of Parked Cars:", msg_str[4])
        print("Number of Un-Parked Cars:", msg_str[5])
        print("=" * 100)


if __name__ == "__main__":
    from smartpark.config import Config
    from smartpark.project_paths import CONFIG_DIR

    toml_path = CONFIG_DIR / 'sample_smartpark_config.toml'

    car_park_config = Config(toml_path)
    display_config = car_park_config.get_display_configs("carpark1")[0]
    pprint.pprint(display_config)
    display = TkGUIDisplay(display_config,
                           car_park_config.create_car_park_display_topic("carpark1"),
                           car_park_config.get_car_park_config("carpark1")["location"]
                           )

    # display = ConsoleDisplay(display_config, car_park_config.create_car_park_display_topic("carpark1"))

    display.start_listening()
