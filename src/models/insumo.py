from src.extensions import db


class Insumo(db.Model):
    __tablename__ = "insumos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(50))
    unidad_medida = db.Column(db.String(20))
    stock_actual = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "unidad_medida": self.unidad_medida,
            "stock_actual": float(self.stock_actual) if self.stock_actual is not None else 0.0,
            "proveedor_id": self.proveedor_id,
        }
