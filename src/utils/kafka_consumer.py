import json
import threading
import time

from kafka import KafkaConsumer

from src.extensions import db
from src.models.kafka_log import KafkaLog


def _decode_message(raw_value):
    decoded = raw_value.decode("utf-8", errors="replace")
    try:
        # Se normaliza JSON para guardar formato consistente en BD.
        return json.dumps(json.loads(decoded), ensure_ascii=False)
    except json.JSONDecodeError:
        return decoded


def consume_forever(app):
    topic = app.config["KAFKA_TOPIC_ALERTAS"]
    bootstrap_servers = app.config["KAFKA_BOOTSTRAP_SERVERS"]
    group_id = app.config["KAFKA_GROUP_ID"]
    auto_offset_reset = app.config["KAFKA_AUTO_OFFSET_RESET"]

    while True:
        consumer = None
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda message: message,
            )
            print(
                f"[kafka-consumer] Conectado al topic '{topic}' en '{bootstrap_servers}'",
                flush=True,
            )

            for message in consumer:
                with app.app_context():
                    entry = KafkaLog(
                        topic=message.topic,
                        message_key=(
                            message.key.decode("utf-8", errors="replace")
                            if message.key
                            else None
                        ),
                        payload=_decode_message(message.value),
                        partition=message.partition,
                        offset=message.offset,
                    )
                    db.session.add(entry)
                    db.session.commit()
                    print(
                        f"[kafka-consumer] Mensaje persistido topic={message.topic} offset={message.offset}",
                        flush=True,
                    )
        except Exception as ex:
            print(f"[kafka-consumer] Error: {ex}", flush=True)
            time.sleep(5)
        finally:
            if consumer:
                consumer.close()


def start_kafka_consumer(app):
    if not app.config.get("KAFKA_CONSUMER_ENABLED", False):
        app.logger.info("Kafka consumer deshabilitado por configuracion.")
        return

    consumer_thread = threading.Thread(
        target=consume_forever,
        args=(app,),
        name="kafka-consumer-thread",
        daemon=True,
    )
    consumer_thread.start()
