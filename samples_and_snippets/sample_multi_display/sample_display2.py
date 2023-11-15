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
                                              "display2",
                                              window_title=config.get_display_config_dict("carpark", "display2")[
                                                  "location"]
                                              )

    display.start_listening()
