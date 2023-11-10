## How to Run the Samples
Assume you have Python 3.10+ in your local machine with pip & virtualenv. Make sure you have 
[eclipse mosquitto](https://mosquitto.org/) installed and running.

### Run Mosquitto Broker
Open a Shell and run `mosquitto -v` where `-v` is for verbose logging.

### Setup and Running a Sample
1. `git clone -b approach-1-simple-mqtt https://github.com/ca20110820/civ-ipriot-proj-carpark.git`
2. `cd civ-ipriot-proj-carpark/`
3. `python -m venv venv`
4. Activate `venv`
5. `python -m pip install -e .`
6. Examples:
   - `python samples_and_snippets/sample_tk_gui/run_the_sample.py`
   - `python samples_and_snippets/sample_random_detector/run_the_sample.py`
