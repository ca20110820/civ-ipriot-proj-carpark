| Requirement Category    | Task Description                                                                     | Checkbox |
|-------------------------|--------------------------------------------------------------------------------------|:--------:|
| General Requirements    | Code follows PEP 8 style guide                                                       |   [x]    |
|                         | Code is documented with comments                                                     |   [x]    |
|                         | Unit tests are created                                                               |   [x]    |
| MQTT Configuration      | **CarPark Class:**                                                                   |          |
|                         | Subscribes to MQTT topics                                                            |   [x]    |
|                         | Publishes MQTT messages                                                              |   [x]    |
|                         | Can parse messages from sensor                                                       |   [x]    |
|                         | Sends MQTT message that includes available bays, temperature                         |   [x]    |
|                         | **Sensor Class:**                                                                    |          |
|                         | Publishes MQTT messages                                                              |   [x]    |
|                         | Sends MQTT messages that include temperature, time, and entry/exit                   |   [x]    |
|                         | **Display Class:**                                                                   |          |
|                         | Subscribes to MQTT topics                                                            |   [x]    |
|                         | Parses MQTT messages from car park                                                   |   [x]    |
| Configuration File      | **CarPark Class:**                                                                   |          |
| Management              | Reads initial configuration from a file                                              |   [x]    |
|                         | Writes available bays to a configuration class                                       |   [x]    |
|                         | **Sensor Class:**                                                                    |          |
|                         | Reads initial configuration from a file                                              |   [x]    |
|                         | **Display Class:**                                                                   |          |
|                         | Reads initial configuration from a file                                              |   [x]    |
| Testing Requirements    | At least one test case for CarPark Class                                             |   [x]    |
|                         | At least one test case for Sensor or Display Class                                   |   [x]    |
| Additional Requirements | Invent your own protocol for transmitting information; JSON is recommended           |   [x]    |
| Git Requirements        | Forked the original project repository                                               |   [x]    |
|                         | At least 3 local commits and 3 remote commits with reasonable messages               |   [x]    |
|                         | Worked in a feature branch and merged the feature branch                             |   [x]    |
|                         | Both origin and local copy are synchronized at time of submission                    |   [x]    |
| Submission Guidelines   | Code files organized in coherent folder structure                                    |   [x]    |
|                         | Unit tests are submitted alongside the main code                                     |   [x]    |
|                         | Configuration files used for testing are included in the submission                  |   [x]    |
|                         | Submitted a zip file containing your code (excluding `venv/`, but including `.git/`) |   [x]    |
|                         | Ensure your lecturer has access to your GitHub repository                            |   [x]    |
|                         | Completed the project journal                                                        |   [x]    |

Please use this updated table as a comprehensive guide for the project requirements. Ensure each task is completed and
checked off before submitting your project for assessment.
Note there is a high-level (less detailed) checklist in the project journal, which is also used for grading.
While there are a lot of items here, most items are small and can be addressed with 1-3 lines of code.
