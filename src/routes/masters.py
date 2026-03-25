from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from src.extensions import db
from src.models.cultivo import Cultivo
from src.models.insumo import Insumo
from src.models.planta import Planta
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
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Cultivo(
        nombre=nombre,
        ubicacion=payload.get("ubicacion"),
        fecha_inicio=fecha_inicio,
        estado=payload.get("estado"),
        responsable_id=payload.get("responsable_id"),
    )
    db.session.add(item)
    db.session.commit()
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

    item.nombre = payload.get("nombre", item.nombre)
    item.ubicacion = payload.get("ubicacion", item.ubicacion)
    item.estado = payload.get("estado", item.estado)
    item.responsable_id = payload.get("responsable_id", item.responsable_id)
    db.session.commit()
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
    if not lote_id:
        return _bad_request("Campo requerido faltante: lote_id")

    try:
        fecha_germinacion = _parse_iso_date(payload.get("fecha_germinacion"), "fecha_germinacion")
    except ValueError as exc:
        return _bad_request(str(exc))

    item = Planta(
        lote_id=lote_id,
        codigo=payload.get("codigo"),
        fecha_germinacion=fecha_germinacion,
        estado=payload.get("estado"),
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "codigo duplicado o lote_id invalido"}), 409
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

    item.lote_id = payload.get("lote_id", item.lote_id)
    item.codigo = payload.get("codigo", item.codigo)
    item.estado = payload.get("estado", item.estado)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "codigo duplicado o lote_id invalido"}), 409
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

    item = Insumo(
        nombre=nombre,
        tipo=payload.get("tipo"),
        unidad_medida=payload.get("unidad_medida"),
        stock_actual=payload.get("stock_actual", 0),
        proveedor_id=payload.get("proveedor_id"),
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

    item.nombre = payload.get("nombre", item.nombre)
    item.tipo = payload.get("tipo", item.tipo)
    item.unidad_medida = payload.get("unidad_medida", item.unidad_medida)
    item.stock_actual = payload.get("stock_actual", item.stock_actual)
    item.proveedor_id = payload.get("proveedor_id", item.proveedor_id)
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
