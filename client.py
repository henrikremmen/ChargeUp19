import requests
import paho.mqtt.client as mqtt


class BasicClient:

    def __init__(self, ip):
        """HTTPS client framework"""
        self.server_url = "http://" + str(ip) + ":8000" 
        

    def send_get_request(self, endpoint=""):
        """Sends get requests to server with specified endpoint, might not use"""
        response = requests.get(self._full_url(endpoint))
        return response.text
    

    def send_post_request(self, data):
        """Sends post request"""
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.server_url, data=data, headers=headers)
        return response
    

    def _full_url(self, endpoint):
        """Gets full url"""
        return f"{self.server_url}/{endpoint}"
    

class MQTTClient:
    
    def __init__(self):
        """MQTT client and it's methods"""
        self.broker_address = "test.mosquitto.org" # This is the public broker we are using
        self.port = 1883
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

        self.last_messages = {} # Initialize last message dictionar

        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message


    def on_connect(self, client, userdata, flags, rc):
        """Prints out message on connect"""
        print(f"Connected to MQTT Broker: {self.broker_address} with result code {rc}")


    def on_message(self, client, userdata, msg):
        """Prints recieved messages"""
        print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}'")
        # Update last message for this topic
        self.last_messages[msg.topic] = msg.payload.decode()


    def connect(self):
        """Connects to broker"""
        self.client.connect(self.broker_address, self.port, 60)
        self.client.loop_start()


    def publish(self, topic, message):
        """Publishes message on topic"""
        self.client.publish(topic, message)
        print(f"Sent '{message}' to topic '{topic}'")


    def subscribe(self, topic):
        """Subscribes to topic"""
        self.client.subscribe(topic)
        print(f"Subscribed to topic '{topic}'")


    def disconnect(self):
        """Disconnects from server"""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT Broker.")


    def get_last_message(self, topic):
        """Returns last message recieved on topic"""
        return self.last_messages.get(topic, None)
