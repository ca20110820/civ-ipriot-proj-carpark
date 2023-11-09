from pathlib import Path

from smartpark.config import Config
from smartpark.sensor import RandomDetector


if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")
    config = Config(config_path)

    detector = RandomDetector(config.get_sensor_config_dict("carpark", "sensor1", "entry"),
                              config.get_sensor_config_dict("carpark", "sensor2", "exit"),
                              lower_bound=20, upper_bound=30, enter_prb=0.6,
                              min_time_interval=0.04, max_time_interval=0.5
                              )

    detector.start_sensing()
