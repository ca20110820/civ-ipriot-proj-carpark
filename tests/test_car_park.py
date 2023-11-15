import unittest

from datetime import datetime
import random

from smartpark.config import Config
from smartpark.carpark import SimulatedCarPark, CarPark
from smartpark.sensor import Detector
from smartpark.car import Car
from smartpark.project_paths import PROJECT_ROOT_DIR


random.seed(0)


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
            print(car.to_json_format(indent=4))
            self.publish_to_display()
        else:
            if self.entry_or_exit_time is None:
                self.entry_or_exit_time = datetime.now()
            print("There are no cars in the park to exit!")

        return car

    def on_message(self, client, userdata, message):
        pass


class TestCarPark(unittest.TestCase):
    def setUp(self) -> None:
        self.car_park_name = "carpark1"
        self.config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')
        self.car_park = MockCarPark(self.config.get_car_park_config(self.car_park_name))
        self.detector = MockDetector()
        self.fixed_num_bays = self.config.get_car_park_config(self.car_park_name)["total_bays"]

    def test_on_message(self):
        for enter_or_exit, temperature in self.detector.start_sensing():
            if enter_or_exit == "Enter":
                self.car_park.temperature = temperature
                car = self.car_park.on_car_entry()

                self.assertIsInstance(car.entry_time, datetime)
                self.assertIsInstance(car.entry_temperature, float)
                self.assertIsNone(car.exit_time)
                self.assertIsNone(car.exit_temperature)

                self.assertLessEqual(self.car_park.parked_cars, self.fixed_num_bays)
                self.assertGreaterEqual(self.car_park.total_cars, 1)
                self.assertLessEqual(self.car_park.available_bays, self.fixed_num_bays)
                self.assertGreaterEqual(self.car_park.available_bays, 0)

                self.assertEqual(len(self.car_park.get_all_cars()), self.car_park.total_cars)

                if self.car_park.total_cars <= self.car_park.total_bays:
                    self.assertEqual(self.car_park.un_parked_cars, 0)
                else:
                    self.assertGreaterEqual(self.car_park.un_parked_cars, 1)

            elif enter_or_exit == "Exit":
                self.car_park.temperature = temperature
                car: Car | None = self.car_park.on_car_exit()

                if isinstance(car, Car):
                    self.assertTrue(not car.is_parked)
                    self.assertIsInstance(car.exit_time, datetime)
                    self.assertIsInstance(car.exit_temperature, float)
                else:
                    self.assertEqual(self.car_park.total_cars, 0)

                self.assertLessEqual(self.car_park.parked_cars, self.fixed_num_bays)
                self.assertGreaterEqual(self.car_park.total_cars, 0)
                self.assertLessEqual(self.car_park.available_bays, self.fixed_num_bays)
                self.assertGreaterEqual(self.car_park.available_bays, 0)

                self.assertEqual(len(self.car_park.get_all_cars()), self.car_park.total_cars)

                if self.car_park.available_bays == self.fixed_num_bays:
                    self.assertEqual(self.car_park.total_cars, 0)
            else:
                break


if __name__ == "__main__":
    unittest.main()
