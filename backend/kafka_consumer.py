from kafka import KafkaConsumer
import json
import sys
import time

# Define the topic to consume from and the Kafka broker(s)
topic_name = 'ipfix'
bootstrap_servers = ['kafka:9092']  # Internal Docker network address

try:
    # Create a KafkaConsumer instance
    print("Attempting to connect to Kafka...")
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        group_id='ipfix_consumer_group',  # Fixed group ID for better tracking
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=30000,  # Timeout after 30 seconds of no messages
        value_deserializer=lambda x: x  # Read raw messages first to debug format
    )

    print(f"Consumer started for topic '{topic_name}' in group")

    # Consume messages
    try:
        for message in consumer:
            print(f"Received message: Topic={message.topic}, Partition={message.partition}, Offset={message.offset}, Value={message.value}")
    except KeyboardInterrupt:
        print("Consumer stopped by user.")
    except Exception as e:
        print(f"Error consuming messages: {str(e)}")
    finally:
        consumer.close()
        print("Consumer closed.")
        
except Exception as e:
    print(f"Failed to connect to Kafka: {str(e)}")
    sys.exit(1)