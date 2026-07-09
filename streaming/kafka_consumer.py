from kafka import KafkaConsumer
import json


class SensorDataConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='sensor-data', group_id='ml-pipeline'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

    def consume_stream(self):
        """Yield messages from Kafka topic"""
        for message in self.consumer:
            yield message.value

    def close(self):
        self.consumer.close()
