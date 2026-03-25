from src.extensions import db


class Cultivo(db.Model):
    __tablename__ = "cultivos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120), nullable=False)
    ubicacion = db.Column(db.String(150))
    fecha_inicio = db.Column(db.Date)
    estado = db.Column(db.String(50))
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "estado": self.estado,
            "responsable_id": self.responsable_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
