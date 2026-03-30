from src.extensions import db


class Lote(db.Model):
    __tablename__ = "lotes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cultivo_id = db.Column(db.Integer, db.ForeignKey("cultivos.id"), nullable=False)
    nombre = db.Column(db.String(120))
    fecha_siembra = db.Column(db.Date)
    estado = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "cultivo_id": self.cultivo_id,
            "nombre": self.nombre,
            "fecha_siembra": self.fecha_siembra.isoformat() if self.fecha_siembra else None,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
