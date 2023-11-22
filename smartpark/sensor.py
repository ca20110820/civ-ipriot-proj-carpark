from typing import Generator, Type, TypeVar
import time
from abc import ABC, abstractmethod
import tkinter as tk
import random

from smartpark.config import Config
from smartpark.mqtt_device import MqttDevice
from smartpark.logger import class_logger
from smartpark.project_paths import LOG_DIR, CONFIG_DIR


class Sensor(MqttDevice):
    """Base Class for Sensors. It follows the Publisher Pattern, but can include (infinite) event loop."""
    @property
    def temperature(self):
        """Returns the current temperature"""
        # Can get from random number generator, file, or API.
        return self.temperature_generator()

    def on_detection(self, message: str):
        """Publish Message to CarPark"""
        self.client.publish(self.topic_address, message)

    def temperature_generator(self) -> float | int:
        """Override and Implement How a Temperature is Generated. e.g. Random number generator, File, or API"""
        raise NotImplementedError()


class EntrySensor(Sensor):

    def on_car_entry(self):
        self.on_detection(f"Enter,{self.temperature}")

    def temperature_generator(self):
        return random.randint(20, 30)


class ExitSensor(Sensor):
    def on_car_exit(self):
        self.on_detection(f"Exit,{self.temperature}")

    def temperature_generator(self):
        return random.randint(20, 30)


class Detector(ABC):
    """Base Class for Detectors. Separated from Sensor class to create a composition of Sensors: Entry, Exit, or Both.
    """

    QUIT_FLAG = False  # Optional Quit Flag

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Override and Implement Sensing Loop."""
        pass


@class_logger(LOG_DIR / 'sensor' / 'cli_detector' / 'sensor.log', 'cli_detector_logger')
class CLIDetector(Detector):
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict):
        self.entry_sensor = EntrySensor(entry_sensor_config)
        self.exit_sensor = ExitSensor(exit_sensor_config)

    def start_sensing(self):
        while not self.QUIT_FLAG:
            user_input = input("E or X >>> ")

            if user_input in ["E", "e", "enter"]:
                self.entry_sensor.on_car_entry()
                self.logger.info("Car Entered")
            elif user_input in ["X", "x", "exit"]:
                self.logger.info("Car Exited")
                self.exit_sensor.on_car_exit()
            elif user_input in ["q", "Q", "quit"]:
                self.logger.info("Quit")
                self.QUIT_FLAG = True
                self.entry_sensor.client.publish("quit", "quit")
            else:
                print("Invalid Input!\n")
                continue


@class_logger(LOG_DIR / 'sensor' / 'tk_detector' / 'sensor.log', 'tk_detector_logger')
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
        self.logger.info("Start Sensing")
        self.root.mainloop()

    def _car_entered(self):
        self.logger.info("Car Entered")
        self.entry_sensor.on_car_entry()

    def _car_exited(self):
        self.logger.info("Car Exited")
        self.exit_sensor.on_car_exit()

    def on_closing(self):
        self.logger.info("Quit")
        self.entry_sensor.client.publish("quit", "quit")
        exit()


class FileSensor(Sensor):

    TEMPERATURE_GENERATOR: Generator = None

    def temperature_generator(self) -> float | int:
        # return next(FileDetector.FileSensor.TEMPERATURE_GENERATOR)
        return next(self.TEMPERATURE_GENERATOR)

    @staticmethod
    def create_temperature_generator(file_path: str):
        with open(file_path, 'r') as file:
            for line in file:
                yield float(line.rstrip().split(',')[1])

    def register_temperature_generator(self, inp_generator: Generator):
        self.TEMPERATURE_GENERATOR = inp_generator


class FileEntrySensor(FileSensor):
    def on_car_entry(self):
        self.on_detection(f"Enter,{self.temperature}")


class FileExitSensor(FileSensor):
    def on_car_exit(self):
        self.on_detection(f"Exit,{self.temperature}")


class FileDetector(Detector):
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict,
                 enter_exit_temperature_filepath: str
                 ):
        # Format: "<Enter|Exit>,<temperature>"

        # Note: Could have implemented alone without FileSensor.

        self._file_path = enter_exit_temperature_filepath

        # Need to be instantiated outside, then attach to file entry and exit sensors
        temperature_generator = FileSensor.create_temperature_generator(self._file_path)

        self.entry_sensor = FileEntrySensor(entry_sensor_config)
        self.exit_sensor = FileExitSensor(exit_sensor_config)

        self.entry_sensor.register_temperature_generator(temperature_generator)
        self.exit_sensor.register_temperature_generator(temperature_generator)

    def start_sensing(self, use_quit=True):
        with open(self._file_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                enter_or_exit, temperature = line.split(',')

                # rnd_time_interval = random.uniform(0.05, 0.55)
                # time.sleep(rnd_time_interval)
                # time.sleep(1)

                if enter_or_exit == 'Enter':
                    self.entry_sensor.on_car_entry()
                elif enter_or_exit == 'Exit':
                    self.exit_sensor.on_car_exit()
                else:
                    if use_quit:
                        self.entry_sensor.client.publish("quit", "quit")
                        self.exit_sensor.client.publish("quit", "quit")
                    print("Done Sensing from File!")
                    break

                yield enter_or_exit, float(temperature)


@class_logger(LOG_DIR / 'sensor' / 'random_detector' / 'sensor.log', 'random_detector_logger')
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
                    self.logger.info("Car Entered")
                    self.entry_sensor.on_detection(f"Enter,{rnd_temperature}")
                else:
                    self.logger.info("Car Exited")
                    self.exit_sensor.on_detection(f"Exit,{rnd_temperature}")
            except KeyboardInterrupt:
                self.logger.info("KeyboardInterrupt - Quit")
                self.entry_sensor.client.publish("quit", "quit")
                self.exit_sensor.client.publish("quit", "quit")
                exit()


_T = TypeVar('_T', bound=Detector)


class DetectorFactory:
    def __init__(self, config_path: str, car_park_name: str):
        self._config = Config(config_path)
        self._car_park_name = car_park_name

    def create_detector_entry_exit(self, detector_type: Type[_T], entry_sensor_name: str, exit_sensor_name: str, *args,
                                   **kwargs):
        # This method is used when a pair of entry-exit sensors have difference names.
        return detector_type(self._config.get_sensor_config_dict(self._car_park_name, entry_sensor_name, "entry"),
                             self._config.get_sensor_config_dict(self._car_park_name, exit_sensor_name, "exit"),
                             *args, **kwargs
                             )

    def create_detector_entry_exit_same_name(self, detector_type: Type[_T], sensor_name: str, *args, **kwargs):
        # This method is used when a pair of entry-exit sensors have same names.
        return detector_type(self._config.get_sensor_config_dict(self._car_park_name, sensor_name, "entry"),
                             self._config.get_sensor_config_dict(self._car_park_name, sensor_name, "exit"),
                             *args, **kwargs
                             )

    def create_detector_entry(self):
        # Some Detectors may only require entry sensor.
        ...

    def create_detector_exit(self):
        # Some Detectors may only require exit sensor.
        ...


if __name__ == '__main__':
    toml_path = CONFIG_DIR / 'sample_smartpark_config.toml'

    config = Config(toml_path)

    detector = DetectorFactory(CONFIG_DIR / 'sample_smartpark_config.toml', "carpark1").create_detector_entry_exit(
        TkDetector, "sensor1", "sensor2")
    detector.start_sensing()
