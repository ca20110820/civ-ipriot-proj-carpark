from pathlib import Path

from smartpark.config import Config
from smartpark.carpark import SimulatedCarPark

if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")
    config = Config(config_path)

    car_park = SimulatedCarPark(config.get_car_park_config("carpark"))

    for sensor_top in config.get_sensor_pub_topics("carpark"):
        car_park.register_sensor_topic(sensor_top)

    car_park.start_serving()
