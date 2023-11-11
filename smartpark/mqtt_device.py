import paho.mqtt.client as paho


class MqttDevice:
    """Base Class for all MQTT Devices. This includes Sensor, CarPark, and Display.

    It Contains 6 attributes:
        - topic-root: str
        - location: str
        - name: str
        - topic-qualifier: str
        - host: str
        - port: int
    """
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
        """Default Topic Address"""
        # Default Topic: <topic-root>/<location>/<name>/<topic-qualifier>
        return f"{self.topic_root}/{self.location}/{self.name}/{self.topic_qualifier}"

    def create_topic_address(self, custom_location: str, custom_name: str, custom_topic_qualifier: str):
        """Create Custom Topic Address. Everything can be changed except the 'topic-root'."""
        # Note: Topic Root cannot be changed.
        return f"{self.topic_root}/{custom_location}/{custom_name}/{custom_topic_qualifier}"

    def create_topic_qualifier(self, custom_topic_qualifier: str):
        """Create Custom 'topic-qualifier'."""
        return f"{self.topic_root}/{self.location}/{self.name}/{custom_topic_qualifier}"
