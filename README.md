# IPRIoT Project: Simulated Workplace Scenario

A simulated workplace environment where students must demonstrate OO skills by interpreting and interacting with modern software requirements.

## Installation and Running - ca20110820
Assume you have Python 3.10+ in your local machine with pip & virtualenv. Make sure you have 
[eclipse mosquitto](https://mosquitto.org/) installed and running.

### Run Mosquitto Broker
Open a Shell and run `mosquitto -v` where `-v` is for verbose logging.

### Setup and Running
1. `git clone -b approach-1-simple-mqtt https://github.com/ca20110820/civ-ipriot-proj-carpark.git`
2. `cd civ-ipriot-proj-carpark/`
3. `python -m venv venv`
4. Activate `venv`
5. `python -m pip install -e .`
6. Run `python smartpark`

### Running Samples
Do the same steps from 1-5 in the previous section. Run using the following
examples:
   - `python samples_and_snippets/sample_tk_gui/run_the_sample.py`
   - `python samples_and_snippets/sample_random_detector/run_the_sample.py`
   - `python samples_and_snippets/sample_multi_display/run_the_sample.py`


## Scenario

You are working as a junior software innovation engineer for the City of Moondalup in the Department of Transport. The department wants to upgrade a few public parking spaces by providing information about the number of available parking spots in near real time for each one. The parking lots in question do not have boom gates.

## Resources

For this project, you will be using foundational agile practices:

- An emphasis on collaboration and communication
- Small rapid iterations
- Minimal, user-focused documentation (how does this help the user?)

However, because in this simulation you may have limited access to developers and customers. They have provided you with some documentation to help get you started:

```text
│
├── docs/
│   ├── requirements.md
│   └── high_level_design.md
```

- **`requirements.md`**: provides a brief agile specification for the project. Please note that unlike a typical agile specifications some requirements are not-user driven but are constraints needed to achieve competency in the unit.
- **`high_level_design`**: because you are a junior developer, the senior developer was asked to write a more detailed specification to help you achieve some of the more difficult aspects of this project.

## Getting started

To get started with this project fork and then clone this repository:

1. From the top right, press **Fork**. This creates a copy of the repository in your GitHub account.

2. After the forking process is complete, press the green **Code** button *on your forked repository*.

3. Copy the URL displayed under "Clone with HTTPS" by pressing the clipboard icon next to it.

4. You did copy **your** forked repository URL, **not** this repository's URL, right?

5. Open a terminal (Command Prompt or Git Bash on Windows, Terminal on macOS and Linux) on your local machine.

6. Navigate to the directory where you want to clone the repository by using the `cd` command. For example:

```bash
cd /path/to/your/directory
```

7. Clone the repository to your local machine by running the `git clone` command followed by the copied URL:

```bash
git clone https://github.com/your-username/civ-ipriot-proj-carpark.git
```

### Making local changes

1. Change to the cloned repository's directory:

```bash
cd civ-ipriot-proj-carpark
```

2.  Create a new branch for your local modifications by running:

```bash
git checkout -b your-new-branch-name
```

Now you can make local modifications to the project files. After you have made the desired changes, follow these steps to commit and push them:

1. Stage the modified files by running:

```bash
git add .
```

2. Commit the changes with a descriptive message:

```bash
git commit -m "Your commit message here"
```

3. Push the changes to your forked repository on GitHub:

```bash
git push origin your-new-branch-name
```

## Optional: Install this project as a module (makes imports easier!)

The `setup.py` file contains information about the project, its dependencies, and how to run the main script.

To install the SmartPark project as a module in development mode, follow these steps:

1. Open a terminal and navigate to the SmartPark project directory (the one containing `setup.py`). 
2. Ensure you have a virtual environment activated for the project. If not, you can create one using:

```bash
python3 -m venv .venv
```

Then activate the virtual environment:

- On Linux/macOS:

```bash
source .venv/bin/activate
```

- On Windows:

```bash
.venv\Scripts\activate
```

3. Install the SmartPark project in development mode using:

```bash
pip install -e .
```

This command installs the project in editable mode, which means any changes you make to the source code will be immediately reflected in the installed module.
