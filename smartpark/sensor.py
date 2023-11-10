from typing import Generator
import time
from abc import ABC, abstractmethod
import tkinter as tk
import random


from smartpark.mqtt_device import MqttDevice
from smartpark.logger import class_logger
from smartpark.project_paths import LOG_DIR


class Sensor(MqttDevice):
    @property
    def temperature(self):
        """Returns the current temperature"""
        # Can get from random number generator, file, or API.
        return self.temperature_generator()

    def on_detection(self, message: str):
        """Publish to CarPark"""
        self.client.publish(self.topic_address, message)

    def temperature_generator(self) -> float | int:
        """Implement How a Temperature is Generated. e.g. Random number generator, File, or API"""
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

    QUIT_FLAG = False

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Define Event Loop"""
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
        return f"Enter,{self.temperature}"


class FileExitSensor(FileSensor):
    def on_car_exit(self):
        return f"Exit,{self.temperature}"


class FileDetector(Detector):
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict,
                 enter_exit_temperature_filepath: str,
                 use_yield: bool = False
                 ):
        # Format: "<Enter|Exit>,<temperature>"
        self._use_yield = use_yield

        self._file_path = enter_exit_temperature_filepath

        # Need to be instantiated outside, then attach to file entry and exit sensors
        temperature_generator = FileSensor.create_temperature_generator(self._file_path)

        self.entry_sensor = FileEntrySensor(entry_sensor_config)
        self.exit_sensor = FileExitSensor(exit_sensor_config)

        # self.entry_sensor.TEMPERATURE_GENERATOR = self.exit_sensor.TEMPERATURE_GENERATOR = temperature_generator
        self.entry_sensor.register_temperature_generator(temperature_generator)
        self.exit_sensor.register_temperature_generator(temperature_generator)

    def start_sensing(self, use_quit=True):
        with open(self._file_path, 'r') as file:
            for line in file:
                line = line.rstrip()
                enter_or_exit, temperature = line.split(',')
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

                if self._use_yield:
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
