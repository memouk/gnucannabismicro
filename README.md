# gnucannabis

Microservicio en Flask para:

- Autenticacion Auth0 tipo WebApp (login/logout/callback/profile)
- Autorizacion JWT para endpoints API
- CRUD de `usuarios` gestionado en Auth0 Management API

## 1) Requisitos

- Docker y Docker Compose
- Tenant en Auth0 con API configurada

## 2) Configuracion

1. Copia archivo de entorno:

```bash
cp .env.example .env
```

2. Edita `.env`:

- `MYSQL_*` para credenciales de la DB (por defecto crea `gnucannabis`)
- `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`, `AUTH0_SECRET`, `AUTH0_REDIRECT_URI`
- `FRONTEND_URL` URL de retorno despues del login (ej. `http://localhost:3000`)
- `AUTH0_AUDIENCE` para proteger endpoints API con bearer token
- `AUTH0_MGMT_AUDIENCE`, `AUTH0_MGMT_CLIENT_ID`, `AUTH0_MGMT_CLIENT_SECRET` para CRUD de usuarios en Auth0
- `AUTH0_DB_CONNECTION` para crear usuarios de base de datos (ej. `Username-Password-Authentication`)
- Genera `AUTH0_SECRET` con:

```bash
openssl rand -hex 64
```

3. Configura tu app en Auth0 Dashboard (Regular Web Application):

- Allowed Callback URLs: `http://localhost:5000/callback`
- Allowed Logout URLs: `http://localhost:5000`, `http://localhost:3000`
- Allowed Web Origins: `http://localhost:5000`

## 3) Levantar servicio

```bash
docker compose up --build -d
```

### 3.1) Si ya tenias el proyecto y hiciste `git pull`

Tus companeros deben ejecutar estos pasos para traer cambios de codigo y de esquema en la BD:

```bash
docker compose up --build -d auth-users-api frontend
```

El backend aplica sincronizacion de esquema al iniciar:

- Crea tabla `estados` si no existe.
- Inserta estados base (`ACTIVO`, `INACTIVO`) si faltan.
- Agrega columna `estado_id` en `cultivos` y `plantas` si no existe.
- Crea llaves foraneas de `estado_id` hacia `estados`.
- Migra datos antiguos de `estado` (texto) hacia `estado_id` cuando coincide.

Si quieren validar en MySQL:

```bash
docker compose exec -T mysql mysql -u root -proot123 -D gnucannabis -e "DESCRIBE estados; DESCRIBE cultivos; DESCRIBE plantas;"
```

Servicios:

- API Flask: `http://localhost:5000`
- Frontend React: `http://localhost:3000`

Verifica salud:

```bash
curl http://localhost:5000/api/health
```

Opcional, revisar logs:

```bash
docker compose logs -f mysql auth-users-api frontend
```

## 4) Rutas web de autenticacion

- `GET /` home con estado de sesion
- `GET /login` redirige al login de Auth0
- `GET /callback` callback OIDC de Auth0
- `GET /profile` vista protegida por sesion
- `GET /logout` cierre de sesion

## 5) Endpoints API

- `GET /api/health` (publico)
- `GET /api/me` (token Auth0)
- `GET /api/usuarios` (token Auth0)
- `GET /api/usuarios/{id}` (token Auth0, id formato `auth0|xxxx`)
- `POST /api/usuarios` (token Auth0)
- `PUT /api/usuarios/{id}` (token Auth0)
- `DELETE /api/usuarios/{id}` (token Auth0)
- `GET /api/cultivos`, `POST /api/cultivos`, `PUT /api/cultivos/{id}`, `DELETE /api/cultivos/{id}` (token)
- `GET /api/lotes`, `POST /api/lotes`, `PUT /api/lotes/{id}`, `DELETE /api/lotes/{id}` (token)
- `GET /api/plantas`, `POST /api/plantas`, `PUT /api/plantas/{id}`, `DELETE /api/plantas/{id}` (token)
- `GET /api/proveedores`, `POST /api/proveedores`, `PUT /api/proveedores/{id}`, `DELETE /api/proveedores/{id}` (token)
- `GET /api/insumos`, `POST /api/insumos`, `PUT /api/insumos/{id}`, `DELETE /api/insumos/{id}` (token)
- `GET /api/estados`, `POST /api/estados`, `PUT /api/estados/{id}`, `DELETE /api/estados/{id}` (token)

> El CRUD de `usuarios` se ejecuta contra Auth0 Management API.

## 6) Ejemplo rapido con token

```bash
curl -X GET http://localhost:5000/api/usuarios \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

## 7) Payload para crear usuario

```json
{
  "nombre": "Juan Perez",
  "email": "juan@gnucannabis.com",
  "password": "Temporal123!",
  "activo": true,
  "tipo_documento": "CC",
  "numero_documento": "1234567890"
}
```

## 8) Payloads ejemplo para maestros

Cultivo:

```json
{
  "nombre": "Cultivo Norte",
  "ubicacion": "Invernadero A",
  "fecha_inicio": "2026-03-25",
  "estado_id": 1,
  "responsable_id": 1
}
```

## 9) Frontend React para CRUD

El frontend esta en `frontend/` y corre en `http://localhost:3000`.

- Haz clic en **Iniciar sesion Auth0**.
- Despues del callback, vuelve automaticamente al frontend.
- Selecciona recurso (`usuarios`, `cultivos`, `lotes`, `plantas`, `proveedores`, `insumos`, `estados`).
- Ejecuta operaciones: listar, crear, obtener por ID, actualizar y eliminar.
- El frontend hace proxy a `/api` hacia `auth-users-api` por Nginx (sin cambiar CORS en navegador).
- En formularios con relaciones se usa selector (no escribir IDs manuales en los casos soportados), por ejemplo:
  - `cultivos.estado_id` y `plantas.estado_id` toman opciones de `estados`.
  - `plantas.lote_id` toma opciones de `lotes`.
  - `lotes.cultivo_id` toma opciones de `cultivos`.
  - `insumos.proveedor_id` toma opciones de `proveedores`.

Planta:

```json
{
  "lote_id": 1,
  "codigo": "PLANTA-0001",
  "fecha_germinacion": "2026-03-10",
  "estado_id": 1
}
```

Insumo:

```json
{
  "nombre": "Fertilizante NPK",
  "tipo": "FERTILIZANTE",
  "unidad_medida": "kg",
  "stock_actual": 25.5,
  "proveedor_id": 1
}
```

Lote:

```json
{
  "cultivo_id": 1,
  "nombre": "Lote A-01",
  "fecha_siembra": "2026-03-12",
  "estado": "PREPARACION"
}
```

Proveedor:

```json
{
  "nombre": "Agroinsumos SAS",
  "telefono": "3000000000",
  "email": "contacto@agroinsumos.co"
}
```

Estado:

```json
{
  "nombre": "ACTIVO",
  "descripcion": "Registro habilitado"
}
```
