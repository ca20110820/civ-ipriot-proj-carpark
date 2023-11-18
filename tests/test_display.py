import unittest

from datetime import datetime
import time
import random

from smartpark.project_paths import PROJECT_ROOT_DIR
from smartpark.config import Config
from smartpark.car import Car
from smartpark.sensor import Detector
from smartpark.carpark import CarPark
from smartpark.display import Display


class MockDetector(Detector):
    def start_sensing(self):
        with open(PROJECT_ROOT_DIR / 'tests' / 'sample_signals.txt', "r") as file:
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

        self.publish_to_display()

        # Only return the car who just entered, not parked
        return car

    def on_car_exit(self):
        all_cars = self.get_all_cars()
        car: Car | None = random.choice(all_cars) if len(all_cars) > 0 else None

        if car is not None:
            car.car_unparked()  # Un-park the car regardless if it's parked or not!
            self.remove_car(car)
            # print(car.to_json_format(indent=4))
        else:
            if self.entry_or_exit_time is None:
                self.entry_or_exit_time = datetime.now()
            print("There are no cars in the park to exit!")

        self.publish_to_display()

        return car

    def on_message(self, client, userdata, message):
        pass


class MockDisplay(Display):

    DATA: list = []

    def start_listening(self):
        self.client.loop()

    def on_message(self, client, userdata, message):
        # ["<available-bays>", "<temperature>", "<time>", "<num-cars>", "<num-parked-cars>", "<num-un-parked-cars>"]
        data = message.payload.decode()  # "<Entry|Exit>,<temperature>"
        msg_str = data.split(';')
        self.DATA.append(msg_str)

    def get_clean_data(self):
        clean_data = []
        for data in self.DATA:
            temp_ls = [None] * 6
            temp_ls[0] = int(data[0])
            temp_ls[1] = float(data[1])
            temp_ls[2] = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
            temp_ls[3] = int(data[3])
            temp_ls[4] = int(data[4])
            temp_ls[5] = int(data[5])
            clean_data.append(temp_ls)

        return clean_data


class TestDisplay(unittest.TestCase):
    def setUp(self) -> None:
        self.car_park_name = "carpark1"
        self.config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')

        self.car_park = MockCarPark(self.config.get_car_park_config(self.car_park_name))
        self.detector = MockDetector()
        self.display = MockDisplay(self.config.get_display_configs(self.car_park_name)[0],
                                   self.config.create_car_park_display_topic("carpark1")
                                   )

    def test_display(self):
        """Test Display Receiving Correct Messages from CarPark"""
        self.assertEqual(len(self.display.DATA), 0)

        for enter_or_exit, temperature in self.detector.start_sensing():
            time.sleep(0.03)  # Need to slow the loop, otherwise mqtt may not catch up and result in error.
            self.car_park.temperature = temperature
            if enter_or_exit == "Enter":
                self.car_park.on_car_entry()
                self.display.start_listening()

            if enter_or_exit == "Exit":
                self.car_park.on_car_exit()
                self.display.start_listening()

            self.display.start_listening()

        self.assertEqual(len(self.display.DATA), 30)

        self.assertTrue(all([len(data) == 6 for data in self.display.DATA]))

        self.assertTrue(
            all([(type(msg) is list and all([type(elem) is str for elem in msg])) for msg in self.display.DATA])
        )


if __name__ == "__main__":
    unittest.main()
