const { useEffect, useMemo, useState } = React;

const TOKEN_STORAGE_KEY = "gnucannabis_access_token";
const MENU_BREAKPOINT = 980;

const RESOURCES = {
  usuarios: {
    title: "Usuarios",
    path: "usuarios",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "email", label: "Email", type: "text" },
      { name: "password", label: "Password", type: "text" },
      { name: "activo", label: "Activo", type: "checkbox" },
      { name: "tipo_documento", label: "Tipo documento", type: "text" },
      { name: "numero_documento", label: "Numero documento", type: "text" },
    ],
    defaults: {
      nombre: "",
      email: "",
      password: "",
      activo: true,
      tipo_documento: "",
      numero_documento: "",
    },
    columns: ["id", "nombre", "email", "activo"],
    idType: "text",
  },
  cultivos: {
    title: "Cultivos",
    path: "cultivos",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "ubicacion", label: "Ubicacion", type: "text" },
      { name: "fecha_inicio", label: "Fecha inicio", type: "date" },
      { name: "estado_id", label: "Estado", type: "number", optionsKey: "estados" },
      { name: "responsable_id", label: "Responsable ID (opcional)", type: "number" },
    ],
    defaults: { nombre: "", ubicacion: "", fecha_inicio: "", estado_id: "", responsable_id: "" },
    columns: ["id", "nombre", "ubicacion", "estado_id", "fecha_inicio"],
    idType: "number",
  },
  lotes: {
    title: "Lotes",
    path: "lotes",
    fields: [
      { name: "cultivo_id", label: "Cultivo", type: "number", optionsKey: "cultivos" },
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "fecha_siembra", label: "Fecha siembra", type: "date" },
      { name: "estado", label: "Estado (texto)", type: "text" },
    ],
    defaults: { cultivo_id: "", nombre: "", fecha_siembra: "", estado: "" },
    columns: ["id", "cultivo_id", "nombre", "estado", "fecha_siembra"],
    idType: "number",
  },
  plantas: {
    title: "Plantas",
    path: "plantas",
    fields: [
      { name: "lote_id", label: "Lote", type: "number", optionsKey: "lotes" },
      { name: "codigo", label: "Codigo", type: "text" },
      { name: "fecha_germinacion", label: "Fecha germinacion", type: "date" },
      { name: "estado_id", label: "Estado", type: "number", optionsKey: "estados" },
    ],
    defaults: { lote_id: "", codigo: "", fecha_germinacion: "", estado_id: "" },
    columns: ["id", "lote_id", "codigo", "estado_id", "fecha_germinacion"],
    idType: "number",
  },
  proveedores: {
    title: "Proveedores",
    path: "proveedores",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "telefono", label: "Telefono", type: "text" },
      { name: "email", label: "Email", type: "text" },
    ],
    defaults: { nombre: "", telefono: "", email: "" },
    columns: ["id", "nombre", "telefono", "email"],
    idType: "number",
  },
  insumos: {
    title: "Insumos",
    path: "insumos",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "tipo", label: "Tipo", type: "text" },
      { name: "unidad_medida", label: "Unidad medida", type: "text" },
      { name: "stock_actual", label: "Stock actual", type: "number" },
      { name: "proveedor_id", label: "Proveedor (opcional)", type: "number", optionsKey: "proveedores" },
    ],
    defaults: { nombre: "", tipo: "", unidad_medida: "", stock_actual: 0, proveedor_id: "" },
    columns: ["id", "nombre", "tipo", "unidad_medida", "stock_actual"],
    idType: "number",
  },
  estados: {
    title: "Estados",
    path: "estados",
    fields: [
      { name: "nombre", label: "Nombre", type: "text" },
      { name: "descripcion", label: "Descripcion", type: "text" },
    ],
    defaults: { nombre: "", descripcion: "" },
    columns: ["id", "nombre", "descripcion", "created_at"],
    idType: "number",
  },
};

function BrandLogo({ small = false }) {
  const size = small ? 32 : 56;
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

function formatCell(value) {
  if (value === null || typeof value === "undefined" || value === "") return "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function toLabel(key, resourceConfig) {
  const field = resourceConfig.fields.find((f) => f.name === key);
  if (field?.label) return field.label;
  const special = {
    id: "ID",
    created_at: "Fecha creacion",
    user_metadata: "Metadata usuario",
  };
  if (special[key]) return special[key];
  return key.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function App() {
  const [token, setToken] = useState(localStorage.getItem(TOKEN_STORAGE_KEY) || "");
  const [isAuthorized, setIsAuthorized] = useState(Boolean(localStorage.getItem(TOKEN_STORAGE_KEY)));
  const [sessionUser, setSessionUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("Bienvenido.");

  const [menuOpen, setMenuOpen] = useState(window.innerWidth > MENU_BREAKPOINT);
  const [resource, setResource] = useState("cultivos");
  const [viewMode, setViewMode] = useState("index"); // index | create | view | update
  const [searchTerm, setSearchTerm] = useState("");
  const [records, setRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [formData, setFormData] = useState({ ...RESOURCES.cultivos.defaults });
  const [catalogs, setCatalogs] = useState({
    estados: [],
    lotes: [],
    cultivos: [],
    proveedores: [],
  });

  const activeResource = useMemo(() => RESOURCES[resource], [resource]);

  useEffect(() => {
    function onResize() {
      setMenuOpen(window.innerWidth > MENU_BREAKPOINT);
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

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
    const authError = params.get("auth_error_description");
    if (authError) {
      setOutput(`Auth0: ${authError}`);
      params.delete("auth_error");
      params.delete("auth_error_description");
      const nextUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}`;
      window.history.replaceState({}, "", nextUrl);
    }
  }, []);

  async function loadSession() {
    setLoading(true);
    try {
      const response = await fetch("/auth/session", { credentials: "include" });
      const data = await response.json();
      if (!response.ok || !data.authenticated) {
        setSessionUser(null);
        saveToken("");
        setOutput("No hay sesion activa.");
        return;
      }
      setSessionUser(data.user);
      if (data.access_token) {
        saveToken(data.access_token);
        setOutput("Sesion activa.");
      } else {
        setIsAuthorized(true);
        setOutput("Sesion activa, sin token API.");
      }
    } catch (err) {
      setOutput(`Error de sesion: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    async function loadCatalogs() {
      if (!token) return;
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [estadosRes, lotesRes, cultivosRes, proveedoresRes] = await Promise.all([
          fetch("/api/estados", { headers }),
          fetch("/api/lotes", { headers }),
          fetch("/api/cultivos", { headers }),
          fetch("/api/proveedores", { headers }),
        ]);

        const [
          estadosData,
          lotesData,
          cultivosData,
          proveedoresData,
        ] = await Promise.all([
          estadosRes.ok ? estadosRes.json() : [],
          lotesRes.ok ? lotesRes.json() : [],
          cultivosRes.ok ? cultivosRes.json() : [],
          proveedoresRes.ok ? proveedoresRes.json() : [],
        ]);

        setCatalogs({
          estados: Array.isArray(estadosData) ? estadosData : [],
          lotes: Array.isArray(lotesData) ? lotesData : [],
          cultivos: Array.isArray(cultivosData) ? cultivosData : [],
          proveedores: Array.isArray(proveedoresData) ? proveedoresData : [],
        });
      } catch (_err) {
        // No bloquea el CRUD principal si falla un catalogo.
      }
    }
    loadCatalogs();
  }, [token]);

  async function apiCall(method, path, payload) {
    if (!token) {
      setOutput("Sin token API. Inicia sesion.");
      return { ok: false };
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
      let data = text;
      try {
        data = JSON.parse(text);
      } catch (_err) {}

      if (!response.ok) {
        setOutput(JSON.stringify({ status: response.status, data }, null, 2));
        return { ok: false, data };
      }
      return { ok: true, data };
    } catch (err) {
      setOutput(`Error de red: ${err.message}`);
      return { ok: false };
    } finally {
      setLoading(false);
    }
  }

  async function fetchIndex() {
    const result = await apiCall("GET", `/api/${activeResource.path}`);
    if (result.ok) {
      const list = Array.isArray(result.data) ? result.data : [];
      setRecords(list);
      setOutput(`Mostrando ${list.length} registros.`);
    }
  }

  useEffect(() => {
    setViewMode("index");
    setSelectedRecord(null);
    setFormData({ ...activeResource.defaults });
    setSearchTerm("");
    if (isAuthorized) fetchIndex();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource, isAuthorized]);

  function onMenuSelect(next) {
    setResource(next);
    if (window.innerWidth <= MENU_BREAKPOINT) setMenuOpen(false);
  }

  function openCreate() {
    setSelectedRecord(null);
    setFormData({ ...activeResource.defaults });
    setViewMode("create");
  }

  function openView(item) {
    setSelectedRecord(item);
    setViewMode("view");
  }

  function openUpdate(item) {
    setSelectedRecord(item);
    setFormData({ ...activeResource.defaults, ...item });
    setViewMode("update");
  }

  async function onCreate() {
    const payload = buildPayload(activeResource.fields, formData);
    const result = await apiCall("POST", `/api/${activeResource.path}`, payload);
    if (result.ok) {
      setOutput("Registro creado.");
      setViewMode("index");
      fetchIndex();
    }
  }

  async function onUpdate() {
    if (!selectedRecord?.id) {
      setOutput("No hay registro seleccionado para actualizar.");
      return;
    }
    const payload = buildPayload(activeResource.fields, formData);
    const result = await apiCall("PUT", `/api/${activeResource.path}/${selectedRecord.id}`, payload);
    if (result.ok) {
      setOutput("Registro actualizado.");
      setViewMode("index");
      setSelectedRecord(null);
      fetchIndex();
    }
  }

  async function onDelete(item) {
    if (!window.confirm("Deseas eliminar este registro?")) return;
    const result = await apiCall("DELETE", `/api/${activeResource.path}/${item.id}`);
    if (result.ok) {
      setOutput("Registro eliminado.");
      fetchIndex();
    }
  }

  const filteredRecords = useMemo(() => {
    if (!searchTerm.trim()) return records;
    const q = searchTerm.toLowerCase();
    return records.filter((row) =>
      activeResource.columns.some((col) => String(row[col] ?? "").toLowerCase().includes(q))
    );
  }, [records, searchTerm, activeResource.columns]);

  function renderForm() {
    return (
      <div className="form-grid">
        {activeResource.fields.map((field) => (
          <label key={field.name} className="field">
            <span>{field.label}</span>
            {field.type === "checkbox" ? (
              <input
                type="checkbox"
                checked={Boolean(formData[field.name])}
                onChange={(e) => setFormData({ ...formData, [field.name]: e.target.checked })}
              />
            ) : field.optionsKey ? (
              <select
                value={formData[field.name] ?? ""}
                onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
              >
                <option value="">Selecciona una opcion...</option>
                {(catalogs[field.optionsKey] || []).map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.id} - {opt.nombre || opt.codigo || `Registro ${opt.id}`}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type={field.type}
                value={formData[field.name] ?? ""}
                onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
              />
            )}
          </label>
        ))}
      </div>
    );
  }

  function renderDetails(record) {
    const keys = Object.keys(record || {});
    return (
      <div className="table-wrap">
        <table className="details-table">
          <tbody>
            {keys.map((key) => (
              <tr key={key}>
                <th>{toLabel(key, activeResource)}</th>
                <td>{formatCell(record[key])}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div className="container">
        <div className="brand-header">
          <BrandLogo />
          <div>
            <h1>gnucannabis</h1>
            <p className="muted">Frontend funcional con layout general</p>
          </div>
        </div>
        <div className="card session-card">
          <h3>Sesion requerida</h3>
          <p className="muted">Debes iniciar sesion para acceder a los maestros.</p>
          <div className="row">
            <button className="primary" onClick={() => (window.location.href = "/login")}>
              Iniciar sesion con Auth0
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="icon-btn" onClick={() => setMenuOpen((prev) => !prev)}>
          ☰
        </button>
        <div className="topbar-brand">
          <BrandLogo small />
          <strong>gnucannabis</strong>
        </div>
        <div className="topbar-right">
          <span>{sessionUser?.name || sessionUser?.email || "usuario"}</span>
          <button
            className="danger small-btn"
            onClick={() => {
              saveToken("");
              setSessionUser(null);
              window.location.href = "/logout";
            }}
          >
            Cerrar sesion
          </button>
        </div>
      </header>

      <div className="app-body">
        <aside className={`sidebar ${menuOpen ? "open" : "collapsed"}`}>
          <h4>Maestros</h4>
          {Object.keys(RESOURCES).map((key) => (
            <button
              key={key}
              className={`menu-item ${resource === key ? "active" : ""}`}
              onClick={() => onMenuSelect(key)}
            >
              {RESOURCES[key].title}
            </button>
          ))}
        </aside>

        <main className="content">
          <div className="content-header">
            <div>
              <h2>{activeResource.title}</h2>
              <p className="muted">Modulo principal / index y formularios CRUD</p>
            </div>
            <div className="row">
              {viewMode === "index" && (
                <button className="primary" onClick={openCreate}>
                  + Crear
                </button>
              )}
              {viewMode !== "index" && (
                <button className="secondary" onClick={() => setViewMode("index")}>
                  Volver al index
                </button>
              )}
            </div>
          </div>

          {viewMode === "index" && (
            <section className="card">
              <div className="toolbar">
                <input
                  type="text"
                  placeholder={`Buscar en ${activeResource.title.toLowerCase()}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button className="secondary" onClick={fetchIndex}>
                  Refrescar
                </button>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {activeResource.columns.map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRecords.map((row) => (
                      <tr key={row.id}>
                        {activeResource.columns.map((col) => (
                          <td key={`${row.id}-${col}`}>{formatCell(row[col])}</td>
                        ))}
                        <td className="actions-cell">
                          <button className="secondary small-btn" onClick={() => openView(row)}>
                            Ver
                          </button>
                          <button className="small-btn" onClick={() => openUpdate(row)}>
                            Actualizar
                          </button>
                          <button className="danger small-btn" onClick={() => onDelete(row)}>
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    ))}
                    {filteredRecords.length === 0 && (
                      <tr>
                        <td colSpan={activeResource.columns.length + 1} className="empty-row">
                          Sin registros
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {viewMode === "view" && selectedRecord && (
            <section className="card">
              <h3>Detalle de {activeResource.title}</h3>
              {renderDetails(selectedRecord)}
            </section>
          )}

          {viewMode === "create" && (
            <section className="card">
              <h3>Crear {activeResource.title}</h3>
              {renderForm()}
              <button className="primary" onClick={onCreate}>
                Guardar
              </button>
            </section>
          )}

          {viewMode === "update" && (
            <section className="card">
              <h3>Actualizar {activeResource.title}</h3>
              {renderForm()}
              <button className="primary" onClick={onUpdate}>
                Guardar cambios
              </button>
            </section>
          )}

          <section className="card">
            <h3>Estado</h3>
            <p className="muted">{loading ? "Procesando..." : output}</p>
          </section>
        </main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
