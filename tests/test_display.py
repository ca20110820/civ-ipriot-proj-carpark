import unittest

from datetime import datetime
import random
import os

from smartpark.project_paths import CONFIG_DIR
from smartpark.config import Config
from smartpark.car import Car
from smartpark.sensor import Detector
from smartpark.carpark import CarPark
from smartpark.display import Display


class MockDetector(Detector):
    def start_sensing(self):
        with open(os.path.join(os.path.dirname(__file__), "sample_signals.txt"), "r") as file:
            for line in file:
                line = line.rstrip()
                signal, temperature = line.split(',')
                if signal in ["Enter", "Exit"]:
                    yield signal, float(temperature)


class MockCarPark(CarPark):
    def start_serving(self):
        pass

    def on_car_entry(self):
        # Generate a Random Car
        car = Car.generate_random_car(["ModelA", "ModelB", "ModelC"])

        self.add_car(car)  # By default, this will be un-parked, thus there will be at least 1 un-parked car(s)

        if self.available_bays > 0:  # If there are available bay(s)
            # Select a Car to be parked, car who just entered or un-parked car(s)
            car_to_park = random.choice(self.get_un_parked_cars())
            car_to_park.car_parked()

        # Only return the car who just entered, not parked
        return car

    def on_car_exit(self):
        all_cars = self.get_all_cars()
        car: Car | None = random.choice(all_cars) if len(all_cars) > 0 else None

        if car is not None:
            car.car_unparked()  # Un-park the car regardless if it's parked or not!
            self.remove_car(car)
            print(car.to_json_format(indent=4))
        else:
            if self.entry_or_exit_time is None:
                self.entry_or_exit_time = datetime.now()
            print("There are no cars in the park to exit!")

        return car

    def on_message(self, client, userdata, message):
        pass


class MockDisplay(Display):

    DATA: list = []

    def start_listening(self):
        pass

    def on_message(self, client, userdata, message):
        pass

    def mock_on_message(self, message: str):
        # ["<available-bays>", "<temperature>", "<time>", "<num-cars>", "<num-parked-cars>", "<num-un-parked-cars>"]

        msg = message.split(';')

        self.DATA.append(msg)

        return msg


class TestDisplay(unittest.TestCase):
    def setUp(self) -> None:
        self.car_park_name = "carpark1"
        self.config = Config(CONFIG_DIR / 'sample_smartpark_config.toml')

        self.car_park = MockCarPark(self.config.get_car_park_config(self.car_park_name))
        self.detector = MockDetector()
        self.display = MockDisplay(self.config.get_display_configs(self.car_park_name)[0],
                                   self.config.create_car_park_display_topic("carpark1")
                                   )

    def test_display(self):

        self.assertEqual(len(self.display.DATA), 0)

        for enter_or_exit, temperature in self.detector.start_sensing():
            print(f"Signal: {enter_or_exit},{temperature}")
            self.car_park.temperature = temperature
            if enter_or_exit == "Enter":
                self.car_park.on_car_entry()

            if enter_or_exit == "Exit":
                self.car_park.on_car_exit()

            msg_str = self.car_park.publish_to_display()
            self.assertIsInstance(msg_str, str)
            received_msg = self.display.mock_on_message(msg_str)
            self.assertIsInstance(received_msg, list)
            self.assertEqual(len(received_msg), 6)

        self.assertEqual(len(self.display.DATA), 30)


if __name__ == "__main__":
    unittest.main()
