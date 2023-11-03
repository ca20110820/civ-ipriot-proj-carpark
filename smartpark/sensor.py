""""Demonstrates a simple implementation of an 'event' listener that triggers
a publication via mqtt"""
from abc import ABC, abstractmethod
import tkinter as tk
import random


from smartpark.mqtt_device import MqttDevice


class Sensor(MqttDevice):
    # For this simulation, we will instantiate entering cars in the Car Park
    @property
    def temperature(self):
        """Returns the current temperature"""
        # Can get from random number generator, file, or API.
        raise NotImplementedError()

    def on_detection(self, message: str):
        """Publish to CarPark"""
        self.client.publish(self.topic_address, message)


class EntrySensor(Sensor):
    @property
    def temperature(self):
        return random.randint(20, 30)

    def on_car_entry(self):
        self.on_detection(f"Enter,{self.temperature}")


class ExitSensor(Sensor):
    @property
    def temperature(self):
        return random.randint(20, 30)

    def on_car_exit(self):
        self.on_detection(f"Exit,{self.temperature}")


class Detector(ABC):

    QUIT_FLAG = False

    @abstractmethod
    def start_sensing(self):
        """Define Event Loop"""
        pass


class CLIDetector(Detector):
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict):
        self.entry_sensor = EntrySensor(entry_sensor_config)
        self.exit_sensor = ExitSensor(exit_sensor_config)

    def start_sensing(self):
        while not self.QUIT_FLAG:
            user_input = input("E or X >>> ")

            if user_input in ["E", "e", "enter"]:
                self.entry_sensor.on_car_entry()
            elif user_input in ["X", "x", "exit"]:
                self.exit_sensor.on_car_exit()
            elif user_input in ["q", "Q", "quit"]:
                self.QUIT_FLAG = True
            else:
                print("Invalid Input!\n")
                continue


class TkDetector(Detector):
    def __init__(self, entry_sensor_config, exit_sensor_config):
        self.entry_sensor = EntrySensor(entry_sensor_config)
        self.exit_sensor = ExitSensor(exit_sensor_config)

        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side', command=self._car_entered)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘', font=('Arial', 50), cursor='bottom_left_corner',
            command=self._car_exited)
        self.btn_outgoing_car.pack(padx=10, pady=5)

    def start_sensing(self):
        self.root.mainloop()

    def _car_entered(self):
        self.entry_sensor.on_car_entry()

    def _car_exited(self):
        self.exit_sensor.on_car_exit()


if __name__ == '__main__':
    from smartpark.config import Config

    # CLIDetector(<entry_config>, <exit_config>).start_sensing()
