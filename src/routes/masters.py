from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from src.extensions import db
from src.models.cultivo import Cultivo
from src.models.estado import Estado
from src.models.insumo import Insumo
from src.models.lote import Lote
from src.models.planta import Planta
from src.models.proveedor import Proveedor
from src.models.user import User
from src.utils.auth import requires_auth

masters_bp = Blueprint("masters", __name__)


def _parse_iso_date(value, field_name):
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"Formato invalido para {field_name}. Usa YYYY-MM-DD.")


def _bad_request(message):
    return jsonify({"error": message}), 400


def _to_int_or_none(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError("Debe ser un numero entero.")


def _validate_fk(model, value, field_name):
    if value is None:
        return None
    if not db.session.get(model, value):
        raise ValueError(f"{field_name} no existe.")
    return value


def _resolve_estado_id(payload, required=False):
    if "estado_id" in payload:
        estado_id = _to_int_or_none(payload.get("estado_id"))
        if required and estado_id is None:
            raise ValueError("Campo requerido faltante: estado_id")
        return _validate_fk(Estado, estado_id, "estado_id")

    estado_nombre = (payload.get("estado") or "").strip().upper()
    if estado_nombre:
        estado = Estado.query.filter(db.func.upper(Estado.nombre) == estado_nombre).first()
        if not estado:
            estado = Estado(nombre=estado_nombre, descripcion="Estado creado desde formulario")
            db.session.add(estado)
            db.session.flush()
        return estado.id

    if required:
        raise ValueError("Campo requerido faltante: estado_id")
    return None


@masters_bp.get("/estados")
@requires_auth
def list_estados(_jwt_payload):
    data = Estado.query.order_by(Estado.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/estados/<int:item_id>")
@requires_auth
def get_estado(_jwt_payload, item_id):
    item = db.session.get(Estado, item_id)
    if not item:
        return jsonify({"error": "Estado no encontrado"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/estados")
@requires_auth
def create_estado(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    nombre = (payload.get("nombre") or "").strip().upper()
    if not nombre:
        return _bad_request("Campo requerido faltante: nombre")

    item = Estado(nombre=nombre, descripcion=payload.get("descripcion"))
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El estado ya existe"}), 409
    return jsonify(item.to_dict()), 201


@masters_bp.put("/estados/<int:item_id>")
@requires_auth
def update_estado(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Estado, item_id)
    if not item:
        return jsonify({"error": "Estado no encontrado"}), 404

    if "nombre" in payload:
        nombre = (payload.get("nombre") or "").strip().upper()
        if not nombre:
            return _bad_request("Campo requerido faltante: nombre")
        item.nombre = nombre
    item.descripcion = payload.get("descripcion", item.descripcion)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Nombre de estado duplicado"}), 409
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/estados/<int:item_id>")
@requires_auth
def delete_estado(_jwt_payload, item_id):
    item = db.session.get(Estado, item_id)
    if not item:
        return jsonify({"error": "Estado no encontrado"}), 404
    db.session.delete(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar: estado en uso"}), 409
    return jsonify({"deleted": True, "id": item_id}), 200


@masters_bp.get("/cultivos")
@requires_auth
def list_cultivos(_jwt_payload):
    data = Cultivo.query.order_by(Cultivo.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/cultivos/<int:item_id>")
@requires_auth
def get_cultivo(_jwt_payload, item_id):
    item = db.session.get(Cultivo, item_id)
    if not item:
        return jsonify({"error": "Cultivo no encontrado"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/cultivos")
@requires_auth
def create_cultivo(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    nombre = payload.get("nombre")
    if not nombre:
        return _bad_request("Campo requerido faltante: nombre")

    try:
        fecha_inicio = _parse_iso_date(payload.get("fecha_inicio"), "fecha_inicio")
        responsable_id = _to_int_or_none(payload.get("responsable_id"))
        responsable_id = _validate_fk(User, responsable_id, "responsable_id")
        estado_id = _resolve_estado_id(payload, required=True)
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Cultivo(
        nombre=nombre,
        ubicacion=payload.get("ubicacion"),
        fecha_inicio=fecha_inicio,
        estado_id=estado_id,
        responsable_id=responsable_id,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se pudo crear cultivo por relacion invalida"}), 409
    return jsonify(item.to_dict()), 201


@masters_bp.put("/cultivos/<int:item_id>")
@requires_auth
def update_cultivo(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Cultivo, item_id)
    if not item:
        return jsonify({"error": "Cultivo no encontrado"}), 404

    if "fecha_inicio" in payload:
        try:
            item.fecha_inicio = _parse_iso_date(payload.get("fecha_inicio"), "fecha_inicio")
        except ValueError as exc:
            return _bad_request(str(exc))

    if "responsable_id" in payload:
        try:
            responsable_id = _to_int_or_none(payload.get("responsable_id"))
            item.responsable_id = _validate_fk(User, responsable_id, "responsable_id")
        except ValueError as exc:
            return _bad_request(str(exc))

    if "estado_id" in payload or "estado" in payload:
        try:
            item.estado_id = _resolve_estado_id(payload, required=True)
        except ValueError as exc:
            return _bad_request(str(exc))

    item.nombre = payload.get("nombre", item.nombre)
    item.ubicacion = payload.get("ubicacion", item.ubicacion)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se pudo actualizar cultivo por relacion invalida"}), 409
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/cultivos/<int:item_id>")
@requires_auth
def delete_cultivo(_jwt_payload, item_id):
    item = db.session.get(Cultivo, item_id)
    if not item:
        return jsonify({"error": "Cultivo no encontrado"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True, "id": item_id}), 200


@masters_bp.get("/lotes")
@requires_auth
def list_lotes(_jwt_payload):
    data = Lote.query.order_by(Lote.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/lotes/<int:item_id>")
@requires_auth
def get_lote(_jwt_payload, item_id):
    item = db.session.get(Lote, item_id)
    if not item:
        return jsonify({"error": "Lote no encontrado"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/lotes")
@requires_auth
def create_lote(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    cultivo_id = payload.get("cultivo_id")
    if cultivo_id in (None, ""):
        return _bad_request("Campo requerido faltante: cultivo_id")
    try:
        cultivo_id = _to_int_or_none(cultivo_id)
        cultivo_id = _validate_fk(Cultivo, cultivo_id, "cultivo_id")
        fecha_siembra = _parse_iso_date(payload.get("fecha_siembra"), "fecha_siembra")
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Lote(
        cultivo_id=cultivo_id,
        nombre=payload.get("nombre"),
        fecha_siembra=fecha_siembra,
        estado=payload.get("estado"),
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se pudo crear lote por relacion invalida"}), 409
    return jsonify(item.to_dict()), 201


@masters_bp.put("/lotes/<int:item_id>")
@requires_auth
def update_lote(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Lote, item_id)
    if not item:
        return jsonify({"error": "Lote no encontrado"}), 404

    if "cultivo_id" in payload:
        try:
            cultivo_id = _to_int_or_none(payload.get("cultivo_id"))
            if cultivo_id is None:
                return _bad_request("Campo requerido faltante: cultivo_id")
            item.cultivo_id = _validate_fk(Cultivo, cultivo_id, "cultivo_id")
        except ValueError as exc:
            return _bad_request(str(exc))

    if "fecha_siembra" in payload:
        try:
            item.fecha_siembra = _parse_iso_date(payload.get("fecha_siembra"), "fecha_siembra")
        except ValueError as exc:
            return _bad_request(str(exc))

    item.nombre = payload.get("nombre", item.nombre)
    item.estado = payload.get("estado", item.estado)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se pudo actualizar lote por relacion invalida"}), 409
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/lotes/<int:item_id>")
@requires_auth
def delete_lote(_jwt_payload, item_id):
    item = db.session.get(Lote, item_id)
    if not item:
        return jsonify({"error": "Lote no encontrado"}), 404
    db.session.delete(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar: lote en uso"}), 409
    return jsonify({"deleted": True, "id": item_id}), 200


@masters_bp.get("/plantas")
@requires_auth
def list_plantas(_jwt_payload):
    data = Planta.query.order_by(Planta.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/plantas/<int:item_id>")
@requires_auth
def get_planta(_jwt_payload, item_id):
    item = db.session.get(Planta, item_id)
    if not item:
        return jsonify({"error": "Planta no encontrada"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/plantas")
@requires_auth
def create_planta(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    lote_id = payload.get("lote_id")
    if lote_id in (None, ""):
        return _bad_request("Campo requerido faltante: lote_id")

    try:
        fecha_germinacion = _parse_iso_date(payload.get("fecha_germinacion"), "fecha_germinacion")
        lote_id = _to_int_or_none(lote_id)
        lote_id = _validate_fk(Lote, lote_id, "lote_id")
        estado_id = _resolve_estado_id(payload, required=True)
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Planta(
        lote_id=lote_id,
        codigo=payload.get("codigo"),
        fecha_germinacion=fecha_germinacion,
        estado_id=estado_id,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "codigo duplicado o relacion invalida"}), 409
    return jsonify(item.to_dict()), 201


@masters_bp.put("/plantas/<int:item_id>")
@requires_auth
def update_planta(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Planta, item_id)
    if not item:
        return jsonify({"error": "Planta no encontrada"}), 404

    if "fecha_germinacion" in payload:
        try:
            item.fecha_germinacion = _parse_iso_date(payload.get("fecha_germinacion"), "fecha_germinacion")
        except ValueError as exc:
            return _bad_request(str(exc))

    if "lote_id" in payload:
        try:
            lote_id = _to_int_or_none(payload.get("lote_id"))
            if lote_id is None:
                return _bad_request("Campo requerido faltante: lote_id")
            item.lote_id = _validate_fk(Lote, lote_id, "lote_id")
        except ValueError as exc:
            return _bad_request(str(exc))

    if "estado_id" in payload or "estado" in payload:
        try:
            item.estado_id = _resolve_estado_id(payload, required=True)
        except ValueError as exc:
            return _bad_request(str(exc))

    item.codigo = payload.get("codigo", item.codigo)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "codigo duplicado o relacion invalida"}), 409
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/plantas/<int:item_id>")
@requires_auth
def delete_planta(_jwt_payload, item_id):
    item = db.session.get(Planta, item_id)
    if not item:
        return jsonify({"error": "Planta no encontrada"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True, "id": item_id}), 200


@masters_bp.get("/proveedores")
@requires_auth
def list_proveedores(_jwt_payload):
    data = Proveedor.query.order_by(Proveedor.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/proveedores/<int:item_id>")
@requires_auth
def get_proveedor(_jwt_payload, item_id):
    item = db.session.get(Proveedor, item_id)
    if not item:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/proveedores")
@requires_auth
def create_proveedor(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    nombre = payload.get("nombre")
    if not nombre:
        return _bad_request("Campo requerido faltante: nombre")

    item = Proveedor(
        nombre=nombre,
        telefono=payload.get("telefono"),
        email=payload.get("email"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@masters_bp.put("/proveedores/<int:item_id>")
@requires_auth
def update_proveedor(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Proveedor, item_id)
    if not item:
        return jsonify({"error": "Proveedor no encontrado"}), 404

    item.nombre = payload.get("nombre", item.nombre)
    item.telefono = payload.get("telefono", item.telefono)
    item.email = payload.get("email", item.email)
    db.session.commit()
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/proveedores/<int:item_id>")
@requires_auth
def delete_proveedor(_jwt_payload, item_id):
    item = db.session.get(Proveedor, item_id)
    if not item:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    db.session.delete(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar: proveedor en uso"}), 409
    return jsonify({"deleted": True, "id": item_id}), 200


@masters_bp.get("/insumos")
@requires_auth
def list_insumos(_jwt_payload):
    data = Insumo.query.order_by(Insumo.id.asc()).all()
    return jsonify([item.to_dict() for item in data]), 200


@masters_bp.get("/insumos/<int:item_id>")
@requires_auth
def get_insumo(_jwt_payload, item_id):
    item = db.session.get(Insumo, item_id)
    if not item:
        return jsonify({"error": "Insumo no encontrado"}), 404
    return jsonify(item.to_dict()), 200


@masters_bp.post("/insumos")
@requires_auth
def create_insumo(_jwt_payload):
    payload = request.get_json(silent=True) or {}
    nombre = payload.get("nombre")
    if not nombre:
        return _bad_request("Campo requerido faltante: nombre")

    try:
        proveedor_id = _to_int_or_none(payload.get("proveedor_id"))
        proveedor_id = _validate_fk(Proveedor, proveedor_id, "proveedor_id")
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Insumo(
        nombre=nombre,
        tipo=payload.get("tipo"),
        unidad_medida=payload.get("unidad_medida"),
        stock_actual=payload.get("stock_actual", 0),
        proveedor_id=proveedor_id,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "proveedor_id invalido"}), 409
    return jsonify(item.to_dict()), 201


@masters_bp.put("/insumos/<int:item_id>")
@requires_auth
def update_insumo(_jwt_payload, item_id):
    payload = request.get_json(silent=True) or {}
    item = db.session.get(Insumo, item_id)
    if not item:
        return jsonify({"error": "Insumo no encontrado"}), 404

    if "proveedor_id" in payload:
        try:
            proveedor_id = _to_int_or_none(payload.get("proveedor_id"))
            item.proveedor_id = _validate_fk(Proveedor, proveedor_id, "proveedor_id")
        except ValueError as exc:
            return _bad_request(str(exc))

    item.nombre = payload.get("nombre", item.nombre)
    item.tipo = payload.get("tipo", item.tipo)
    item.unidad_medida = payload.get("unidad_medida", item.unidad_medida)
    item.stock_actual = payload.get("stock_actual", item.stock_actual)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "proveedor_id invalido"}), 409
    return jsonify(item.to_dict()), 200


@masters_bp.delete("/insumos/<int:item_id>")
@requires_auth
def delete_insumo(_jwt_payload, item_id):
    item = db.session.get(Insumo, item_id)
    if not item:
        return jsonify({"error": "Insumo no encontrado"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True, "id": item_id}), 200
