import concurrent.futures
import subprocess
import os
import sys


def run_script(script_name):
    file_dir = os.path.dirname(__file__)
    subprocess.run([sys.executable, os.path.join(file_dir, script_name)])


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(run_script, "sample_detector.py")
        executor.submit(run_script, "sample_car_park.py")
        executor.submit(run_script, "sample_display1.py")
        executor.submit(run_script, "sample_display2.py")

    print("Closing Car Park Simulation Program")
