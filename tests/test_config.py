import unittest

from smartpark.config import Config
from smartpark.project_paths import PROJECT_ROOT_DIR


class TestConfigParsing(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config(PROJECT_ROOT_DIR / 'tests' / 'sample_config.toml')
        self.car_park_name = "carpark1"

    def test_get_car_park_names(self):
        car_park_names = self.config.get_car_park_names()

        self.assertEqual(len(car_park_names), 2)
        self.assertIn("carpark1", car_park_names)
        self.assertIn("carpark2", car_park_names)

    def test_get_sensor_configs(self):
        sensor_configs = self.config.get_sensor_configs(self.car_park_name)

        self.assertEqual(len(sensor_configs), 2)
        self.assertIn("sensor1", [sensor_config['name'] for sensor_config in sensor_configs])
        self.assertIn("sensor2", [sensor_config['name'] for sensor_config in sensor_configs])

        for sensor_config in sensor_configs:
            self.assertEqual(len(sensor_config.keys()), 6)
            self.assertIn('topic-root', sensor_config.keys())
            self.assertIn('host', sensor_config.keys())
            self.assertIn('port', sensor_config.keys())
            self.assertIn('name', sensor_config.keys())
            self.assertIn('topic-qualifier', sensor_config.keys())
            self.assertIn('location', sensor_config.keys())

            if sensor_config["name"] == "sensor1":
                self.assertEqual(sensor_config["topic-root"], 'carpark1')
                self.assertEqual(sensor_config["host"], 'localhost')
                self.assertEqual(sensor_config["port"], 1883)
                self.assertEqual(sensor_config["name"], 'sensor1')
                self.assertEqual(sensor_config["topic-qualifier"], 'entry')
                self.assertEqual(sensor_config["location"], 'L306')
            elif sensor_config["name"] == "sensor2":
                self.assertEqual(sensor_config["topic-root"], 'carpark1')
                self.assertEqual(sensor_config["host"], 'localhost')
                self.assertEqual(sensor_config["port"], 1883)
                self.assertEqual(sensor_config["name"], 'sensor2')
                self.assertEqual(sensor_config["topic-qualifier"], 'exit')
                self.assertEqual(sensor_config["location"], 'L306')

    def test_get_car_park_config(self):
        car_park_config = self.config.get_car_park_config(self.car_park_name)
        self.assertEqual(len(car_park_config.keys()), 6)
        self.assertEqual(car_park_config["topic-root"], 'carpark1')
        self.assertEqual(car_park_config["host"], 'localhost')
        self.assertEqual(car_park_config["port"], 1883)
        self.assertEqual(car_park_config["name"], 'carpark1')
        self.assertEqual(car_park_config["total_bays"], 5)
        self.assertEqual(car_park_config["location"], 'Moondaloop Park')

        car_park_config = self.config.get_car_park_config('carpark2')
        self.assertEqual(len(car_park_config.keys()), 6)
        self.assertEqual(car_park_config["topic-root"], 'carpark2')
        self.assertEqual(car_park_config["host"], 'localhost')
        self.assertEqual(car_park_config["port"], 1883)
        self.assertEqual(car_park_config["name"], 'carpark2')
        self.assertEqual(car_park_config["total_bays"], 1)
        self.assertEqual(car_park_config["location"], 'Jandurah Park')

    def test_get_display_configs(self):
        display_configs = self.config.get_display_configs(self.car_park_name)

        self.assertEqual(len(display_configs), 1)
        self.assertIn("display1", [display_config['name'] for display_config in display_configs])

        for display_config in display_configs:
            self.assertEqual(len(display_config.keys()), 6)
            self.assertIn('topic-root', display_config.keys())
            self.assertIn('host', display_config.keys())
            self.assertIn('port', display_config.keys())
            self.assertIn('name', display_config.keys())
            self.assertIn('topic-qualifier', display_config.keys())
            self.assertIn('location', display_config.keys())

            self.assertEqual(display_config["topic-root"], 'carpark1')
            self.assertEqual(display_config["host"], 'localhost')
            self.assertEqual(display_config["port"], 1883)
            self.assertEqual(display_config["name"], 'display1')
            self.assertEqual(display_config["topic-qualifier"], 'na')
            self.assertEqual(display_config["location"], 'Moondaloop Park')

    def test_get_sensor_pub_topics(self):
        sensor_pub_topics = self.config.get_sensor_pub_topics(self.car_park_name)

        self.assertEqual(len(sensor_pub_topics), 2)
        self.assertIn('carpark1/L306/sensor1/entry', sensor_pub_topics)
        self.assertIn('carpark1/L306/sensor2/exit', sensor_pub_topics)

    def test_create_car_park_display_topic(self):
        display_topic = self.config.create_car_park_display_topic(self.car_park_name)
        self.assertEqual(display_topic, 'carpark1/Moondaloop Park/carpark1/display')

        display_topic = self.config.create_car_park_display_topic('carpark2')
        self.assertEqual(display_topic, 'carpark2/Jandurah Park/carpark2/display')

    @unittest.skip("Skip")
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

    @unittest.skip("Skip")
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
