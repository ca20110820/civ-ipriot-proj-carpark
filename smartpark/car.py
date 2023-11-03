from datetime import datetime
import time
import random
import string
import json


class Car:
    """
    Car Data:
    - license_plate
    - car_model
    - entry_time
    - entry_temperature
    - exit_time
    - exit_temperature
    """
    def __init__(self, license_plate: str, car_model: str):
        self.license_plate = license_plate
        self.car_model = car_model
        self.entry_time: datetime | None = None  # .strftime("%Y-%m-%d %H:%M:%S")
        self.entry_temperature: float | int | None = None

        self._is_parked: bool = False  # When car is instantiated (i.e. Entered) it not parked by default

        self.exit_time: datetime | None = None
        self.exit_temperature: float | int | None = None

    @property
    def is_parked(self):
        return self._is_parked

    @classmethod
    def from_json(cls, car_as_json: str):
        """Contruct class from JSON String"""
        car_dict: dict = json.loads(car_as_json)

        for k, v in car_dict.items():
            if k in ["license_plate", "car_model"]:
                continue
            elif k in ["entry_time", "exit_time"]:
                if v is None:
                    continue
                else:
                    car_dict[k] = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            elif k in ["entry_temperature", "exit_temperature"]:
                if v is None:
                    continue
                else:
                    car_dict[k] = float(v)
            elif k == "is_parked":
                assert isinstance(v, bool), f"{k} is not bool!"
                continue
            else:
                raise KeyError()

        car = cls(car_dict["license_plate"], car_dict["car_model"])
        car.entry_time = car_dict["entry_time"]
        car.exit_time = car_dict["exit_time"]
        car.entry_temperature = car_dict["entry_temperature"]
        car.exit_temperature = car_dict["exit_temperature"]
        car._is_parked = car_dict["is_parked"]

        return car

    @classmethod
    def from_csv(cls, car_as_csv: str):
        car_str_list = car_as_csv.split(",")

        for i in range(len(car_str_list)):
            if i in [0, 1]:
                continue
            elif i in [2, 3]:
                temp_val = None if car_str_list[i] == "null" else datetime.strptime(car_str_list[i],
                                                                                    "%Y-%m-%d %H:%M:%S")
                car_str_list[i] = temp_val
            elif i in [4, 5]:
                temp_val = None if car_str_list[i] == "null" else float(car_str_list[i])
                car_str_list[i] = temp_val
            elif i == 6:
                car_str_list[i] = True if car_str_list[6] == "True" else False
            else:
                raise KeyError()

        car = cls(car_str_list[0], car_str_list[1])
        car.entry_time = car_str_list[2]
        car.exit_time = car_str_list[3]
        car.entry_temperature = car_str_list[4]
        car.exit_temperature = car_str_list[5]
        car._is_parked = car_str_list[6]

        return car

    def __str__(self):
        return f"{self.license_plate} - {self.car_model}"

    def car_parked(self):
        self._is_parked = True

    def car_unparked(self):
        self._is_parked = False

    def entered_car_park(self, temperature: float):
        # Warn: Make sure to check if there is available bay before changing parked state
        self.entry_time = datetime.now()
        self.entry_temperature = float(temperature)

    def exited_car_park(self, temperature: float):
        self.car_unparked()  # Update the State of Car to Un-parked
        self.exit_time = datetime.now()
        self.exit_temperature = float(temperature)

    def to_csv_format(self):
        item_list = [self.license_plate,
                     self.car_model,
                     self.entry_time.strftime("%Y-%m-%d %H:%M:%S") if self.entry_time is not None else "null",
                     self.exit_time.strftime("%Y-%m-%d %H:%M:%S") if self.exit_time is not None else "null",
                     self.entry_temperature if self.entry_temperature is not None else "null",
                     self.exit_temperature if self.exit_temperature is not None else "null",
                     self._is_parked
                     ]

        item_list = [str(item) for item in item_list]

        return ",".join(item_list)

    def to_json_format(self, **kwargs):
        out_json = {"license_plate": self.license_plate,
                    "car_model": self.car_model,
                    "entry_time": self._get_datetime_as_str("entry_time"),
                    "exit_time": self._get_datetime_as_str("exit_time"),
                    "entry_temperature": self.entry_temperature,
                    "exit_temperature": self.exit_temperature,
                    "is_parked": self._is_parked
                    }

        return json.dumps(out_json, sort_keys=False, default=str, **kwargs)

    def _get_datetime_as_str(self, entry_or_exit: str) -> str | None:
        if entry_or_exit not in ["entry_time", "exit_time"]:
            raise ValueError("entry_or_exit must be 'entry_time' or 'exit_time'")

        entry_or_exit_time = self.entry_time if entry_or_exit == "entry_time" else self.exit_time

        if entry_or_exit_time is None:
            return None

        return entry_or_exit_time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def generate_random_license_plate():
        format_string = random.choice(["LLL-NNN", "NLL-NNN", "NLLL-NNN", "LL-NNNN", "TAXI-NNNN", "LLL-NNNN"])

        letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(format_string.count("L")))
        numbers = ''.join(random.choice(string.digits) for _ in range(format_string.count("N")))

        license_plate = format_string
        for char in format_string:
            if char == "L":
                license_plate = license_plate.replace(char, letters[0], 1)
                letters = letters[1:]
            elif char == "N":
                license_plate = license_plate.replace(char, numbers[0], 1)
                numbers = numbers[1:]

        return license_plate

    @staticmethod
    def generate_random_car_model(model_list):
        return random.choice(model_list)

    @classmethod
    def generate_random_car(cls, car_model_list):
        rnd_license_plate = cls.generate_random_license_plate()
        rnd_car_model = cls.generate_random_car_model(car_model_list)
        return cls(rnd_license_plate, rnd_car_model)


if __name__ == "__main__":
    # play_car = Car("AAAA", "ModelA")
    play_car = Car.generate_random_car(["AAA", "BBB", "CCC"])
    play_car.entered_car_park(30)
    play_car.car_parked()
    print(play_car.to_json_format(indent=4))
    play_car_json = play_car.to_json_format()
    time.sleep(1)
    reborn_car = Car.from_json(play_car_json)
    reborn_car.car_unparked()
    reborn_car.exited_car_park(31)
    print(reborn_car.to_json_format(indent=4))

    print(Car.from_csv(reborn_car.to_csv_format()).to_json_format(indent=4))
