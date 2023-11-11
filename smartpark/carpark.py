import pprint
import random

import paho.mqtt.client as paho
from typing import List, Any
from datetime import datetime

from smartpark.utils import quit_listener
from smartpark.mqtt_device import MqttDevice
from smartpark.car import Car
from smartpark.logger import class_logger
from smartpark.project_paths import LOG_DIR


class CarPark(MqttDevice):
    def __init__(self, config: dict, *args, **kwargs):
        mqtt_config = {k: v for k, v in config.items() if k not in ["total_bays"]} | {"topic-qualifier": "na"}
        super().__init__(mqtt_config, *args, **kwargs)

        self.display_topic: str = self.create_topic_qualifier("display")  # Topic for Publication to Displays
        self._sensor_topics: List[str] = []

        self.client.on_message = self.on_message

        self._total_bays = config["total_bays"]

        self._cars: List[Car] = []

        self._temperature: float | int | None = None  # From Sensor Message
        self._entry_or_exit_time: datetime | None = None  # Passed from the Car

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value
    
    @property
    def total_cars(self) -> int:
        return len(self._cars)
    
    @property
    def parked_cars(self) -> int:
        return len(self.get_parked_cars())

    @property
    def un_parked_cars(self) -> int:
        return len(self.get_un_parked_cars())

    @property
    def total_bays(self) -> int:
        return self._total_bays

    @property
    def available_bays(self) -> int:
        num_available_bays = self._total_bays - len(self.get_parked_cars())
        assert 0 <= num_available_bays, "Number of Bays Cannot be Negative!"
        return num_available_bays

    def get_parked_cars(self) -> List[Car]:
        """Get List of Parked Cars"""
        return [car for car in self._cars if car.is_parked]

    def get_un_parked_cars(self) -> List[Car]:
        """Get List of Un-Parked Cars"""
        return [car for car in self._cars if not car.is_parked]

    def get_all_cars(self) -> List[Car]:
        """Get List of All Cars"""
        return self.get_parked_cars() + self.get_un_parked_cars()

    def register_sensor_topic(self, sensor_topic: str, *args, **kwargs):
        """Register a Sensor Topic"""
        if sensor_topic in self._sensor_topics:
            return

        self._sensor_topics.append(sensor_topic)
        self.client.subscribe(sensor_topic, *args, **kwargs)

    def unregister_sensor_topic(self, sensor_topic: str, *args, **kwargs):
        """Unregister a Sensor Topic"""
        if sensor_topic not in self._sensor_topics:
            return

        self._sensor_topics = [topic for topic in self._sensor_topics if topic != sensor_topic]
        self.client.unsubscribe(sensor_topic, *args, **kwargs)

    def add_car(self, car: Car):
        """Add a Car in the Car Park"""
        assert self.temperature is not None, "Update the Temperature!"

        # Note: The recently added car does not necessarily get parked first.

        car.entered_car_park(self.temperature)
        self._entry_or_exit_time = car.entry_time
        self._cars.append(car)

    def remove_car(self, car: Car):
        """Remove a Car from the Car Park"""
        assert self.temperature is not None, "Update the Temperature!"

        # Note: As an example, we can randomly select any car (parked or un-parked) to exit.
        # Need to implement logic in on_car_exit() method.

        car.exited_car_park(self.temperature)
        self._entry_or_exit_time = car.exit_time
        self._cars = [c for c in self._cars if c.license_plate != car.license_plate]

    def publish_to_display(self):
        """Publish the latest Entry/Exit Event to listening Displays.

        Format of Message String:
        "<available-bays>;<temperature>;<time>;<total-cars>;<parked-cars>;<un-parked-cars>"
        """
        msg_str = f"{self.available_bays};" \
                  f"{self.temperature};" \
                  f"{self._entry_or_exit_time.strftime('%Y-%m-%d %H:%M:%S')};"\
                  f"{self.total_cars};"\
                  f"{self.parked_cars};"\
                  f"{self.un_parked_cars}"

        self.client.publish(self.display_topic, msg_str)
        self._print_car_park_state()
        print("=" * 100, "\n")

    def _print_car_park_state(self):
        """Print Car Park State"""

        print_dict = {"Available Bays": self.available_bays,
                      "Number of Cars": self.total_cars,
                      "Number of Parked Cars": self.parked_cars,
                      "Number of Un-parked Cars": self.un_parked_cars,
                      "Time": self._entry_or_exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                      "Temperature": self.temperature
                      }
        pprint.pprint(print_dict)

    def start_serving(self, *args, **kwargs):
        """Override and Implement the Event Loop"""
        # e.g. self.client.loop_forever()
        raise NotImplementedError()

    def on_car_entry(self, *args, **kwargs):
        """Override and Implement how a new car would be generated and parked"""
        raise NotImplementedError()

    def on_car_exit(self, *args, **kwargs):
        """Override and Implement how a car which car would un-park and exit"""
        raise NotImplementedError()

    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        """Override and Implement the Callback as a Subscriber to Sensors"""
        raise NotImplementedError()


@class_logger(LOG_DIR / 'car_park' / 'car_park.log', 'car_park_logger')
class SimulatedCarPark(CarPark):
    def start_serving(self):
        self.logger.info(f"Car Park Start Serving ...")
        # e.g. self.client.loop_forever()
        self.client.loop_forever()

    def on_car_entry(self):
        # Generate a Random Car
        car = Car.generate_random_car(["ModelA", "ModelB", "ModelC"])

        self.add_car(car)  # By default, this will be un-parked, thus there will be at least 1 un-parked car(s)
        self.logger.info(f"Car Entered - {car.to_json_format()}")

        if self.available_bays > 0:  # If there are available bay(s)
            # Select a Car to be parked, car who just entered or un-parked car(s)
            car_to_park = random.choice(self.get_un_parked_cars())
            car_to_park.car_parked()
            self.logger.info(f"Car '{car_to_park}' got parked")
            print(car_to_park.to_json_format(indent=4))

        self.publish_to_display()

    def on_car_exit(self):
        # Select random car (parked or un-parked) to exit.
        all_cars = self.get_all_cars()
        car: Car | None = random.choice(all_cars) if len(all_cars) > 0 else None

        if car is not None:
            car.car_unparked()  # Un-park the car regardless if it's parked or not!
            self.logger.info(f"Car '{car}' got un-parked")
            self.remove_car(car)
            self.logger.info(f"Car Exited - {car.to_json_format()}")
            print(car.to_json_format(indent=4))
            self.publish_to_display()
        else:
            self.logger.warning(f"Exiting while there's no cars in Car Park")
            print("There are no cars in the park to exit!")

    @quit_listener
    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        msg = message.payload.decode()

        self.logger.info(f"Message Received - {msg}")

        try:
            signal, self.temperature = msg.split(",")
        except Exception as e:
            print(e)
            self.logger.error(str(e))
            return

        if signal == "Enter":
            self.on_car_entry()
        elif signal == "Exit":
            self.on_car_exit()


if __name__ == "__main__":
    from smartpark.config import Config
    from smartpark.project_paths import PROJECT_ROOT_DIR

    toml_path = PROJECT_ROOT_DIR / 'configurations' / 'sample_smartpark_config.toml'

    car_park_config = Config(toml_path)

    car_park = SimulatedCarPark(car_park_config.get_car_park_config("carpark1"))
    print(car_park.display_topic)
    for sensor_top in car_park_config.get_sensor_pub_topics("carpark1"):
        car_park.register_sensor_topic(sensor_top)

    car_park.start_serving()
