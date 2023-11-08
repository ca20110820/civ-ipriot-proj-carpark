import unittest
import random
import os

from smartpark.config import Config
from smartpark.sensor import Sensor, Detector
from smartpark.project_paths import CONFIG_DIR


random.seed(0)  # Seed=0 & SampleSize=30 & min_temperature=20 & max_temperature=30


class MockSensor(Sensor):
    TEMPERATURE_GENERATOR = None

    @property
    def temperature(self):
        return next(MockSensor.TEMPERATURE_GENERATOR)

    @staticmethod
    def temperature_generator():
        with open(os.path.join(os.path.dirname(__file__), "sample_signals.txt"), 'r') as file:
            for line in file:
                yield int(line.rstrip().split(',')[1])


MockSensor.TEMPERATURE_GENERATOR = MockSensor.temperature_generator()


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
            enter_or_exit, temperature = message.split(',')
            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertLessEqual(float(temperature), 30)
            self.assertGreaterEqual(float(temperature), 20)


if __name__ == "__main__":
    unittest.main()
