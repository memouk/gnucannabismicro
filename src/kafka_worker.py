from src.app import create_app
from src.utils.kafka_consumer import consume_forever


def main():
    print("[kafka-worker] Inicializando worker Kafka...", flush=True)
    app = create_app()
    print("[kafka-worker] Worker listo. Iniciando consumo...", flush=True)
    consume_forever(app)


if __name__ == "__main__":
    main()
