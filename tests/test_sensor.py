import unittest
import random
import os

from smartpark.config import Config
from smartpark.sensor import Sensor, Detector, FileDetector
from smartpark.project_paths import CONFIG_DIR, PROJECT_ROOT_DIR


random.seed(0)  # Seed=0 & SampleSize=30 & min_temperature=20 & max_temperature=30


class MockSensor(Sensor):
    TEMPERATURE_GENERATOR = None

    def temperature_generator(self) -> float | int:
        return next(MockSensor.TEMPERATURE_GENERATOR)

    @staticmethod
    def mock_temperature_generator():
        with open(os.path.join(os.path.dirname(__file__), "sample_signals.txt"), 'r') as file:
            for line in file:
                yield int(line.rstrip().split(',')[1])


MockSensor.TEMPERATURE_GENERATOR = MockSensor.mock_temperature_generator()


class MockEntrySensor(MockSensor):
    def on_car_entry(self):
        return f"Enter,{self.temperature}"


class MockExitSensor(MockSensor):
    def on_car_exit(self):
        return f"Exit,{self.temperature}"


class MockDetector(Detector):
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict):
        self.entry_sensor = MockEntrySensor(entry_sensor_config)
        self.exit_sensor = MockExitSensor(exit_sensor_config)

    def start_sensing(self):
        with open(os.path.join(os.path.dirname(__file__), "sample_signals.txt"), "r") as file:
            for line in file:
                line = line.rstrip()
                signal, temperature = line.split(',')
                if signal == "Enter":
                    yield self.entry_sensor.on_car_entry()
                elif signal == "Exit":
                    yield self.exit_sensor.on_car_exit()
                else:
                    yield None


class TestSensor(unittest.TestCase):
    def setUp(self) -> None:
        config = Config(CONFIG_DIR / 'sample_smartpark_config.toml')

        self.detector = MockDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
                                     config.get_sensor_config_dict("carpark1", "sensor2", "exit")
                                     )

    def test_message(self):
        for message in self.detector.start_sensing():
            if message is None:
                print("Message was None! Stop Sensing ...")
                break

            rnd_enter_or_exit = random.choice(["Enter", "Exit"])
            rnd_temperature = random.randint(20, 30)
            rnd_message = f"{rnd_enter_or_exit},{rnd_temperature}"

            self.assertEqual(rnd_message, message)
            self.assertEqual(len(message.split(',')), 2)
            enter_or_exit, temperature = message.split(',')
            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertLessEqual(float(temperature), 30)
            self.assertGreaterEqual(float(temperature), 20)


class MockFileDetector(FileDetector):
    def start_sensing(self, use_quit=True):
        # Copy-Pasted from original implementation except, instead of sending mqtt messages,
        # we yield the results so we can iterate and test.
        with open(self._file_path, 'r') as file:
            for line in file:
                line = line.rstrip()
                enter_or_exit, temperature = line.split(',')
                if enter_or_exit == 'Enter':
                    yield enter_or_exit, self.entry_sensor.temperature
                elif enter_or_exit == 'Exit':
                    yield enter_or_exit, self.exit_sensor.temperature


class TestFileDetector(unittest.TestCase):
    def setUp(self) -> None:
        config = Config(CONFIG_DIR / 'sample_smartpark_config.toml')

        self.detector = MockFileDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
                                         config.get_sensor_config_dict("carpark1", "sensor2", "exit"),
                                         PROJECT_ROOT_DIR / 'tests' / 'sample_signals.txt'
                                         )

    def test_detection(self):
        counter = 0
        for enter_or_exit, temperature in self.detector.start_sensing():
            print(f"{enter_or_exit},{temperature}")
            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertIsInstance(temperature, float)
            counter += 1

        self.assertEqual(counter, 30)


if __name__ == "__main__":
    unittest.main()
