from pathlib import Path

from smartpark.config import Config
from smartpark.display import TkGUIDisplay, create_display_from_config_path

if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")
    config = Config(config_path)

    display = create_display_from_config_path(TkGUIDisplay,
                                              config_path,
                                              "carpark",
                                              "display1",
                                              window_title=config.get_car_park_config("carpark")["location"]
                                              )

    display.start_listening()
