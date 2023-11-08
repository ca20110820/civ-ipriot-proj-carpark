import concurrent.futures
import subprocess
import os
import sys

from smartpark.project_paths import SMART_PARK_DIR


def run_script(script_name):
    subprocess.run([sys.executable, SMART_PARK_DIR / script_name])


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(run_script, "sensor.py")
        executor.submit(run_script, "carpark.py")
        executor.submit(run_script, "display.py")

    print("Closing Car Park Simulation Program")
