# Guion de Video - Entrega GNUCannabis

## Duracion sugerida
- 8 a 10 minutos

---

## 0) Apertura (20-30s)
**Que decir:**

> Hola profe, soy [tu nombre]. En esta entrega presento el sistema GNUCannabis, un aplicativo web con microservicio en Flask, autenticacion con Auth0, frontend en React y base de datos MySQL. Voy a mostrar contexto, CRUD, autenticacion personalizada, metadata en Auth0 y modelo de datos.

**Que mostrar:**
- Pantalla inicial de la app (`http://localhost:3000`) con logo y branding.

---

## 1) Contexto del escenario (1 min)
**Que decir:**

> GNUCannabis es un sistema para gestionar procesos del negocio de cultivo: usuarios, cultivos, lotes, plantas, proveedores e insumos.  
> El objetivo es centralizar informacion operativa, mantener trazabilidad y asegurar acceso controlado por autenticacion.  
> Este escenario es relevante porque mezcla seguridad, operacion agricola e inventario, y permite tomar decisiones con datos consistentes.

**Que mostrar:**
- Menu lateral con los modulos.
- Vista general del dashboard.

---

## 2) Tecnologias usadas (45s)
**Que decir:**

> La solucion esta implementada con arquitectura de servicios y contenedores:
> - Backend: Flask + SQLAlchemy.  
> - Frontend: React servido con Nginx.  
> - Base de datos: MySQL.  
> - Seguridad: Auth0 (login, sesion y JWT).  
> - Orquestacion: Docker Compose.

**Que mostrar:**
- Archivo `docker-compose.yml` (servicios `auth-users-api`, `frontend`, `mysql`).
- Terminal con `docker compose ps`.

---

## 3) CRUD completo (3-4 min)

### 3.1 CRUD de usuarios
**Que decir:**

> El modulo de usuarios esta integrado con Auth0 Management API, por lo que consumimos un servicio de identidad externo seguro.

**Demostracion:**
- Entrar a `Usuarios`.
- Crear usuario (nombre, correo, password, tipo/numero documento).
- Ver detalle.
- Actualizar.
- Eliminar.

**Captura de codigo recomendada:**
- `src/routes/users.py` (endpoints CRUD).
- `src/utils/auth0_management.py` (llamados a Auth0).

---

### 3.2 CRUD de modulos adicionales
**Que decir:**

> Ademas del maestro usuarios, implementamos CRUD para cultivos, plantas, lotes, proveedores, insumos y estados.

**Demostracion sugerida:**
- `Estados`: crear `ACTIVO` / `INACTIVO`.
- `Cultivos`: crear con estado por selector.
- `Lotes`: crear relacionado a cultivo.
- `Plantas`: crear relacionado a lote y estado.
- Mostrar botones `Ver`, `Actualizar`, `Eliminar`.

**Captura de codigo recomendada:**
- `src/routes/masters.py` (CRUD y validaciones de relaciones).
- `frontend/main.jsx` (vistas index/create/view/update y selects dinamicos).
- `frontend/styles.css` (layout y componentes visuales).

---

## 4) Autenticacion con Auth0 (2 min)

### 4.1 Login integrado
**Que decir:**

> La autenticacion se realiza con Auth0 e integra el flujo completo de login con nuestra aplicacion.

**Que mostrar:**
- Clic en "Iniciar sesion".
- Flujo de Auth0.
- Regreso al frontend autenticado.

**Captura de codigo recomendada:**
- `src/routes/web_auth.py` (`/login`, `/callback`, `/auth/session`, `/logout`).
- `src/utils/auth.py` (validacion JWT).

---

### 4.2 Interfaz personalizada
**Que decir:**

> La interfaz fue personalizada con branding de GNUCannabis: colores, logo y una experiencia visual consistente.

**Que mostrar:**
- Pantallas de login y frontend con logo nuevo.

**Captura de codigo recomendada:**
- `src/templates/index.html`
- `src/static/style.css`
- `frontend/main.jsx`

---

### 4.3 Registro y metadata en Auth0
**Que decir:**

> En registro se captura correo y contrasena; ademas, nombre completo y un flujo adicional para tipo y numero de documento.  
> Esta informacion se almacena en el perfil del usuario como metadata en Auth0.

**Que mostrar:**
- Formulario adicional en Auth0 (el que ya configuraste).
- En Auth0 Dashboard -> Users: mostrar `name` y `user_metadata.tipo_documento` / `numero_documento`.

---

## 5) Diagramacion y modelo de datos (1-1.5 min)
**Que decir:**

> Se reutilizo la diagramacion general del sistema y el modelo relacional en MySQL Workbench, mostrando tablas y relaciones entre modulos.

**Que mostrar:**
- Draw.io (modulos, actores, conexiones).
- MySQL Workbench (tablas y relaciones: cultivos-lotes-plantas, proveedores-insumos, estados, etc.).

---

## 6) Implementacion de Kafka (1.5-2 min)
**Que decir:**

> Se implemento Apache Kafka fuera de `gnucannabis` con Docker Compose y se integro un consumidor en el microservicio Flask para persistir eventos en MySQL.  
> El flujo es: producer -> topic `plantasAlertas` -> consumer -> tabla `kafka_logs`.

**Que mostrar (paso a paso):**
- `docker compose -f ../docker-compose-kafka.yml ps` con `kafka` y `zookeeper` arriba.
- `docker compose -f docker-compose.yml ps` con `kafka-log-consumer` arriba.
- Envio de mensaje al topic con `kafka-console-producer`.
- Consulta SQL en MySQL mostrando inserts en `kafka_logs`.

**Captura de codigo recomendada:**
- `src/models/kafka_log.py` (modelo/tabla de logs).
- `src/utils/kafka_consumer.py` (consumo y persistencia).
- `src/kafka_worker.py` (worker dedicado).
- `docker-compose.yml` (servicio `kafka-log-consumer`).
- `.env` / `.env.example` (variables `KAFKA_*`).

**Comandos de verificacion para evidencia:**
- `docker compose -f ../docker-compose-kafka.yml exec -T kafka kafka-topics --list --bootstrap-server kafka:29092`
- `docker compose -f ../docker-compose-kafka.yml exec -T kafka bash -lc "kafka-console-producer --topic plantasAlertas --bootstrap-server kafka:29092 <<< 'alerta_video_demo'"`
- `docker compose -f docker-compose.yml exec -T mysql mysql -uroot -proot123 gnucannabis -e "SELECT id, topic, payload, created_at FROM kafka_logs ORDER BY id DESC LIMIT 10;"`

---

## 7) Cierre (20-30s)
**Que decir:**

> En conclusion, se entrega una solucion funcional con CRUD completo, autenticacion Auth0, personalizacion visual y modelo de datos consistente, todo dockerizado para un despliegue reproducible.

---

## Evidencias obligatorias recomendadas
- `docker compose ps` con servicios arriba.
- `docker compose -f ../docker-compose-kafka.yml ps` y `docker compose -f docker-compose.yml ps`.
- Insercion de eventos en tabla `kafka_logs`.
- Login y logout funcionando.
- CRUD de `usuarios` + al menos un modulo adicional.
- Selectores de relaciones (`estado`, `lote`, `cultivo`, `proveedor`).
- Metadata en Auth0.
- Diagrama Draw.io y modelo Workbench.

---

## Checklist antes de grabar
- Tener datos de prueba cargados para no improvisar.
- Dejar abiertas estas ventanas: app, Auth0 dashboard, codigo, draw.io, workbench.
- Usar zoom del navegador entre 110% y 125%.
- Ensayar una vez el flujo completo (sin pausas largas).
 
 $pass= memopunk