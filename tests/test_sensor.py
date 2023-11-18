import unittest
import random

from smartpark.config import Config
from smartpark.sensor import Sensor, Detector, FileDetector, DetectorFactory
from smartpark.project_paths import PROJECT_ROOT_DIR


random.seed(0)  # Seed=0 & SampleSize=30 & min_temperature=20 & max_temperature=30


class MockSensor(Sensor):
    TEMPERATURE_GENERATOR = None

    def temperature_generator(self) -> float | int:
        return next(MockSensor.TEMPERATURE_GENERATOR)

    @staticmethod
    def mock_temperature_generator():
        with open(PROJECT_ROOT_DIR / 'tests' / "sample_signals.txt", 'r') as file:
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
        with open(PROJECT_ROOT_DIR / 'tests' / 'sample_signals.txt', "r") as file:
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
        config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')

        self.detector = MockDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
                                     config.get_sensor_config_dict("carpark1", "sensor2", "exit")
                                     )

        self.detector_factory = DetectorFactory(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml', 'carpark1')

    def test_message(self):
        """Test Message Structure and Correctness from Sensor"""
        count = 0
        for message in self.detector.start_sensing():
            if message is None:
                print("Message was None! Stop Sensing ...")
                break

            count += 1

            rnd_enter_or_exit = random.choice(["Enter", "Exit"])
            rnd_temperature = random.randint(20, 30)
            rnd_message = f"{rnd_enter_or_exit},{rnd_temperature}"

            enter_or_exit, temperature = message.split(',')
            self.assertEqual(rnd_message, message)
            self.assertEqual(rnd_enter_or_exit, enter_or_exit)
            self.assertEqual(rnd_temperature, int(temperature))
            self.assertEqual(len(message.split(',')), 2)
            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertLessEqual(float(temperature), 30)
            self.assertGreaterEqual(float(temperature), 20)

        self.assertEqual(count, 30)

    def test_detector_factory(self):
        """Test the Detector Factory"""
        detector = self.detector_factory.create_detector_entry_exit(FileDetector,
                                                                    'sensor1', 'sensor2',
                                                                    PROJECT_ROOT_DIR / 'tests' / 'sample_signals.txt'
                                                                    )

        count = 0
        for enter_or_exit, temperature in detector.start_sensing():
            count += 1

            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertLessEqual(temperature, 30)
            self.assertGreaterEqual(temperature, 20)
            self.assertIsInstance(temperature, float)

        self.assertEqual(count, 30)


class TestFileDetector(unittest.TestCase):
    def setUp(self) -> None:
        config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')

        self.detector = FileDetector(config.get_sensor_config_dict("carpark1", "sensor1", "entry"),
                                     config.get_sensor_config_dict("carpark1", "sensor2", "exit"),
                                     PROJECT_ROOT_DIR / 'tests' / 'sample_signals.txt'
                                     )

    def test_detection(self):
        """Test Output/Yield of FileDetector"""
        counter = 0
        for enter_or_exit, temperature in self.detector.start_sensing():
            print(f"{enter_or_exit},{temperature}")
            self.assertIn(enter_or_exit, ['Enter', 'Exit'])
            self.assertIsInstance(temperature, float)
            counter += 1

        self.assertEqual(counter, 30)


if __name__ == "__main__":
    unittest.main()
