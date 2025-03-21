import os

from mx_stream_core.infrastructure.kafka import create_kafka_topic_name


class KafkaUtil:
    @staticmethod
    def get_kafka_bootstrap_server():
        return os.getenv('KAFKA_HOST', 'kafka:9092')

    @staticmethod
    def create_ingestor_topic(entity: str):
        return create_kafka_topic_name('ingestor', entity)

    @staticmethod
    def create_aggregate_topic(entity: str):
        return create_kafka_topic_name('aggregate', entity)

    @staticmethod
    def create_transformation_topic(entity: str):
        return create_kafka_topic_name('transformation', entity)

    @staticmethod
    def create_cleaning_topic(entity: str):
        return create_kafka_topic_name('cleaning', entity)

    @staticmethod
    def create_customize_topic(entity: str):
        return create_kafka_topic_name('unification', entity)
