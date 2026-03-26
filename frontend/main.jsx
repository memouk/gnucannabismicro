const { useEffect, useMemo, useState } = React;

const TOKEN_STORAGE_KEY = "gnucannabis_access_token";

const RESOURCES = {
  usuarios: {
    path: "usuarios",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "email", label: "Email", type: "text" },
      { name: "password_hash", label: "Password hash", type: "text" },
      { name: "activo", label: "Activo", type: "checkbox" },
    ],
    defaults: { nombre: "", email: "", password_hash: "", activo: true },
  },
  cultivos: {
    path: "cultivos",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "ubicacion", label: "Ubicacion", type: "text" },
      { name: "fecha_inicio", label: "Fecha inicio", type: "date" },
      { name: "estado", label: "Estado", type: "text" },
      { name: "responsable_id", label: "Responsable ID", type: "number" },
    ],
    defaults: { nombre: "", ubicacion: "", fecha_inicio: "", estado: "", responsable_id: 1 },
  },
  plantas: {
    path: "plantas",
    fields: [
      { name: "lote_id", label: "Lote ID", type: "number" },
      { name: "codigo", label: "Codigo", type: "text" },
      { name: "fecha_germinacion", label: "Fecha germinacion", type: "date" },
      { name: "estado", label: "Estado", type: "text" },
    ],
    defaults: { lote_id: 1, codigo: "", fecha_germinacion: "", estado: "" },
  },
  insumos: {
    path: "insumos",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "tipo", label: "Tipo", type: "text" },
      { name: "unidad_medida", label: "Unidad medida", type: "text" },
      { name: "stock_actual", label: "Stock actual", type: "number" },
      { name: "proveedor_id", label: "Proveedor ID", type: "number" },
    ],
    defaults: { nombre: "", tipo: "", unidad_medida: "", stock_actual: 0, proveedor_id: 1 },
  },
};

function BrandLogo({ small = false }) {
  const size = small ? 36 : 64;
  return (
    <div className={`brand-logo ${small ? "small" : ""}`}>
      <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
        <circle cx="32" cy="32" r="31" fill="#C8E6C9" stroke="#2E7D32" strokeWidth="2" />
        <path
          d="M32 10c5 6 5 13 0 19-5-6-5-13 0-19Zm-12 9c7 2 11 8 11 15-7-2-11-8-11-15Zm24 0c0 7-4 13-11 15 0-7 4-13 11-15Zm-22 17c8 0 13 4 15 11-8 0-13-4-15-11Zm20 0c-2 7-7 11-15 11 2-7 7-11 15-11Z"
          fill="#2E7D32"
        />
        <text x="32" y="49" textAnchor="middle" fontSize="16" fontWeight="700" fill="#1B5E20">
          G
        </text>
      </svg>
    </div>
  );
}

function castByType(value, type) {
  if (type === "number") return value === "" ? null : Number(value);
  return value;
}

function buildPayload(fields, values) {
  const payload = {};
  fields.forEach((field) => {
    const raw = values[field.name];
    if (field.type === "checkbox") {
      payload[field.name] = Boolean(raw);
      return;
    }
    if (raw === "" || raw === null || typeof raw === "undefined") return;
    payload[field.name] = castByType(raw, field.type);
  });
  return payload;
}

function App() {
  const [token, setToken] = useState(localStorage.getItem(TOKEN_STORAGE_KEY) || "");
  const [isAuthorized, setIsAuthorized] = useState(Boolean(localStorage.getItem(TOKEN_STORAGE_KEY)));
  const [sessionUser, setSessionUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("Listo para probar CRUD...");

  const [resource, setResource] = useState("plantas");
  const [menuAction, setMenuAction] = useState("index");
  const [currentId, setCurrentId] = useState("");
  const [createData, setCreateData] = useState({ ...RESOURCES.plantas.defaults });
  const [updateData, setUpdateData] = useState({ ...RESOURCES.plantas.defaults });

  const activeResource = useMemo(() => RESOURCES[resource], [resource]);

  function saveToken(nextToken) {
    setToken(nextToken);
    if (nextToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, nextToken);
      setIsAuthorized(true);
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setIsAuthorized(false);
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const authError = params.get("auth_error");
    const authErrorDescription = params.get("auth_error_description");
    if (authError) {
      setOutput(`Auth0: ${authErrorDescription || "No se pudo completar la autenticacion."}`);
      params.delete("auth_error");
      params.delete("auth_error_description");
      const nextQuery = params.toString();
      const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ""}`;
      window.history.replaceState({}, "", nextUrl);
    }
  }, []);

  useEffect(() => {
    setCreateData({ ...RESOURCES[resource].defaults });
    setUpdateData({ ...RESOURCES[resource].defaults });
    setCurrentId("");
  }, [resource]);

  async function loadSession() {
    setLoading(true);
    try {
      const response = await fetch("/auth/session", { credentials: "include" });
      const data = await response.json();
      if (!response.ok || !data.authenticated) {
        setSessionUser(null);
        setIsAuthorized(false);
        setOutput("No hay sesion activa. Inicia sesion con Auth0.");
        return;
      }
      setSessionUser(data.user);
      setIsAuthorized(true);
      if (data.access_token) {
        saveToken(data.access_token);
        setOutput("Sesion activa y token guardado.");
      } else {
        setOutput("Sesion activa, pero no hay access token (configura AUTH0_AUDIENCE).");
      }
    } catch (err) {
      setOutput(`Error cargando sesion: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function callApi(method, path, payload) {
    if (!token) {
      setOutput("No hay token. Inicia sesion y carga sesion/token.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(path, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          ...(payload ? { "Content-Type": "application/json" } : {}),
        },
        ...(payload ? { body: JSON.stringify(payload) } : {}),
      });
      const text = await response.text();
      let parsed = text;
      try {
        parsed = JSON.parse(text);
      } catch (_err) {}
      setOutput(JSON.stringify({ status: response.status, data: parsed }, null, 2));
    } catch (err) {
      setOutput(`Error de red: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function runAction() {
    const base = `/api/${activeResource.path}`;
    if (menuAction === "index") return callApi("GET", base);
    if ((menuAction === "update" || menuAction === "delete") && !currentId) {
      setOutput("Debes ingresar un ID.");
      return;
    }
    if (menuAction === "create") {
      return callApi("POST", base, buildPayload(activeResource.fields, createData));
    }
    if (menuAction === "update") {
      return callApi("PUT", `${base}/${currentId}`, buildPayload(activeResource.fields, updateData));
    }
    if (menuAction === "delete") {
      return callApi("DELETE", `${base}/${currentId}`);
    }
  }

  function renderForm(values, setter) {
    return (
      <div className="form-grid">
        {activeResource.fields.map((field) => (
          <label key={field.name} className="field">
            <span>{field.label}</span>
            {field.type === "checkbox" ? (
              <input
                type="checkbox"
                checked={Boolean(values[field.name])}
                onChange={(e) => setter({ ...values, [field.name]: e.target.checked })}
              />
            ) : (
              <input
                type={field.type}
                value={values[field.name] ?? ""}
                onChange={(e) => setter({ ...values, [field.name]: e.target.value })}
              />
            )}
          </label>
        ))}
      </div>
    );
  }

  return (
    <div className="container">
      <div className="brand-header">
        <BrandLogo />
        <div>
          <h1>gnucannabis</h1>
          <p className="muted">Panel CRUD maestro con sesion Auth0</p>
        </div>
      </div>

      <div className="card login-card">
        <div className="login-left">
          <div className="login-title-row">
            <BrandLogo small />
            <h2>Sesion y autorizacion</h2>
          </div>
          <p className="muted">
            Estado:{" "}
            <strong>{isAuthorized ? "Autorizado" : "No autorizado"}</strong>
          </p>
          <p className="muted">
            Usuario: {sessionUser ? sessionUser.name || sessionUser.email : "Sin sesion"}
          </p>
        </div>
        <div className="login-right">
          {!isAuthorized && (
            <>
              <button className="primary" onClick={() => (window.location.href = "/login")}>
                Iniciar sesion con Auth0
              </button>
              <button className="secondary" onClick={loadSession}>
                Cargar sesion/token
              </button>
            </>
          )}
          <button
            className="danger"
            onClick={() => {
              saveToken("");
              setSessionUser(null);
              window.location.href = "/logout";
            }}
          >
            Cerrar sesion
          </button>
        </div>
      </div>

      <div className="layout">
        <aside className="card sidebar">
          <h3>Menu maestros</h3>
          {Object.keys(RESOURCES).map((name) => (
            <button
              key={name}
              className={`tab ${resource === name ? "active" : "secondary"}`}
              onClick={() => setResource(name)}
            >
              {name}
            </button>
          ))}

          <h4>Accion</h4>
          <div className="tabs vertical">
            {["index", "create", "update", "delete"].map((action) => (
              <button
                key={action}
                className={`tab ${menuAction === action ? "active" : "secondary"}`}
                onClick={() => setMenuAction(action)}
              >
                {action}
              </button>
            ))}
          </div>
        </aside>

        <section className="card content">
          <h3>
            {resource} / {menuAction}
          </h3>

          {(menuAction === "update" || menuAction === "delete") && (
            <label className="field">
              <span>ID</span>
              <input type="number" value={currentId} onChange={(e) => setCurrentId(e.target.value)} />
            </label>
          )}

          {menuAction === "create" && renderForm(createData, setCreateData)}
          {menuAction === "update" && renderForm(updateData, setUpdateData)}

          <div className="row">
            <button className="primary" onClick={runAction}>
              Ejecutar {menuAction}
            </button>
          </div>

          <p className="muted">{loading ? "Procesando..." : "Listo"}</p>
        </section>
      </div>

      <div className="card">
        <h3>Respuesta</h3>
        <pre>{output}</pre>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
