import json
import paho.mqtt.client as mqtt
import threading
import types
import time

class MQTTManager():    
    def __init__(self, server_url, server_port=1883, client_id=None, heart_beat_time=60):
        self.server_url = server_url
        self.server_port = server_port
        self.client_id = client_id if client_id else str(int(time.time() * 1000))
        print(self.client_id)
        self.heart_beat_time = heart_beat_time
        self.mqttc = mqtt.Client(client_id=self.client_id)
        self.callbacks = {}
        self.lock = threading.Lock()  # 添加一个锁
        self.connect_client()

    def connect_client(self):
        self.mqttc.will_set('/topic/' + self.client_id, '', retain=True)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_log = self.on_log
        self.mqttc.connect(self.server_url, self.server_port, self.heart_beat_time)
        threading.Thread(target=self.mqttc.loop_forever).start()

    def topic_callback(self, topic, func):
        with self.lock:
            print(f'self.client_id: {self.client_id}, topic: {topic}')
            self.callbacks[topic] = func
            self.mqttc.subscribe(topic)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_message(self, client, userdata, message):
        topic = message.topic
        with self.lock:
            if topic in self.callbacks:
                thread = threading.Thread(target=self.callbacks[topic], args=(self.client_id, message,), daemon=True)
                thread.start()

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected")   

    def on_log(self, client, userdata, level, buf):
        # print(f'on_log: {buf}, client_id: {self.client_id}')
        pass

class MQTTManagerGroup():
    def __init__(self, server_info):
        self.managers = []

        for info in server_info:
            manager = MQTTManager(server_url=info['server_url'], client_id=info['client_id'])
            self.managers.append(manager)

    def topic_callback(self, topic):
        def decorator(f):
            for manager in self.managers:
                print(f'self.client_id: {manager.client_id}, topic: {topic}')
                manager.topic_callback(topic, f)  # 现在你可以直接传递回调函数
            return f
        return decorator
    
    def publish(self, client_id, topic, payload):
        for manager in self.managers:
            if manager.client_id == client_id:
                manager.mqttc.publish(topic, json.dumps(payload))
                return
        print(f"No client with id {client_id} found.")


if __name__ == '__main__':
    server_info = [
        {
            "server_url": "10.10.0.101",
            "client_id": "10.10.0.101",
        },
        {
            "server_url": "10.10.0.195",
            "client_id": "10.10.0.195",
        }
    ]
    group = MQTTManagerGroup(server_info)

    # 使用装饰器定义回调
    @group.topic_callback('/get_speed_response')
    def handle_message_1(client_id, message):
        json_str = message.payload.decode()
        data = json.loads(json_str)  # 假设消息总是JSON格式
        print(f"Received message from {client_id}: {data}")
        
    # 使用publish方法发布消息
    while True:
        time.sleep(1)
        group.publish("10.10.0.101", "/test", {"speed": 50})
        group.publish("10.10.0.195", "/test", {"speed": 75})