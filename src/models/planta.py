from src.extensions import db


class Planta(db.Model):
    __tablename__ = "plantas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lote_id = db.Column(db.Integer, db.ForeignKey("lotes.id"), nullable=False)
    codigo = db.Column(db.String(100), unique=True)
    fecha_germinacion = db.Column(db.Date)
    estado = db.Column(db.String(50))
    estado_id = db.Column(db.Integer, db.ForeignKey("estados.id"))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "lote_id": self.lote_id,
            "codigo": self.codigo,
            "fecha_germinacion": self.fecha_germinacion.isoformat() if self.fecha_germinacion else None,
            "estado": self.estado,
            "estado_id": self.estado_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
