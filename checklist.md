|  #  | Requirement Category    | Task Description                                                                     | Checkbox |
|:---:|-------------------------|--------------------------------------------------------------------------------------|:--------:|
|  1  | General Requirements    | Code follows PEP 8 style guide                                                       |   [x]    |
|  2  |                         | Code is documented with comments                                                     |   [x]    |
|  3  |                         | Unit tests are created                                                               |   [x]    |
|     | MQTT Configuration      | **CarPark Class:**                                                                   |          |
|  4  |                         | Subscribes to MQTT topics                                                            |   [x]    |
|  5  |                         | Publishes MQTT messages                                                              |   [x]    |
|  6  |                         | Can parse messages from sensor                                                       |   [x]    |
|  7  |                         | Sends MQTT message that includes available bays, temperature                         |   [x]    |
|     |                         | **Sensor Class:**                                                                    |          |
|  8  |                         | Publishes MQTT messages                                                              |   [x]    |
|  9  |                         | Sends MQTT messages that include temperature, time, and entry/exit                   |   [x]    |
|     |                         | **Display Class:**                                                                   |          |
| 10  |                         | Subscribes to MQTT topics                                                            |   [x]    |
| 11  |                         | Parses MQTT messages from car park                                                   |   [x]    |
|     | Configuration File      | **CarPark Class:**                                                                   |          |
| 12  | Management              | Reads initial configuration from a file                                              |   [x]    |
| 13  |                         | Writes available bays to a configuration class                                       |   [x]    |
|     |                         | **Sensor Class:**                                                                    |          |
| 14  |                         | Reads initial configuration from a file                                              |   [x]    |
|     |                         | **Display Class:**                                                                   |          |
| 15  |                         | Reads initial configuration from a file                                              |   [x]    |
| 16  | Testing Requirements    | At least one test case for CarPark Class                                             |   [x]    |
| 17  |                         | At least one test case for Sensor or Display Class                                   |   [x]    |
| 18  | Additional Requirements | Invent your own protocol for transmitting information; JSON is recommended           |   [x]    |
| 19  | Git Requirements        | Forked the original project repository                                               |   [x]    |
| 20  |                         | At least 3 local commits and 3 remote commits with reasonable messages               |   [x]    |
| 21  |                         | Worked in a feature branch and merged the feature branch                             |   [x]    |
| 22  |                         | Both origin and local copy are synchronized at time of submission                    |   [x]    |
| 23  | Submission Guidelines   | Code files organized in coherent folder structure                                    |   [x]    |
| 24  |                         | Unit tests are submitted alongside the main code                                     |   [x]    |
| 25  |                         | Configuration files used for testing are included in the submission                  |   [x]    |
| 26  |                         | Submitted a zip file containing your code (excluding `venv/`, but including `.git/`) |   [x]    |
| 27  |                         | Ensure your lecturer has access to your GitHub repository                            |   [x]    |
| 28  |                         | Completed the project journal                                                        |   [x]    |

Please use this updated table as a comprehensive guide for the project requirements. Ensure each task is completed and
checked off before submitting your project for assessment.
Note there is a high-level (less detailed) checklist in the project journal, which is also used for grading.
While there are a lot of items here, most items are small and can be addressed with 1-3 lines of code.

### Student Notes/Remarks

- In #9; Sensors only transmits temperature and Enter/Exit. The Time is created from Car when it entered or exited the
  car park. And this Entered/Exited Time is passed on to `CarPark`.
- In #18; When transmitting messages, we simply use strings and the data or content from a message is separated by `,`
  or `;`. Also note that we created methods in `Car` so that the properties/fields can be transmitted over a network and
  re-instantiated in other MQTT Device (e.g. from `Sensor` to `CarPark`).
- `Config` class acts more of a parser for the toml configuration file and has methods to extract configurations as 
  dictionaries to instantiate objects such as `Sensor`, `CarPark`, and `Display`. It also contains methods for extracting
  topics for subscriptions and publications.