"""
OPTIONAL: Kafka Integration Example

If you want to use Kafka instead of the simple stream_data() generator,
replace the streaming loop in main.py with this:
"""

from streaming.kafka_consumer import SensorDataConsumer

# Replace this line in main.py:
# for i, data in enumerate(stream_data(stream_df.head(200))):

# With this:
consumer = SensorDataConsumer(
    bootstrap_servers='localhost:9092',
    topic='sensor-data'
)

for i, data in enumerate(consumer.consume_stream()):
    # ... rest of your pipeline code stays the same
    pass

consumer.close()

# To send data to Kafka, use:
from streaming.kafka_producer import SensorDataProducer

producer = SensorDataProducer(
    bootstrap_servers='localhost:9092',
    topic='sensor-data'
)
producer.send_stream(stream_df.head(200))
producer.close()
