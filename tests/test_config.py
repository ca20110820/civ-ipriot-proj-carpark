import unittest

from smartpark.config import Config
from smartpark.project_paths import PROJECT_ROOT_DIR


class TestConfigParsing(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')

    def test_car_park1(self):
        """Test Parsing Configuration of 'carpark1'"""
        car_park_name = "carpark1"
        self.assertEqual(len(self.config.car_park_configs), 2)
        self.assertIn(car_park_name, self.config.get_car_park_names())

        self.assertEqual(len(self.config._get_common_config(car_park_name).keys()), 3)
        self.assertEqual(self.config._get_common_config(car_park_name)["topic-root"], car_park_name)
        self.assertEqual(self.config._get_common_config(car_park_name)["host"], "localhost")
        self.assertEqual(self.config._get_common_config(car_park_name)["port"], 1883)

        for sensor_config in self.config.get_sensor_configs(car_park_name):
            self.assertIn(sensor_config["name"], ["sensor1", "sensor2"])
            self.assertEqual(sensor_config["location"], "L306")
            self.assertEqual(sensor_config["host"], "localhost")
            self.assertEqual(sensor_config["port"], 1883)
            self.assertEqual(sensor_config["topic-root"], car_park_name)
            self.assertIn(sensor_config["topic-qualifier"], ["entry", "exit"])

        car_park_config = self.config.get_car_park_config(car_park_name)
        self.assertEqual(car_park_config["name"], car_park_name)
        self.assertEqual(car_park_config["location"], "Moondaloop Park")
        self.assertEqual(car_park_config["host"], "localhost")
        self.assertEqual(car_park_config["port"], 1883)
        self.assertEqual(car_park_config["topic-root"], car_park_name)
        self.assertRaises(KeyError, lambda: car_park_config["topic-qualifier"])
        self.assertEqual(car_park_config["total_bays"], 5)

        for display_config in self.config.get_display_configs(car_park_name):
            self.assertIn(display_config["name"], ["display1"])
            self.assertEqual(display_config["location"], "Moondaloop Park")
            self.assertEqual(display_config["host"], "localhost")
            self.assertEqual(display_config["port"], 1883)
            self.assertEqual(display_config["topic-root"], car_park_name)
            self.assertEqual(display_config["topic-qualifier"], "na")

        self.assertEqual(self.config.create_car_park_display_topic(car_park_name),
                         "carpark1/Moondaloop Park/carpark1/display")

        sensor_pub_topics = ["carpark1/L306/sensor1/entry",
                             "carpark1/L306/sensor2/exit"
                             ]
        for pub_topic in sensor_pub_topics:
            self.assertIn(pub_topic, self.config.get_sensor_pub_topics(car_park_name))

        entry_sensor_config_dict = self.config.get_sensor_config_dict(car_park_name, "sensor1", "entry")
        self.assertIn(entry_sensor_config_dict, self.config.get_sensor_configs(car_park_name))

        exit_sensor_config_dict = self.config.get_sensor_config_dict(car_park_name, "sensor2", "exit")
        self.assertIn(exit_sensor_config_dict, self.config.get_sensor_configs(car_park_name))

    def test_car_park2(self):
        """Test Parsing Configuration of 'carpark2'"""
        car_park_name = "carpark2"
        self.assertIn(car_park_name, self.config.get_car_park_names())

        self.assertEqual(len(self.config._get_common_config(car_park_name).keys()), 3)
        self.assertEqual(self.config._get_common_config(car_park_name)["topic-root"], car_park_name)
        self.assertEqual(self.config._get_common_config(car_park_name)["host"], "localhost")
        self.assertEqual(self.config._get_common_config(car_park_name)["port"], 1883)

        for sensor_config in self.config.get_sensor_configs(car_park_name):
            self.assertIn(sensor_config["name"], ["sensor1", "sensor2"])
            self.assertEqual(sensor_config["location"], "L250")
            self.assertEqual(sensor_config["host"], "localhost")
            self.assertEqual(sensor_config["port"], 1883)
            self.assertEqual(sensor_config["topic-root"], car_park_name)
            self.assertIn(sensor_config["topic-qualifier"], ["entry", "exit"])

        car_park_config = self.config.get_car_park_config(car_park_name)
        self.assertEqual(car_park_config["name"], car_park_name)
        self.assertEqual(car_park_config["location"], "Jandurah Park")
        self.assertEqual(car_park_config["host"], "localhost")
        self.assertEqual(car_park_config["port"], 1883)
        self.assertEqual(car_park_config["topic-root"], car_park_name)
        self.assertRaises(KeyError, lambda: car_park_config["topic-qualifier"])
        self.assertEqual(car_park_config["total_bays"], 1)

        for display_config in self.config.get_display_configs(car_park_name):
            self.assertIn(display_config["name"], ["display1", "display2"])
            self.assertEqual(display_config["location"], "Jandurah Park")
            self.assertEqual(display_config["host"], "localhost")
            self.assertEqual(display_config["port"], 1883)
            self.assertEqual(display_config["topic-root"], car_park_name)
            self.assertEqual(display_config["topic-qualifier"], "na")

        self.assertEqual(self.config.create_car_park_display_topic(car_park_name),
                         "carpark2/Jandurah Park/carpark2/display")

        sensor_pub_topics = ["carpark2/L250/sensor1/entry",
                             "carpark2/L250/sensor2/exit"
                             ]
        for pub_topic in sensor_pub_topics:
            self.assertIn(pub_topic, self.config.get_sensor_pub_topics(car_park_name))

        entry_sensor_config_dict = self.config.get_sensor_config_dict(car_park_name, "sensor1", "entry")
        self.assertIn(entry_sensor_config_dict, self.config.get_sensor_configs(car_park_name))

        exit_sensor_config_dict = self.config.get_sensor_config_dict(car_park_name, "sensor2", "exit")
        self.assertIn(exit_sensor_config_dict, self.config.get_sensor_configs(car_park_name))


if __name__ == "__main__":
    unittest.main()
