# gnucannabis

Microservicio en Flask para:

- Autenticacion Auth0 tipo WebApp (login/logout/callback/profile)
- Autorizacion JWT para endpoints API
- CRUD del maestro `usuarios` en MySQL

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
- `AUTH0_AUDIENCE` para proteger endpoints API con bearer token
- Genera `AUTH0_SECRET` con:

```bash
openssl rand -hex 64
```

3. Configura tu app en Auth0 Dashboard (Regular Web Application):

- Allowed Callback URLs: `http://localhost:5000/callback`
- Allowed Logout URLs: `http://localhost:5000`
- Allowed Web Origins: `http://localhost:5000`

## 3) Levantar servicio

```bash
docker compose up --build -d
```

Verifica salud:

```bash
curl http://localhost:5000/api/health
```

Opcional, revisar logs:

```bash
docker compose logs -f mysql auth-users-api
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
- `GET /api/users` o `GET /api/usuarios` (token Auth0)
- `GET /api/users/{id}` o `GET /api/usuarios/{id}` (token Auth0)
- `POST /api/users` o `POST /api/usuarios` (token Auth0)
- `PUT /api/users/{id}` o `PUT /api/usuarios/{id}` (token Auth0)
- `DELETE /api/users/{id}` o `DELETE /api/usuarios/{id}` (token Auth0)
- `GET /api/cultivos`, `POST /api/cultivos`, `PUT /api/cultivos/{id}`, `DELETE /api/cultivos/{id}` (token)
- `GET /api/plantas`, `POST /api/plantas`, `PUT /api/plantas/{id}`, `DELETE /api/plantas/{id}` (token)
- `GET /api/insumos`, `POST /api/insumos`, `PUT /api/insumos/{id}`, `DELETE /api/insumos/{id}` (token)

> Estos endpoints operan sobre la tabla `usuarios` del script SQL compartido.

## 6) Ejemplo rapido con token

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

## 7) Payload para crear usuario

```json
{
  "nombre": "Juan Perez",
  "email": "juan@gnucannabis.com",
  "password_hash": "$2b$12$hash_de_ejemplo",
  "activo": true
}
```

## 8) Payloads ejemplo para maestros

Cultivo:

```json
{
  "nombre": "Cultivo Norte",
  "ubicacion": "Invernadero A",
  "fecha_inicio": "2026-03-25",
  "estado": "ACTIVO",
  "responsable_id": 1
}
```

Planta:

```json
{
  "lote_id": 1,
  "codigo": "PLANTA-0001",
  "fecha_germinacion": "2026-03-10",
  "estado": "SANA"
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
