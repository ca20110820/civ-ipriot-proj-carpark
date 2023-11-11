from pathlib import Path

from smartpark.config import Config
from smartpark.sensor import RandomDetector, TkDetector


if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")
    config = Config(config_path)

    detector = TkDetector(config.get_sensor_config_dict("carpark", "sensor1", "entry"),
                          config.get_sensor_config_dict("carpark", "sensor2", "exit")
                          )

    detector.start_sensing()
