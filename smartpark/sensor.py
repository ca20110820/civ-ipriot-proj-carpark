import time
from abc import ABC, abstractmethod
import tkinter as tk
import random


from smartpark.mqtt_device import MqttDevice


class Sensor(MqttDevice):

    _temperature: float

    @property
    def temperature(self):
        """Returns the current temperature"""
        # Can get from random number generator, file, or API.
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        self._temperature = value

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
                self.entry_sensor.client.publish("quit", "quit")
            else:
                print("Invalid Input!\n")
                continue


class TkDetector(Detector):
    def __init__(self, entry_sensor_config, exit_sensor_config):
        self.entry_sensor = EntrySensor(entry_sensor_config)
        self.exit_sensor = ExitSensor(exit_sensor_config)

        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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

    def on_closing(self):
        self.entry_sensor.client.publish("quit", "quit")
        exit()


class RandomDetector(Detector):
    def __init__(self, entry_sensor_config, exit_sensor_config,
                 lower_bound=20, upper_bound=30, enter_prb=0.55,
                 min_time_interval=0.3, max_time_interval=1.2
                 ):

        self.entry_sensor = EntrySensor(entry_sensor_config)
        self.exit_sensor = ExitSensor(exit_sensor_config)

        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._enter_prb = enter_prb
        self._min_time_interval = min_time_interval
        self._max_time_interval = max_time_interval

    def start_sensing(self):
        while True:
            try:
                p = self._enter_prb
                rnd_enter_or_exit = random.choices(["Enter", "Exit"], weights=[p, 1-p], k=1)[0]

                rnd_temperature = random.uniform(self._lower_bound, self._upper_bound)
                rnd_time_interval = random.uniform(self._min_time_interval, self._max_time_interval)
                time.sleep(rnd_time_interval)

                if rnd_enter_or_exit == "Enter":
                    self.entry_sensor.on_detection(f"Enter,{rnd_temperature}")
                else:
                    self.exit_sensor.on_detection(f"Exit,{rnd_temperature}")
            except KeyboardInterrupt:
                self.entry_sensor.client.publish("quit", "quit")
                self.exit_sensor.client.publish("quit", "quit")
                exit()


if __name__ == '__main__':
    from smartpark.config import Config
    from smartpark.project_paths import PROJECT_ROOT_DIR

    toml_path = PROJECT_ROOT_DIR / 'configurations' / 'sample_smartpark_config.toml'

    config = Config(toml_path)

    # RandomDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
    #                config.get_sensor_config_dict("carpark1", "sensor2", "exit"),
    #                lower_bound=20, upper_bound=30, enter_prb=0.6,
    #                min_time_interval=0.1, max_time_interval=0.5
    #                ) \
    #     .start_sensing()

    TkDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
               config.get_sensor_config_dict("carpark1", "sensor2", "exit")) \
        .start_sensing()
