from datetime import datetime

from src.extensions import db


class KafkaLog(db.Model):
    __tablename__ = "kafka_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(120), nullable=False)
    message_key = db.Column(db.String(255), nullable=True)
    payload = db.Column(db.Text, nullable=False)
    partition = db.Column(db.Integer, nullable=False)
    offset = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
