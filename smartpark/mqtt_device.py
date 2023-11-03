import paho.mqtt.client as paho


class MqttDevice:
    def __init__(self, config: dict, keepalive: int = 65535, *args, **kwargs):
        self.topic_root = config["topic-root"]
        self.location = config["location"]
        self.name = config["name"]
        self.topic_qualifier = config["topic-qualifier"]
        self.host = config["host"]
        self.port = config["port"]

        self.client: paho.Client = paho.Client(*args, **kwargs)
        self.client.connect(self.host, self.port, keepalive=keepalive)

    @property
    def topic_address(self) -> str:
        # Default Topic: <topic-root>/<location>/<name>/<topic-qualifier>
        return f"{self.topic_root}/{self.location}/{self.name}/{self.topic_qualifier}"

    def create_topic_address(self, custom_location: str, custom_name: str, custom_topic_qualifier: str):
        # Note: Topic Root cannot be changed.
        return f"{self.topic_root}/{custom_location}/{custom_name}/{custom_topic_qualifier}"

    def create_topic_qualifier(self, custom_topic_qualifier: str):
        return f"{self.topic_root}/{self.location}/{self.name}/{custom_topic_qualifier}"
