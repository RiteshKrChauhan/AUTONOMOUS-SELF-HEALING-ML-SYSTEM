from kafka import KafkaProducer
import json
import time


class SensorDataProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='sensor-data'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic

    def send_stream(self, df, delay=0.05):
        """Stream DataFrame rows to Kafka topic"""
        for _, row in df.iterrows():
            data = row.to_dict()
            self.producer.send(self.topic, value=data)
            time.sleep(delay)
        self.producer.flush()

    def close(self):
        self.producer.close()
