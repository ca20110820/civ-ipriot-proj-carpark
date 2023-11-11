from pathlib import Path

from smartpark.config import Config
from smartpark.display import TkGUIDisplay

if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")
    config = Config(config_path)

    display_config = config.get_display_configs("carpark")[0]

    display = TkGUIDisplay(display_config,
                           config.create_car_park_display_topic("carpark"),
                           window_title=display_config["location"]
                           )

    display.start_listening()
