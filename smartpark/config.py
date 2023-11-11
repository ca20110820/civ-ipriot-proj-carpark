"""

Example: config.toml
[[car_parks]]
name = "carpark1"
location = "Moondaloop Park"
host = "localhost"
port = 1883
topic-root = "carpark1"
total_bays = 5

[[car_parks.sensors]]
name = "sensor1"
location = "L306"
type = "entry"

[[car_parks.sensors]]
name = "sensor2"
location = "L306"
type = "exit"

[[car_parks.displays]]
name = "display1"

# -----------------------------------------------

[[car_parks]]
name = "carpark2"
location = "Jandurah Park"
host = "localhost"
port = 1883
topic-root = "carpark2"
total_bays = 1

[[car_parks.sensors]]
name = "sensor1"
location = "L250"
type = "entry"

[[car_parks.sensors]]
name = "sensor2"
location = "L250"
type = "exit"

[[car_parks.displays]]
name = "display1"

[[car_parks.displays]]
name = "display2"


"""

from typing import List
import toml
import pprint
import os

from smartpark.project_paths import PROJECT_ROOT_DIR


class Config:
    """Class for Parsing a Configuration File.
    """
    def __init__(self, config_file_path: str):
        self._config_file_path = config_file_path

        # Config for the Whole Car Park, including Sensors and Displays, not the Car Park class
        self._car_park_dict_configs: List[dict] = []

        with open(self._config_file_path, "r") as file:
            config_dict = toml.load(file)

            for car_park_config in config_dict["car_parks"]:
                self._car_park_dict_configs.append(car_park_config)

    @property
    def config_file_path(self):
        return self._config_file_path

    @property
    def car_park_configs(self):
        """List of 'Complete' Raw Configurations of Car Parks. This includes the  configurations of Sensors and
        Displays. Not to be confused with CarPark Configuration as a Class"""
        return self._car_park_dict_configs

    def get_car_park_names(self) -> List[str]:
        """Returns the List of Car Park Names"""
        return [car_park_config["name"] for car_park_config in self._car_park_dict_configs]

    def _get_common_config(self, car_park_name: str) -> dict:
        """Returns the Common Configuration Key-Value Pairs

        This includes:
            - topic-root: str
            - host: str
            - port: int
        """
        if car_park_name not in self.get_car_park_names():
            # TODO: Create a Decorator for Checking whether the car_park_name exist.
            raise ValueError("The given car park name is not in the configuration file.")

        for car_park_dict_config in self._car_park_dict_configs:
            out_dict = {}
            if car_park_name == car_park_dict_config["name"]:
                out_dict["topic-root"] = car_park_dict_config["topic-root"]
                out_dict["host"] = car_park_dict_config["host"]
                out_dict["port"] = car_park_dict_config["port"]
                return out_dict

    def _get_car_park_complete_config(self, car_park_name: str) -> dict:
        """Returns the Config for the Whole Car Park, including Sensors and Displays, not the Car Park class from
        a given Car Park Name"""
        if car_park_name not in self.get_car_park_names():
            raise ValueError("The given car park name is not in the configuration file.")

        for car_park_dict_config in self._car_park_dict_configs:
            if car_park_name == car_park_dict_config["name"]:
                return car_park_dict_config

    def get_sensor_configs(self, car_park_name: str) -> List[dict]:
        """Returns a List of Sensor Configurations as a Dictionary from a given Car Park Name"""
        common_config = self._get_common_config(car_park_name)
        sensor_dict_configs: List[dict] = self._get_car_park_complete_config(car_park_name)["sensors"]

        out_sensor_configs = []

        for sensor_dict_config in sensor_dict_configs:
            temp_sensor_dict = dict()
            temp_sensor_dict["name"] = sensor_dict_config["name"]
            temp_sensor_dict["topic-qualifier"] = sensor_dict_config["type"]
            temp_sensor_dict["location"] = sensor_dict_config["location"]
            out_sensor_configs.append(temp_sensor_dict | common_config)

        return out_sensor_configs

    def get_car_park_config(self, car_park_name: str) -> dict:
        """Returns a Car Park Configuration as a Dictionary from a given Car Park Name"""
        # Return the configuration for instantiating a CarPark instance
        if car_park_name not in self.get_car_park_names():
            raise ValueError("The given car park name is not in the configuration file.")

        out_dict = {}

        common_config = self._get_common_config(car_park_name)

        car_park_complete_config = self._get_car_park_complete_config(car_park_name)

        out_dict["name"] = car_park_complete_config["name"]
        out_dict["location"] = car_park_complete_config["location"]
        out_dict["total_bays"] = car_park_complete_config["total_bays"]

        return out_dict | common_config

    def get_display_configs(self, car_park_name: str) -> List[dict]:
        """Returns a List of Display Configurations as a Dictionary from a given Car Park Name"""
        common_config = self._get_common_config(car_park_name)
        display_dict_configs: List[dict] = self._get_car_park_complete_config(car_park_name)["displays"]

        out_display_configs = []

        for display_dict_config in display_dict_configs:
            temp_display_dict = dict()
            temp_display_dict["name"] = display_dict_config["name"]
            temp_display_dict["topic-qualifier"] = "na"  # default='na' for Display

            # If location, is not provided for display, it defaults to location of the Car Park
            display_location = display_dict_config.get("location", None)
            temp_display_dict["location"] = display_location if display_location is not None else \
                self._get_car_park_complete_config(car_park_name)["location"]

            out_display_configs.append(temp_display_dict | common_config)

        return out_display_configs

    def get_sensor_pub_topics(self, car_park_name: str) -> List[str]:
        """Create and Get Sensor Publication Topic Strings from a given Car Park Name.

        This method can be used by a Car Park instance for subscribing/registering sensor topics.

        Formats:
            - "<topic-root>/<location>/<sensor-name>/entry"
            - "<topic-root>/<location>/<sensor-name>/exit"
        """

        sensor_pub_topics = []

        sensor_configs = self.get_sensor_configs(car_park_name)

        for sensor_config in sensor_configs:
            topic = f"{sensor_config['topic-root']}/{sensor_config['location']}/" \
                    f"{sensor_config['name']}/{sensor_config['topic-qualifier']}"
            sensor_pub_topics.append(topic)

        return sensor_pub_topics

    def create_car_park_display_topic(self, car_park_name: str) -> str:
        """Create and Get Topic for Publishing to Displays.

        This method can be used by a Display instance."""
        car_park_config = self.get_car_park_config(car_park_name)
        topic = f"{car_park_config['topic-root']}/{car_park_config['location']}/" \
                f"{car_park_config['name']}/display"
        return topic

    def get_sensor_config_dict(self, car_park_name: str, sensor_name: str, sensor_type: str) -> dict | None:
        """Getting a Sensor Configuration by Car Park Name, Sensor Name, and Sensor Type ('entry'/'exit')

        Used as argument for Sensor construction to filter and get entry and exit sensor configurations.
        """
        sensor_config_dict_list = self.get_sensor_configs(car_park_name)
        for sensor_config_dict in sensor_config_dict_list:
            if sensor_config_dict["name"] == sensor_name and sensor_config_dict["topic-qualifier"] == sensor_type:
                return sensor_config_dict
        return None


if __name__ == "__main__":
    config = Config(PROJECT_ROOT_DIR / 'configurations' / 'sample_smartpark_config.toml')

    car_park = "carpark1"

    print(config.config_file_path)
    print(config.get_car_park_names())
    print("-" * 50)
    pprint.pprint(config.get_car_park_config(car_park))
    print("-" * 50)
    for sensor_conf in config.get_sensor_configs(car_park):
        pprint.pprint(sensor_conf)
        print("-" * 50)
    for display_conf in config.get_display_configs(car_park):
        pprint.pprint(display_conf)
        print("-" * 50)
    for sensor_topic in config.get_sensor_pub_topics(car_park):
        print(sensor_topic)
    print("-" * 50)
    print(config.create_car_park_display_topic(car_park))
    print("-" * 50)
    print(config.get_sensor_config_dict(car_park, "sensor1", "entry"))
    print("-" * 50)
    print(config.get_sensor_config_dict(car_park, "sensor2", "exit"))
