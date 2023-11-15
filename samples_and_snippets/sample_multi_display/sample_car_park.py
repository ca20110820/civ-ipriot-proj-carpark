from pathlib import Path

from smartpark.carpark import SimulatedCarPark, create_car_park_from_config_path

if __name__ == "__main__":
    curr_dir = Path(__file__).resolve().parent
    config_path = str(curr_dir / "config.toml")

    car_park = create_car_park_from_config_path(SimulatedCarPark, config_path, "carpark")

    car_park.start_serving()
