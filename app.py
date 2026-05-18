import streamlit as st
from supabase import create_client
from datetime import date, datetime
import plotly.graph_objects as go
from collections import defaultdict

# ── Config ───────────────────────────────────────────────────
SUPA_URL = st.secrets["SUPA_URL"]
SUPA_KEY = st.secrets["SUPA_KEY"]

st.set_page_config(
    page_title="ComprasPro",
    layout="wide",
    page_icon="🛒",
    initial_sidebar_state="expanded"
)

# ── TEMA GLOBAL ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, body, .stApp { font-family: 'DM Sans', sans-serif !important; }

/* ─ Ocultar botón collapse de sidebar ─ */
[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] > div > div > div > button,
.st-emotion-cache-1cypcdb,
.st-emotion-cache-nakbow,
.eyeqlp52,
button[aria-label="Close sidebar"],
button[aria-label="Collapse sidebar"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* ─ Fondo general ─ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section[data-testid="stMain"] > div {
    background-color: #0b1520 !important;
}

/* ─ Sidebar rediseñada ─ */
[data-testid="stSidebar"] {
    background: #070f1a !important;
    border-right: 1px solid rgba(0, 194, 160, 0.12) !important;
    width: 260px !important;
    min-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
}
/* Scrollbar sidebar */
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-track { background: transparent; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: #1a3a52; border-radius: 10px; }

/* ─ Radio botones de nav rediseñados ─ */
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 20px !important;
    border-radius: 10px !important;
    margin: 0 12px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    color: #4a6b80 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(0, 194, 160, 0.07) !important;
    color: #a0c8d8 !important;
    border-color: rgba(0, 194, 160, 0.12) !important;
}
/* Ítem activo */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(0, 168, 132, 0.15) !important;
    color: #00c2a0 !important;
    border-color: rgba(0, 168, 132, 0.3) !important;
    font-weight: 600 !important;
}
/* Ocultar SOLO el círculo nativo, NO el texto */
[data-testid="stSidebar"] .stRadio label > div:first-child {
    display: none !important;
}
/* Asegurar que el texto del label sea visible */
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio label span {
    color: inherit !important;
    display: inline !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* ─ Inputs ─ */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #0d2137 !important;
    color: #e2f0ff !important;
    border: 1px solid #1e4d6b !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #00c2a0 !important;
    box-shadow: 0 0 0 2px rgba(0,194,160,0.15) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: #2a5570 !important; }

/* ─ Date input ─ */
.stDateInput [data-baseweb="input"],
.stDateInput [data-baseweb="base-input"],
.stDateInput input {
    background-color: #0d2137 !important;
    color: #e2f0ff !important;
    border: 1px solid #1e4d6b !important;
    border-radius: 8px !important;
}
.stDateInput [data-baseweb="input"] div[role="button"] { display:none !important; }

/* ─ Selectbox ─ */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #0d2137 !important;
    border: 1px solid #1e4d6b !important;
    border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] div[class*="singleValue"],
.stSelectbox [data-baseweb="select"] div[class*="placeholder"] {
    color: #e2f0ff !important;
    font-size: 13px !important;
}
[data-baseweb="popover"] ul,
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #0d2137 !important;
    border: 1px solid #1e4d6b !important;
}
[role="option"] { color: #cbd5e1 !important; font-size: 13px !important; }
[role="option"]:hover { background-color: #0a2e44 !important; color: #00c2a0 !important; }
.stSelectbox svg { color: #4a6b80 !important; fill: #4a6b80 !important; }

/* ─ Labels ─ */
.stTextInput label, .stSelectbox label, .stTextArea label,
.stDateInput label, .stNumberInput label {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #4a8fa6 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* ─ Texto general ─ */
p, .stMarkdown p, .stMarkdown span, .stCaption,
[data-testid="stMarkdownContainer"] p { color: #7fa8c0 !important; }

/* ─ Métricas ─ */
[data-testid="metric-container"] {
    background: #0d2137 !important;
    border: 1px solid #1a3d5a !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="metric-container"] label { color: #4a8fa6 !important; font-size: 11px !important; font-weight:600 !important; }
[data-testid="metric-container"] [data-testid="metric-value"] { color: #e2f0ff !important; font-weight:800 !important; font-size:22px !important; }

/* ─ Botones ─ */
.stButton button {
    background: linear-gradient(135deg, #00a884 0%, #008c6e 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 8px 18px !important;
    transition: all .2s !important;
}
.stButton button:hover {
    background: linear-gradient(135deg, #00c2a0 0%, #00a884 100%) !important;
    box-shadow: 0 4px 14px rgba(0,168,132,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ─ Tabs ─ */
.stTabs [data-baseweb="tab-list"] {
    background: #0a1628 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4a8fa6 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #00a884 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 18px !important; }

/* ─ Disabled ─ */
.stTextInput input:disabled { background-color: #091520 !important; color: #7fa8c0 !important; -webkit-text-fill-color: #7fa8c0 !important; border-color: #122b3e !important; opacity: 1 !important; }

/* ─ Cards ─ */
.cp-card {
    background: #0d2137;
    border: 1px solid #1a3d5a;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 16px;
}
.cp-card-accent { border-left: 3px solid #00a884 !important; }
.cp-card-warn   { border-left: 3px solid #f59e0b !important; }
.cp-card-danger { border-left: 3px solid #ef4444 !important; }

.cp-section {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #00a884;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1a3d5a;
}

/* ─ Tabla headers ─ */
.th { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.8px; color:#4a8fa6; }

/* ─ Badges ─ */
.badge {
    display:inline-block; padding:3px 12px; border-radius:20px;
    font-size:11px; font-weight:700; letter-spacing:.4px;
}
.b-pend  { background:#2d1f00; color:#f59e0b !important; border:1px solid #92400e; }
.b-apro  { background:#002d22; color:#00c2a0 !important; border:1px solid #065f46; }
.b-anul  { background:#2d0a0a; color:#f87171 !important; border:1px solid #991b1b; }
.b-ent   { background:#002d22; color:#00c2a0 !important; border:1px solid #065f46; }
.b-sal   { background:#2d0a0a; color:#f87171 !important; border:1px solid #991b1b; }

/* ─ Stock row styling ─ */
.stock-row {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 4px;
    background: #091a28;
    border: 1px solid #132d42;
    transition: background 0.15s;
}
.stock-row:hover { background: #0d2337; }
.stock-row-ok    { border-left: 3px solid #00a884 !important; }
.stock-row-warn  { border-left: 3px solid #f59e0b !important; }
.stock-row-cero  { border-left: 3px solid #ef4444 !important; }

/* ─ Número OC ─ */
.oc-num {
    font-family: 'DM Mono', monospace;
    font-size: 22px; font-weight:500; color:#00c2a0;
    letter-spacing: 2px;
}

/* ─ Total box ─ */
.total-strip {
    background: linear-gradient(135deg, #004d3a 0%, #006b52 100%);
    border-radius: 10px; padding: 14px 20px;
    border: 1px solid #00a884;
    text-align: right; margin-top: 10px;
}
.total-strip .lbl { font-size:10px; color:rgba(255,255,255,.6); font-weight:700; text-transform:uppercase; letter-spacing:.8px; }
.total-strip .val { font-size:28px; font-weight:900; color:#00ffd5; margin-top:2px; }

/* ─ Montos coloreados ─ */
.clr-teal  { color:#00c2a0 !important; font-weight:700; }
.clr-red   { color:#f87171 !important; font-weight:700; }
.clr-amber { color:#fbbf24 !important; font-weight:700; }
.clr-dim   { color:#4a6b80 !important; }
.clr-main  { color:#e2f0ff !important; font-weight:600; }
.clr-muted { color:#7fa8c0 !important; }

/* ─ Code chip ─ */
.chip {
    font-family: 'DM Mono', monospace; background:#091520; color:#00c2a0 !important;
    padding:2px 8px; border-radius:5px; font-size:12px;
    border:1px solid #1a3d5a;
}

/* ─ Empty ─ */
.empty { color:#2a5570 !important; text-align:center; padding:30px 0; font-size:13px; font-style:italic; }

/* ─ KPI mini card ─ */
.kpi-mini {
    background: #091a28;
    border: 1px solid #1a3d5a;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.kpi-mini .kv { font-size: 24px; font-weight: 800; }
.kpi-mini .kl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .8px; color: #4a8fa6; margin-top: 2px; }

/* ─ Barra de stock visual ─ */
.stock-bar-bg { background:#0f2a3d; border-radius:4px; height:6px; width:100%; margin-top:4px; overflow:hidden; }
.stock-bar-fill { height:6px; border-radius:4px; }

hr { border-color: #1a3d5a !important; margin: 6px 0 10px !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Conexión ─────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return create_client(SUPA_URL, SUPA_KEY)

sb = get_client()

# ── Helpers de carga ─────────────────────────────────────────
def cargar_proveedores():
    return sb.table("proveedor").select("id,nombre,ruc,telefono").order("nombre").execute().data or []

@st.cache_data(ttl=60)
def cargar_productos():
    return sb.table("producto").select(
        "id,codigo,nombre,unidad,precio_unitario,categoria:id_categoria(nombre)"
    ).order("codigo").execute().data or []

@st.cache_data(ttl=30)
def cargar_numeros_oc():
    return [r["numero"] for r in (sb.table("orden_compra").select("numero").order("fecha", desc=True).execute().data or [])]

@st.cache_data(ttl=20)
def cargar_stock():
    movs = sb.table("movimiento").select(
        "tipo,cantidad,id_producto,"
        "producto:id_producto(id,codigo,nombre,unidad,stock_minimo,categoria:id_categoria(nombre))"
    ).execute().data or []
    ENTRADAS = {"COMPRA","DEVOLUCION"}
    SALIDAS  = {"VENTA","INHABILITADO","USO_INTERNO"}
    prods = {}
    for m in movs:
        p   = m.get("producto") or {}
        pid = p.get("id") or m.get("id_producto")
        if not pid: continue
        if pid not in prods:
            prods[pid] = {
                "id_producto": pid,
                "codigo":   p.get("codigo","—"),
                "nombre":   p.get("nombre","—"),
                "unidad":   p.get("unidad","—"),
                "categoria":(p.get("categoria") or {}).get("nombre","Sin cat."),
                "stock_minimo": p.get("stock_minimo") or 0,
                "entradas": 0, "salidas": 0,
            }
        if m["tipo"] in ENTRADAS: prods[pid]["entradas"] += m["cantidad"]
        elif m["tipo"] in SALIDAS: prods[pid]["salidas"]  += m["cantidad"]
    result = []
    for p in prods.values():
        p["stock_actual"] = p["entradas"] - p["salidas"]
        result.append(p)
    return sorted(result, key=lambda x: x["nombre"])

@st.cache_data(ttl=20)
def cargar_kardex(pid):
    # Query sin join a id_orden para evitar error de FK
    movs = sb.table("movimiento").select(
        "id,fecha,tipo,cantidad,persona_contacto,observacion,created_at,id_orden"
    ).eq("id_producto", pid).order("fecha").order("created_at").execute().data or []

    # Obtener números de OC por separado si hay id_orden
    oc_map = {}
    ids_oc = list({m["id_orden"] for m in movs if m.get("id_orden")})
    if ids_oc:
        try:
            oc_rows = sb.table("orden_compra").select("id,numero").in_("id", ids_oc).execute().data or []
            oc_map = {r["id"]: r["numero"] for r in oc_rows}
        except Exception:
            pass

    ENTRADAS = {"COMPRA","DEVOLUCION"}
    saldo, rows = 0, []
    for i, m in enumerate(movs, 1):
        es_e = m["tipo"] in ENTRADAS
        e = m["cantidad"] if es_e else 0
        s = m["cantidad"] if not es_e else 0
        saldo += e - s
        rows.append({
            "nro": i, "fecha": m["fecha"], "tipo": m["tipo"],
            "entrada": e, "salida": s, "saldo": saldo,
            "persona": m.get("persona_contacto","—"),
            "oc":      oc_map.get(m.get("id_orden"), "—"),
            "obs":     m.get("observacion","—"),
        })
    return rows

def gen_numero():
    ts = str(int(datetime.now().timestamp()))[-5:]
    return f"OC-{date.today().year}-{ts}"

TIPOS_E = ["COMPRA","DEVOLUCION"]
TIPOS_S = ["VENTA","INHABILITADO","USO_INTERNO"]
TODOS   = TIPOS_E + TIPOS_S
LABEL   = {
    "COMPRA":"📥 Compra","DEVOLUCION":"↩️ Devolución",
    "VENTA":"📤 Venta","INHABILITADO":"🚫 Inhabilitado","USO_INTERNO":"🔧 Uso Interno",
}

# ── Session state ─────────────────────────────────────────────
for k, v in {
    "detalle": [], "oc_id": None, "oc_num": gen_numero(),
    "estado": "PENDIENTE", "guardada": False,
    "show_cat": False, "busq": "", "prov_idx": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════
# SIDEBAR — navegación lateral rediseñada
# ════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo / branding
    st.markdown("""
    <div style="padding: 32px 24px 24px; border-bottom: 1px solid rgba(0,194,160,0.1);">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="background: linear-gradient(135deg, #00a884 0%, #005c47 100%);
                        width:42px; height:42px; border-radius:12px;
                        display:flex; align-items:center; justify-content:center;
                        font-size:20px; flex-shrink:0; box-shadow:0 4px 14px rgba(0,168,132,0.3);">🛒</div>
            <div>
                <div style="font-size:15px; font-weight:800; color:#e2f0ff; letter-spacing:.5px; line-height:1.2;">ComprasPro</div>
                <div style="font-size:10px; color:#2a5570; letter-spacing:1.5px; text-transform:uppercase; margin-top:1px;">Sistema de Compras</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Sección NAVEGACIÓN label
    st.markdown("""
    <div style="padding:0 24px 8px;">
        <span style="font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#1e4d6b;">Navegación</span>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Menú",
        ["📝  Nueva Orden", "🔍  Consultar Órdenes", "🔄  Movimientos", "📦  Stock & Kardex", "📊  Reportes"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Divider
    st.markdown("""
    <div style="margin:0 24px; height:1px; background:linear-gradient(90deg,transparent,rgba(0,194,160,0.15),transparent);"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Sección RESUMEN GLOBAL
    st.markdown("""
    <div style="padding:0 24px 10px;">
        <span style="font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#1e4d6b;">Resumen Global</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        _ocs   = sb.table("orden_compra").select("estado").execute().data or []
        _stock = cargar_stock()

        _pend     = sum(1 for o in _ocs if o["estado"] == "PENDIENTE")
        _apro     = sum(1 for o in _ocs if o["estado"] == "APROBADA")
        _sin_stk  = sum(1 for s in _stock if int(s["stock_actual"]) <= 0)
        _bajo_stk = sum(1 for s in _stock if 0 < int(s["stock_actual"]) <= int(s.get("stock_minimo") or 0))

        def _kpi_sb(icon, label, value, color):
            return f"""
            <div style="display:flex; align-items:center; justify-content:space-between;
                        padding:8px 12px; margin-bottom:5px; border-radius:8px;
                        background:#091520; border:1px solid #132d42;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:14px;">{icon}</span>
                    <span style="font-size:11px; color:#4a6b80; font-weight:500;">{label}</span>
                </div>
                <span style="font-size:14px; font-weight:800; color:{color};">{value}</span>
            </div>"""

        st.markdown(
            "<div style='margin:0 12px;'>"
            + _kpi_sb("📋", "OC Pendientes",  _pend,     "#f59e0b")
            + _kpi_sb("✅", "OC Aprobadas",   _apro,     "#00c2a0")
            + _kpi_sb("❌", "Sin stock",       _sin_stk,  "#f87171")
            + _kpi_sb("⚠️", "Stock bajo",      _bajo_stk, "#fbbf24")
            + "</div>",
            unsafe_allow_html=True
        )
    except Exception:
        st.markdown("<div style='padding:0 24px;'><span style='font-size:11px;color:#1e4d6b;'>No disponible</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Divider
    st.markdown("""
    <div style="margin:0 24px; height:1px; background:linear-gradient(90deg,transparent,rgba(0,194,160,0.15),transparent);"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Info versión
    st.markdown("""
    <div style="padding:0 24px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <div style="width:6px;height:6px;border-radius:50%;background:#00c2a0;
                        box-shadow:0 0 6px #00c2a0;flex-shrink:0;"></div>
            <span style="font-size:11px; color:#2a5570;">Sistema en línea</span>
        </div>
        <div style="font-size:10px; color:#1a3d5a; letter-spacing:.5px;">v2.0 · ComprasPro</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PÁGINA 1 — NUEVA ORDEN
# ════════════════════════════════════════════════════════════
if "Nueva Orden" in pagina:

    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:24px;">
        <div style="background:linear-gradient(135deg,#00a884,#006b52);
                    border-radius:12px; padding:10px 14px; font-size:22px;
                    box-shadow:0 4px 14px rgba(0,168,132,0.25);">📝</div>
        <div>
            <div style="font-size:20px; font-weight:800; color:#e2f0ff;">Nueva Orden de Compra</div>
            <div style="font-size:12px; color:#2a5570;">Registra y gestiona una orden de compra</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    a1, a2, a3, a4, _ = st.columns([1.2, 1, 1, 1, 2.6])
    guardar_click = a1.button("💾 Guardar", type="primary", use_container_width=True,
                               disabled=st.session_state.guardada)
    aprobar_click = a2.button("✅ Aprobar", use_container_width=True,
                               disabled=not st.session_state.guardada or st.session_state.estado != "PENDIENTE")
    anular_click  = a3.button("🚫 Anular",  use_container_width=True,
                               disabled=not st.session_state.guardada or st.session_state.estado == "ANULADA")
    nueva_click   = a4.button("➕ Limpiar", use_container_width=True)

    if nueva_click:
        for k, v in {"detalle":[], "oc_id":None, "oc_num":gen_numero(), "estado":"PENDIENTE",
                     "guardada":False, "show_cat":False, "busq":"", "prov_idx":0}.items():
            st.session_state[k] = v
        st.rerun()

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="cp-card cp-card-accent">', unsafe_allow_html=True)
    st.markdown('<div class="cp-section">📋 Cabecera de la Orden</div>', unsafe_allow_html=True)

    proveedores = cargar_proveedores()
    opciones_pv = ["— Seleccionar proveedor —"] + [f"{p['ruc']} — {p['nombre']}" for p in proveedores]
    prov_map    = {f"{p['ruc']} — {p['nombre']}": p for p in proveedores}

    h1, h2, h3, h4 = st.columns([1.4, 1, 2.5, 1])
    with h1:
        st.markdown(
            "<div style='font-size:10px;font-weight:600;text-transform:uppercase;color:#4a8fa6;letter-spacing:.8px;margin-bottom:6px;'>Número OC</div>"
            f"<div class='oc-num'>{st.session_state.oc_num}</div>",
            unsafe_allow_html=True
        )
    with h2:
        fecha_oc = st.date_input("Fecha", value=date.today(), disabled=st.session_state.guardada)
    with h3:
        prov_lbl = st.selectbox("Proveedor", opciones_pv, index=st.session_state.prov_idx,
                                 disabled=st.session_state.guardada, key="sel_prov")
        prov_sel = prov_map.get(prov_lbl)
        if prov_lbl in opciones_pv:
            st.session_state.prov_idx = opciones_pv.index(prov_lbl)
    with h4:
        st.text_input("Teléfono", value=prov_sel["telefono"] if prov_sel else "", disabled=True)

    obs = st.text_area("Observación", placeholder="Notas adicionales...", height=65,
                        disabled=st.session_state.guardada, key="obs")

    if not st.session_state.guardada:
        lbl_cat = "🔼 Ocultar catálogo" if st.session_state.show_cat else "🔽 Agregar del catálogo"
        col_btn, _ = st.columns([2, 6])
        if col_btn.button(lbl_cat, use_container_width=True):
            st.session_state.show_cat = not st.session_state.show_cat
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Catálogo ──────────────────────────────────────────────
    if st.session_state.show_cat and not st.session_state.guardada:
        productos = cargar_productos()
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section">🗂️ Catálogo de Productos</div>', unsafe_allow_html=True)

        bq = st.text_input("🔎 Buscar producto", value=st.session_state.busq,
                            placeholder="Código, nombre o categoría...", key="bq_cat")
        st.session_state.busq = bq
        filt = [p for p in productos if
                bq.lower() in p["nombre"].lower() or bq.lower() in p["codigo"].lower() or
                bq.lower() in ((p["categoria"]["nombre"].lower()) if p.get("categoria") else "")
               ] if bq else productos

        if filt:
            hc = st.columns([1, 2.8, 0.7, 1.4, 0.9, 1.2, 1])
            for col, h in zip(hc, ["Código","Nombre","Und.","Categoría","Cantidad","P. Unit.","Acción"]):
                col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            for p in filt:
                rc = st.columns([1, 2.8, 0.7, 1.4, 0.9, 1.2, 1])
                rc[0].markdown(f"<span class='chip'>{p['codigo']}</span>", unsafe_allow_html=True)
                rc[1].markdown(f"<span class='clr-main'>{p['nombre']}</span>", unsafe_allow_html=True)
                rc[2].markdown(f"<span class='clr-dim'>{p['unidad']}</span>", unsafe_allow_html=True)
                rc[3].markdown(f"<span class='clr-dim'>{p['categoria']['nombre'] if p.get('categoria') else '—'}</span>", unsafe_allow_html=True)
                cant   = rc[4].number_input("", min_value=1, value=1, key=f"c_{p['id']}", label_visibility="collapsed")
                precio = rc[5].number_input("", min_value=0.0, value=float(p["precio_unitario"]),
                                             step=0.01, format="%.2f", key=f"p_{p['id']}", label_visibility="collapsed")
                if rc[6].button("＋", key=f"ag_{p['id']}"):
                    if any(d["id_producto"] == p["id"] for d in st.session_state.detalle):
                        st.toast(f"⚠️ '{p['nombre']}' ya está en el detalle.", icon="⚠️")
                    else:
                        st.session_state.detalle.append({
                            "id_producto": p["id"], "codigo": p["codigo"],
                            "nombre": p["nombre"], "unidad": p["unidad"],
                            "cantidad": cant, "precio_unitario": precio,
                        })
                        st.toast(f"✅ Agregado: {p['nombre']}", icon="📦")
                    st.rerun()
        else:
            st.markdown("<p class='empty'>Sin resultados para esa búsqueda.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Detalle ───────────────────────────────────────────────
    st.markdown('<div class="cp-card">', unsafe_allow_html=True)
    st.markdown('<div class="cp-section">📄 Detalle de la Orden</div>', unsafe_allow_html=True)

    if not st.session_state.detalle:
        st.markdown("<p class='empty'>Agrega productos con el botón «Agregar del catálogo»</p>", unsafe_allow_html=True)
    else:
        hd = st.columns([0.4, 1, 3, 0.7, 1, 1.2, 1.3, 0.6])
        for col, h in zip(hd, ["#","Código","Descripción","Und.","Cant.","P. Unit.","Subtotal","Del."]):
            col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        to_del = []
        for i, item in enumerate(st.session_state.detalle):
            cd = st.columns([0.4, 1, 3, 0.7, 1, 1.2, 1.3, 0.6])
            cd[0].markdown(f"<span class='clr-dim'>{i+1}</span>", unsafe_allow_html=True)
            cd[1].markdown(f"<span class='chip'>{item['codigo']}</span>", unsafe_allow_html=True)
            cd[2].markdown(f"<span class='clr-main'>{item['nombre']}</span>", unsafe_allow_html=True)
            cd[3].markdown(f"<span class='clr-dim'>{item['unidad']}</span>", unsafe_allow_html=True)
            cd[4].markdown(f"<span class='clr-main'>{int(item['cantidad'])}</span>", unsafe_allow_html=True)
            cd[5].markdown(f"<span class='clr-dim'>S/{item['precio_unitario']:.2f}</span>", unsafe_allow_html=True)
            sub = item["cantidad"] * item["precio_unitario"]
            cd[6].markdown(f"<span class='clr-teal'>S/{sub:,.2f}</span>", unsafe_allow_html=True)
            if not st.session_state.guardada:
                if cd[7].button("✕", key=f"rm_{i}"):
                    to_del.append(i)
            else:
                cd[7].markdown("<span class='clr-dim'>—</span>", unsafe_allow_html=True)
        for idx in reversed(to_del):
            st.session_state.detalle.pop(idx)
        if to_del: st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    sub_v   = sum(d["cantidad"] * d["precio_unitario"] for d in st.session_state.detalle)
    igv_v   = sub_v * 0.18
    total_v = sub_v + igv_v

    c_res, c_tot = st.columns(2)
    with c_res:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section">📊 Resumen</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        r1.metric("Ítems", len(st.session_state.detalle))
        r2.metric("Unidades", int(sum(d["cantidad"] for d in st.session_state.detalle)))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_tot:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section">💰 Totales</div>', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        t1.metric("Subtotal", f"S/ {sub_v:,.2f}")
        t2.metric("IGV 18%",  f"S/ {igv_v:,.2f}")
        st.markdown(f"""
        <div class="total-strip">
            <div class="lbl">TOTAL ORDEN</div>
            <div class="val">S/ {total_v:,.2f}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if guardar_click:
        if not prov_sel:
            st.error("⚠️ Selecciona un proveedor.")
        elif not st.session_state.detalle:
            st.error("⚠️ Agrega al menos un producto.")
        else:
            try:
                res = sb.table("orden_compra").insert({
                    "numero": st.session_state.oc_num,
                    "id_proveedor": prov_sel["id"],
                    "fecha": str(fecha_oc),
                    "estado": "PENDIENTE",
                }).execute()
                if res.data:
                    oc = res.data[0]
                    st.session_state.oc_id    = oc["id"]
                    st.session_state.estado   = "PENDIENTE"
                    st.session_state.guardada = True
                    st.session_state.show_cat = False
                    items = [{"id_orden": oc["id"], "id_producto": d["id_producto"],
                              "cantidad": d["cantidad"], "precio_unitario": d["precio_unitario"]}
                             for d in st.session_state.detalle if d["id_producto"]]
                    if items:
                        sb.table("detalle_orden").insert(items).execute()
                    st.success(f"✅ Orden {oc['numero']} guardada.")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    if aprobar_click and st.session_state.oc_id:
        try:
            sb.table("orden_compra").update({"estado":"APROBADA"}).eq("id", st.session_state.oc_id).execute()
            st.session_state.estado = "APROBADA"
            st.success("✅ Orden aprobada.")
            st.rerun()
        except Exception as e: st.error(f"❌ {e}")

    if anular_click and st.session_state.oc_id:
        try:
            sb.table("orden_compra").update({"estado":"ANULADA"}).eq("id", st.session_state.oc_id).execute()
            st.session_state.estado = "ANULADA"
            st.warning("🚫 Orden anulada.")
            st.rerun()
        except Exception as e: st.error(f"❌ {e}")

# ════════════════════════════════════════════════════════════
# PÁGINA 2 — CONSULTAR ÓRDENES
# ════════════════════════════════════════════════════════════
elif "Consultar" in pagina:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;">
        <div style="background:linear-gradient(135deg,#00a884,#006b52);border-radius:12px;padding:10px 14px;font-size:22px;box-shadow:0 4px 14px rgba(0,168,132,0.25);">🔍</div>
        <div>
            <div style="font-size:20px;font-weight:800;color:#e2f0ff;">Consultar Órdenes</div>
            <div style="font-size:12px;color:#2a5570;">Busca y gestiona órdenes existentes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cp-card cp-card-accent">', unsafe_allow_html=True)
    st.markdown('<div class="cp-section">🔎 Filtros</div>', unsafe_allow_html=True)

    nums_oc = cargar_numeros_oc()
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1, 1])
    with f1:
        sel_num = st.selectbox(f"N° Orden ({len(nums_oc)} total)", ["— Todas —"] + nums_oc, key="fn")
        f_num   = "" if sel_num == "— Todas —" else sel_num
    with f2:
        pvs_c   = cargar_proveedores()
        ops_pvc = ["— Todos —"] + [f"{p['ruc']} — {p['nombre']}" for p in pvs_c]
        f_prov  = st.selectbox("Proveedor", ops_pvc, key="fp")
    with f3:
        f_est = st.selectbox("Estado", ["— Todos —","PENDIENTE","APROBADA","ANULADA"], key="fe")
    with f4:
        f_fecha = st.date_input("Desde", value=None, key="ff")

    bc, bl, _ = st.columns([1,1,5])
    buscar  = bc.button("🔍 Buscar", type="primary", use_container_width=True, key="btn_b")
    limpiar = bl.button("🗑️ Limpiar", use_container_width=True, key="btn_l")
    st.markdown('</div>', unsafe_allow_html=True)

    if limpiar:
        for k in ["fn","fp","fe","ff","q_activa"]:
            st.session_state.pop(k, None)
        cargar_numeros_oc.clear()
        st.rerun()

    if buscar or st.session_state.get("q_activa"):
        st.session_state["q_activa"] = True
        try:
            q = sb.table("orden_compra").select(
                "id,numero,fecha,estado,proveedor:id_proveedor(nombre,ruc)"
            ).order("fecha", desc=True)
            if f_num: q = q.eq("numero", f_num)
            if f_est != "— Todos —": q = q.eq("estado", f_est)
            if f_fecha: q = q.gte("fecha", str(f_fecha))
            ordenes = q.execute().data or []
            if f_prov != "— Todos —":
                ruc_s = f_prov.split(" — ")[0]
                ordenes = [o for o in ordenes if (o.get("proveedor") or {}).get("ruc") == ruc_s]

            st.markdown(f'<div class="cp-card"><div class="cp-section">📋 {len(ordenes)} orden(es) encontrada(s)</div>', unsafe_allow_html=True)
            if not ordenes:
                st.markdown("<p class='empty'>No hay órdenes con esos filtros.</p>", unsafe_allow_html=True)
            else:
                hh = st.columns([1.4, 1, 2.2, 1.2, 0.8, 0.8])
                for col, h in zip(hh, ["N° Orden","Fecha","Proveedor","Estado","Ver","Acción"]):
                    col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                for oc in ordenes:
                    ro = st.columns([1.4, 1, 2.2, 1.2, 0.8, 0.8])
                    ro[0].markdown(f"<span style='font-family:DM Mono,monospace;font-weight:500;color:#00c2a0;'>{oc['numero']}</span>", unsafe_allow_html=True)
                    ro[1].markdown(f"<span class='clr-dim'>{oc['fecha']}</span>", unsafe_allow_html=True)
                    ro[2].markdown(f"<span class='clr-main'>{(oc.get('proveedor') or {}).get('nombre','—')}</span>", unsafe_allow_html=True)
                    bc_ = {"PENDIENTE":"b-pend","APROBADA":"b-apro","ANULADA":"b-anul"}.get(oc["estado"],"b-pend")
                    ro[3].markdown(f"<span class='badge {bc_}'>{oc['estado']}</span>", unsafe_allow_html=True)
                    if ro[4].button("👁️", key=f"v_{oc['id']}"):
                        st.session_state["det_id"] = oc["id"]
                        st.session_state["det_num"] = oc["numero"]
                    if oc["estado"] == "PENDIENTE":
                        if ro[5].button("✅", key=f"ap_{oc['id']}"):
                            sb.table("orden_compra").update({"estado":"APROBADA"}).eq("id",oc["id"]).execute()
                            st.toast(f"✅ {oc['numero']} aprobada"); st.rerun()
                    elif oc["estado"] == "APROBADA":
                        if ro[5].button("🚫", key=f"an_{oc['id']}"):
                            sb.table("orden_compra").update({"estado":"ANULADA"}).eq("id",oc["id"]).execute()
                            st.toast(f"🚫 {oc['numero']} anulada"); st.rerun()
                    else:
                        ro[5].markdown("<span class='clr-dim'>—</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.get("det_id"):
                did  = st.session_state["det_id"]
                dnum = st.session_state.get("det_num","")
                items_d = sb.table("detalle_orden").select(
                    "cantidad,precio_unitario,subtotal,producto:id_producto(codigo,nombre,unidad)"
                ).eq("id_orden", did).execute().data or []
                st.markdown(f'<div class="cp-card cp-card-accent"><div class="cp-section">📄 Detalle — {dnum}</div>', unsafe_allow_html=True)
                if not items_d:
                    st.markdown("<p class='empty'>Sin ítems.</p>", unsafe_allow_html=True)
                else:
                    hd2 = st.columns([1, 3, 0.8, 1, 1.2, 1.4])
                    for col, h in zip(hd2, ["Código","Producto","Und.","Cant.","P. Unit.","Subtotal"]):
                        col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    tot_d = 0
                    for d in items_d:
                        pr = d.get("producto") or {}
                        rd = st.columns([1, 3, 0.8, 1, 1.2, 1.4])
                        rd[0].markdown(f"<span class='chip'>{pr.get('codigo','—')}</span>", unsafe_allow_html=True)
                        rd[1].markdown(f"<span class='clr-main'>{pr.get('nombre','—')}</span>", unsafe_allow_html=True)
                        rd[2].markdown(f"<span class='clr-dim'>{pr.get('unidad','—')}</span>", unsafe_allow_html=True)
                        rd[3].markdown(f"<span class='clr-main'>{int(d['cantidad'])}</span>", unsafe_allow_html=True)
                        rd[4].markdown(f"<span class='clr-dim'>S/{float(d['precio_unitario']):.2f}</span>", unsafe_allow_html=True)
                        sub = float(d.get("subtotal") or d["cantidad"]*d["precio_unitario"])
                        rd[5].markdown(f"<span class='clr-teal'>S/{sub:,.2f}</span>", unsafe_allow_html=True)
                        tot_d += sub
                    st.markdown("<hr>", unsafe_allow_html=True)
                    igv_d = tot_d * .18
                    x1, x2 = st.columns(2)
                    x1.metric("Subtotal", f"S/ {tot_d:,.2f}")
                    x2.metric("IGV 18%", f"S/ {igv_d:,.2f}")
                    st.markdown(f'<div class="total-strip"><div class="lbl">TOTAL CON IGV</div><div class="val">S/ {tot_d+igv_d:,.2f}</div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if st.button("✖️ Cerrar detalle"):
                    del st.session_state["det_id"]
                    st.rerun()
        except Exception as e:
            st.error(f"❌ {e}")
    else:
        st.markdown("<p class='empty' style='padding:40px;'>Usa los filtros y presiona Buscar.</p>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PÁGINA 3 — MOVIMIENTOS
# ════════════════════════════════════════════════════════════
elif "Movimientos" in pagina:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;">
        <div style="background:linear-gradient(135deg,#00a884,#006b52);border-radius:12px;padding:10px 14px;font-size:22px;box-shadow:0 4px 14px rgba(0,168,132,0.25);">🔄</div>
        <div>
            <div style="font-size:20px;font-weight:800;color:#e2f0ff;">Movimientos de Inventario</div>
            <div style="font-size:12px;color:#2a5570;">Registra entradas y salidas de productos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cp-card cp-card-accent">', unsafe_allow_html=True)
    st.markdown('<div class="cp-section">➕ Registrar Movimiento</div>', unsafe_allow_html=True)
    prods_m = cargar_productos()
    pmap_m  = {f"{p['codigo']} — {p['nombre']}": p for p in prods_m}
    ops_m   = ["— Seleccionar producto —"] + list(pmap_m.keys())

    m1, m2, m3 = st.columns([1.5, 1.5, 1])
    with m1:
        tipo_m = st.selectbox("Tipo", ["— Seleccionar —"] + [LABEL[t] for t in TODOS], key="m_tipo")
        tipo_r = next((t for t in TODOS if LABEL.get(t) == tipo_m), None)
        es_e   = tipo_r in TIPOS_E
    with m2:
        prod_lm = st.selectbox("Producto", ops_m, key="m_prod")
        prod_m  = pmap_m.get(prod_lm)
    with m3:
        fecha_m = st.date_input("Fecha", value=date.today(), key="m_fecha")

    m4, m5, m6 = st.columns([1, 1.5, 2])
    with m4: cant_m = st.number_input("Cantidad", min_value=1, value=1, key="m_cant")
    with m5: pers_m = st.text_input("Recibido de / Entregado a", placeholder="Nombre...", key="m_pers")
    with m6: obs_m  = st.text_area("Observación", placeholder="Detalle...", height=65, key="m_obs")

    id_oc_m = None
    if tipo_r == "COMPRA":
        nums_oc_m = cargar_numeros_oc()
        oc_sel = st.selectbox("Vincular a OC (opcional)", ["— Sin vincular —"] + nums_oc_m, key="m_oc")
        if oc_sel != "— Sin vincular —":
            r = sb.table("orden_compra").select("id").eq("numero", oc_sel).execute()
            if r.data: id_oc_m = r.data[0]["id"]

    if st.button("💾 Registrar movimiento", type="primary", use_container_width=False, key="btn_rm"):
        errs = []
        if not tipo_r: errs.append("Selecciona el tipo.")
        if not prod_m: errs.append("Selecciona el producto.")
        if not pers_m.strip(): errs.append("Indica la persona/área.")
        if errs:
            for e in errs: st.error(f"⚠️ {e}")
        else:
            try:
                sb.table("movimiento").insert({
                    "fecha": str(fecha_m),
                    "tipo": tipo_r,
                    "motivo": tipo_r,
                    "cantidad": cant_m,
                    "id_producto": prod_m["id"],
                    "persona_contacto": pers_m.strip(),
                    "observacion": obs_m.strip() or None,
                    "id_orden": id_oc_m,
                }).execute()
                cargar_stock.clear()
                cargar_kardex.clear()
                st.success(f"✅ Movimiento registrado: {LABEL[tipo_r]} — {prod_m['nombre']} x{int(cant_m)}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Historial ─────────────────────────────────────────────
    st.markdown('<div class="cp-card">', unsafe_allow_html=True)
    st.markdown('<div class="cp-section">📋 Historial de Movimientos</div>', unsafe_allow_html=True)

    hf1, hf2, hf3, hf4, hf5 = st.columns([1.4, 1.8, 1, 1, 0.8])
    with hf1:
        ft   = st.selectbox("Tipo", ["— Todos —"] + [LABEL[t] for t in TODOS], key="ht")
        ft_r = next((t for t in TODOS if LABEL.get(t) == ft), None)
    with hf2:
        # ── Selectbox de producto igual que en registro ──
        ops_h   = ["— Todos los productos —"] + list(pmap_m.keys())
        prod_h_lbl = st.selectbox("Producto", ops_h, key="hp_sel")
        prod_h  = pmap_m.get(prod_h_lbl)          # None si "— Todos —"
    with hf3:
        fd = st.date_input("Desde", value=None, key="hd")
    with hf4:
        fh = st.date_input("Hasta", value=None, key="hh_")
    with hf5:
        st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
        filtrar = st.button("🔍 Filtrar", type="primary", use_container_width=True, key="btn_fh")

    if filtrar or st.session_state.get("h_activo"):
        st.session_state["h_activo"] = True
        try:
            qh = sb.table("movimiento").select(
                "fecha,tipo,cantidad,persona_contacto,observacion,"
                "producto:id_producto(codigo,nombre,unidad)"
            ).order("fecha", desc=True).order("created_at", desc=True)

            if ft_r:       qh = qh.eq("tipo", ft_r)
            if prod_h:     qh = qh.eq("id_producto", prod_h["id"])
            if fd:         qh = qh.gte("fecha", str(fd))
            if fh:         qh = qh.lte("fecha", str(fh))

            movs = qh.execute().data or []

            entradas = [m for m in movs if m["tipo"] in TIPOS_E]
            salidas  = [m for m in movs if m["tipo"] in TIPOS_S]
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Total",       len(movs))
            s2.metric("📥 Entradas", len(entradas))
            s3.metric("📤 Salidas",  len(salidas))
            s4.metric("Neto", int(
                sum(m["cantidad"] for m in entradas) -
                sum(m["cantidad"] for m in salidas)
            ))
            st.markdown("<hr>", unsafe_allow_html=True)

            if not movs:
                st.markdown("<p class='empty'>Sin movimientos con esos filtros.</p>", unsafe_allow_html=True)
            else:
                ws   = [0.9, 1.5, 2.5, 0.6, 0.9, 1.8, 2]
                hrow = st.columns(ws)
                for col, h in zip(hrow, ["Fecha","Tipo","Producto","Und.","Cant.","Persona","Obs."]):
                    col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0 8px;'>", unsafe_allow_html=True)

                for mv in movs:
                    pr   = mv.get("producto") or {}
                    fila = st.columns(ws)

                    # ── Fecha limpia ──────────────────────────────
                    fecha_raw = mv.get("fecha", "")
                    fecha_fmt = str(fecha_raw)[:10]   # "2026-05-18"

                    fila[0].markdown(f"<span class='clr-dim'>{fecha_fmt}</span>", unsafe_allow_html=True)
                    bc2 = "b-ent" if mv["tipo"] in TIPOS_E else "b-sal"
                    fila[1].markdown(f"<span class='badge {bc2}'>{LABEL.get(mv['tipo'], mv['tipo'])}</span>", unsafe_allow_html=True)
                    fila[2].markdown(f"<span class='clr-main'>{pr.get('nombre','—')}</span>", unsafe_allow_html=True)
                    fila[3].markdown(f"<span class='clr-dim'>{pr.get('unidad','—')}</span>", unsafe_allow_html=True)
                    signo = "+" if mv["tipo"] in TIPOS_E else "-"
                    cls2  = "clr-teal" if mv["tipo"] in TIPOS_E else "clr-red"
                    fila[4].markdown(f"<span class='{cls2}'>{signo}{int(mv['cantidad'])}</span>", unsafe_allow_html=True)
                    fila[5].markdown(f"<span class='clr-dim'>{mv.get('persona_contacto','—')}</span>", unsafe_allow_html=True)
                    fila[6].markdown(f"<span class='clr-dim'>{mv.get('observacion','—')}</span>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ {e}")
    else:
        st.markdown("<p class='empty'>Presiona Filtrar para ver el historial.</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PÁGINA 4 — STOCK & KARDEX (REDISEÑADA)
# ════════════════════════════════════════════════════════════
elif "Stock" in pagina:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;">
        <div style="background:linear-gradient(135deg,#00a884,#006b52);border-radius:12px;padding:10px 14px;font-size:22px;box-shadow:0 4px 14px rgba(0,168,132,0.25);">📦</div>
        <div>
            <div style="font-size:20px;font-weight:800;color:#e2f0ff;">Stock & Kardex</div>
            <div style="font-size:12px;color:#2a5570;">Control de inventario en tiempo real</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        sd = cargar_stock()
    except Exception as e:
        st.error(f"❌ Error cargando stock: {e}")
        sd = []

    if sd:
        ok_l   = [s for s in sd if int(s["stock_actual"]) > int(s.get("stock_minimo") or 0)]
        bajo_l = [s for s in sd if 0 < int(s["stock_actual"]) <= int(s.get("stock_minimo") or 0)]
        cero_l = [s for s in sd if int(s["stock_actual"]) <= 0]

        # ── KPIs superiores ───────────────────────────────────────
        k1, k2, k3, k4, k5 = st.columns(5)
        kpi_data = [
            (k1, str(len(sd)), "Productos", "#7fa8c0"),
            (k2, str(len(ok_l)), "Stock OK", "#00c2a0"),
            (k3, str(len(bajo_l)), "Stock Bajo", "#f59e0b"),
            (k4, str(len(cero_l)), "Sin Stock", "#f87171"),
            (k5, f"{sum(s['stock_actual'] for s in sd):,}", "Unidades Total", "#a78bfa"),
        ]
        for col, val, lbl, color in kpi_data:
            col.markdown(f"""
            <div class="kpi-mini" style="border-top:3px solid {color};">
                <div class="kv" style="color:{color};">{val}</div>
                <div class="kl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── Layout: Stock (izq) | Kardex (der) ────────────────────
    col_st, col_kd = st.columns([1.4, 1])

    with col_st:
        st.markdown('<div class="cp-card cp-card-accent">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section">🏬 Stock General</div>', unsafe_allow_html=True)

        # Filtros inline
        fc1, fc2, fc3 = st.columns([1.6, 1, 0.6])
        with fc1:
            busq_s = st.text_input("", placeholder="🔎  Buscar producto...", key="s_busq", label_visibility="collapsed")
        with fc2:
            if sd:
                cats_s = sorted(set(s.get("categoria","Sin cat.") for s in sd))
                cat_sel_s = st.selectbox("", ["— Todas las categorías —"] + cats_s, key="s_cat", label_visibility="collapsed")
            else:
                cat_sel_s = "— Todas las categorías —"
        with fc3:
            if st.button("🔄 Actualizar", key="ref_s", use_container_width=True):
                cargar_stock.clear(); cargar_kardex.clear(); st.rerun()

        if not sd:
            st.markdown("<p class='empty'>Sin movimientos registrados aún.</p>", unsafe_allow_html=True)
        else:
            # Filtrar
            sf = sd
            if busq_s:
                sf = [s for s in sf if busq_s.lower() in s["nombre"].lower() or busq_s.lower() in s["codigo"].lower()]
            if cat_sel_s != "— Todas las categorías —":
                sf = [s for s in sf if (s.get("categoria") or "Sin cat.") == cat_sel_s]

            # Ordenar: primero sin stock, luego bajo, luego ok
            sf_cero = [s for s in sf if int(s["stock_actual"]) <= 0]
            sf_bajo = [s for s in sf if 0 < int(s["stock_actual"]) <= int(s.get("stock_minimo") or 0)]
            sf_ok   = [s for s in sf if int(s["stock_actual"]) > int(s.get("stock_minimo") or 0)]
            sf = sf_cero + sf_bajo + sf_ok

            if not sf:
                st.markdown("<p class='empty'>Sin resultados.</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                # Header
                hcols = st.columns([0.9, 2.6, 0.7, 0.8, 0.8, 1.2, 1])
                for col, h in zip(hcols, ["Código","Producto","Und.","Ent.","Sal.","Stock","Estado"]):
                    col.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
                st.markdown("<div style='height:4px;border-bottom:1px solid #1a3d5a;margin-bottom:8px;'></div>", unsafe_allow_html=True)

                for s in sf:
                    sa  = int(s["stock_actual"])
                    sm  = int(s.get("stock_minimo") or 0)
                    if sa <= 0:
                        row_cls, estado_html, stock_cls = "stock-row-cero", "<span class='badge b-sal' style='font-size:10px;'>Sin stock</span>", "clr-red"
                    elif sa <= sm:
                        row_cls, estado_html, stock_cls = "stock-row-warn", "<span style='color:#f59e0b;font-size:11px;font-weight:700;'>⚠ Bajo</span>", "clr-amber"
                    else:
                        row_cls, estado_html, stock_cls = "stock-row-ok", "<span style='color:#00c2a0;font-size:11px;font-weight:700;'>✓ OK</span>", "clr-teal"

                    # Barra visual de stock (% respecto al mínimo x2)
                    ref = max(sm * 2, sa, 1)
                    pct = min(100, int(sa / ref * 100)) if sa > 0 else 0
                    bar_color = "#00a884" if sa > sm else ("#f59e0b" if sa > 0 else "#ef4444")

                    fila = st.columns([0.9, 2.6, 0.7, 0.8, 0.8, 1.2, 1])
                    fila[0].markdown(f"<span class='chip' style='font-size:11px;'>{s['codigo']}</span>", unsafe_allow_html=True)
                    fila[1].markdown(
                        f"<span class='clr-main' style='font-size:13px;'>{s['nombre']}</span>"
                        f"<div class='stock-bar-bg'><div class='stock-bar-fill' style='width:{pct}%;background:{bar_color};'></div></div>",
                        unsafe_allow_html=True
                    )
                    fila[2].markdown(f"<span class='clr-dim'>{s['unidad']}</span>", unsafe_allow_html=True)
                    fila[3].markdown(f"<span class='clr-teal' style='font-size:12px;'>+{int(s['entradas'])}</span>", unsafe_allow_html=True)
                    fila[4].markdown(f"<span class='clr-red' style='font-size:12px;'>-{int(s['salidas'])}</span>", unsafe_allow_html=True)
                    fila[5].markdown(f"<span class='{stock_cls}' style='font-size:16px;font-weight:800;'>{sa}</span>", unsafe_allow_html=True)
                    fila[6].markdown(estado_html, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="margin-top:14px; padding:10px 14px; background:#091520;
                            border-radius:8px; display:flex; justify-content:space-between; align-items:center;
                            border:1px solid #1a3d5a;">
                    <span style="font-size:11px; color:#2a5570;">Mostrando {len(sf)} de {len(sd)} productos</span>
                    <span style="font-size:11px; color:#4a8fa6;">
                        <span style="color:#00a884; font-weight:700;">■</span> OK &nbsp;
                        <span style="color:#f59e0b; font-weight:700;">■</span> Bajo &nbsp;
                        <span style="color:#ef4444; font-weight:700;">■</span> Sin stock
                    </span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Kardex ────────────────────────────────────────────────
    with col_kd:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section">📒 Kardex por Producto</div>', unsafe_allow_html=True)

        prods_kd = cargar_productos()
        pkd_map  = {f"{p['codigo']} — {p['nombre']}": p for p in prods_kd}
        pkd_lbl  = st.selectbox("Selecciona un producto", ["— Seleccionar —"] + list(pkd_map.keys()), key="kd_s")
        pkd      = pkd_map.get(pkd_lbl)

        if pkd:
            try:
                krows = cargar_kardex(pkd["id"])
                if not krows:
                    st.markdown("<p class='empty'>Sin movimientos registrados.</p>", unsafe_allow_html=True)
                else:
                    ultimo = krows[-1]
                    sk     = int(ultimo["saldo"])
                    sc_k   = "#00c2a0" if sk > 0 else "#f87171"

                    # Header del producto
                    st.markdown(f"""
                    <div style="background:#091a28; border-radius:10px; padding:14px 16px; margin-bottom:14px;
                                border:1px solid #1a3d5a; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-size:14px; font-weight:700; color:#e2f0ff; margin-bottom:3px;">{pkd['nombre']}</div>
                            <div style="font-size:11px; font-family:'DM Mono',monospace; color:#00c2a0;">{pkd['codigo']}</div>
                            <div style="font-size:11px; color:#4a6b80; margin-top:2px;">{pkd.get('unidad','—')}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:10px; color:#2a5570; text-transform:uppercase; letter-spacing:.8px; margin-bottom:4px;">Saldo actual</div>
                            <div style="font-size:30px; font-weight:900; color:{sc_k}; line-height:1;">{sk}</div>
                            <div style="font-size:10px; color:#2a5570; margin-top:2px;">{len(krows)} movimiento(s)</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Tabla kardex
                    wk = [0.4, 0.9, 1.4, 0.8, 0.8, 0.9]
                    hk = st.columns(wk)
                    for c, h in zip(hk, ["#","Fecha","Tipo","Ent.","Sal.","Saldo"]):
                        c.markdown(f"<span class='th'>{h}</span>", unsafe_allow_html=True)
                    st.markdown("<div style='border-bottom:1px solid #1a3d5a;margin:4px 0 8px;'></div>", unsafe_allow_html=True)

                    for r in reversed(krows):  # Más reciente primero
                        fk = st.columns(wk)
                        fk[0].markdown(f"<span class='clr-dim' style='font-size:11px;'>{r['nro']}</span>", unsafe_allow_html=True)
                        fk[1].markdown(f"<span class='clr-dim' style='font-size:11px;'>{r['fecha']}</span>", unsafe_allow_html=True)
                        tipo_label = LABEL.get(r['tipo'], r['tipo'])
                        tipo_short = tipo_label.split(" ", 1)[1] if " " in tipo_label else tipo_label
                        bc3 = "b-ent" if r["entrada"] > 0 else "b-sal"
                        fk[2].markdown(f"<span class='badge {bc3}' style='font-size:9px;padding:2px 7px;'>{tipo_short}</span>", unsafe_allow_html=True)
                        if r["entrada"]:
                            fk[3].markdown(f"<span class='clr-teal' style='font-weight:800;'>+{int(r['entrada'])}</span>", unsafe_allow_html=True)
                        else:
                            fk[3].markdown("<span class='clr-dim'>—</span>", unsafe_allow_html=True)
                        if r["salida"]:
                            fk[4].markdown(f"<span class='clr-red' style='font-weight:800;'>-{int(r['salida'])}</span>", unsafe_allow_html=True)
                        else:
                            fk[4].markdown("<span class='clr-dim'>—</span>", unsafe_allow_html=True)
                        sc3 = "clr-teal" if int(r["saldo"]) > 0 else "clr-red"
                        fk[5].markdown(f"<span class='{sc3}' style='font-size:14px;font-weight:800;'>{int(r['saldo'])}</span>", unsafe_allow_html=True)

                    # Mini chart de evolución de saldo
                    if len(krows) >= 2:
                        fig_k = go.Figure()
                        fig_k.add_trace(go.Scatter(
                            x=[r["fecha"] for r in krows],
                            y=[r["saldo"] for r in krows],
                            mode="lines+markers",
                            line=dict(color="#00a884", width=2),
                            marker=dict(size=5, color="#00ffd5"),
                            fill="tozeroy",
                            fillcolor="rgba(0,168,132,0.08)",
                        ))
                        fig_k.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="DM Sans", color="#4a6b80", size=10),
                            margin=dict(l=10,r=10,t=10,b=10), height=120,
                            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                            yaxis=dict(gridcolor="#1a3d5a", zeroline=True, zerolinecolor="#2a4560"),
                            showlegend=False,
                        )
                        st.plotly_chart(fig_k, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Error en kardex: {e}")
        else:
            st.markdown("""
            <div style="text-align:center; padding:40px 20px;">
                <div style="font-size:36px; margin-bottom:12px; opacity:0.3;">📒</div>
                <div style="color:#2a5570; font-size:13px;">Selecciona un producto<br>para ver su historial</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PÁGINA 5 — REPORTES / DASHBOARD
# ════════════════════════════════════════════════════════════
elif "Reportes" in pagina:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;">
        <div style="background:linear-gradient(135deg,#00a884,#006b52);border-radius:12px;padding:10px 14px;font-size:22px;box-shadow:0 4px 14px rgba(0,168,132,0.25);">📊</div>
        <div>
            <div style="font-size:20px;font-weight:800;color:#e2f0ff;">Reportes & Dashboard</div>
            <div style="font-size:12px;color:#2a5570;">Análisis visual de órdenes e inventario</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#7fa8c0", size=11),
        margin=dict(l=10,r=10,t=36,b=10),
    )

    try:
        ordenes_d  = sb.table("orden_compra").select("id,numero,fecha,estado,proveedor:id_proveedor(nombre)").order("fecha").execute().data or []
        detalles_d = sb.table("detalle_orden").select("id_orden,cantidad,precio_unitario,subtotal,producto:id_producto(id,nombre,categoria:id_categoria(nombre))").execute().data or []
        movs_d     = sb.table("movimiento").select("tipo,cantidad,fecha").execute().data or []
        stock_d    = cargar_stock()

        mpo = defaultdict(float)
        for d in detalles_d:
            mpo[d["id_orden"]] += float(d.get("subtotal") or d["cantidad"]*d["precio_unitario"])

        total_oc   = len(ordenes_d)
        pend       = sum(1 for o in ordenes_d if o["estado"]=="PENDIENTE")
        apro       = sum(1 for o in ordenes_d if o["estado"]=="APROBADA")
        anul       = sum(1 for o in ordenes_d if o["estado"]=="ANULADA")
        m_apro     = sum(mpo[o["id"]] for o in ordenes_d if o["estado"]=="APROBADA")
        sin_stock  = sum(1 for s in stock_d if int(s["stock_actual"])<=0)

        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        k1,k2,k3,k4,k5,k6 = st.columns(6)
        k1.metric("Total OC",     total_oc)
        k2.metric("Pendientes",   pend)
        k3.metric("Aprobadas",    apro)
        k4.metric("Anuladas",     anul)
        k5.metric("Monto Apro.", f"S/{m_apro:,.0f}")
        k6.metric("Sin stock",    sin_stock)
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([1.6, 1])
        with c1:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">📅 Órdenes por Mes</div>', unsafe_allow_html=True)
            mc  = defaultdict(int); mm = defaultdict(float)
            for o in ordenes_d:
                m = o["fecha"][:7]; mc[m]+=1; mm[m]+=mpo.get(o["id"],0)
            ms = sorted(mc.keys())
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ms, y=[mc[m] for m in ms], name="OC", marker_color="#00a884",
                                 text=[mc[m] for m in ms], textposition="outside", yaxis="y"))
            fig.add_trace(go.Scatter(x=ms, y=[mm[m] for m in ms], name="Monto (S/)",
                                     line=dict(color="#00ffd5",width=3), mode="lines+markers",
                                     marker=dict(size=8), yaxis="y2"))
            fig.update_layout(**LAYOUT, height=300,
                yaxis=dict(gridcolor="#1a3d5a", zeroline=False),
                yaxis2=dict(overlaying="y", side="right", gridcolor="#1a3d5a"),
                legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">🥧 Por Estado</div>', unsafe_allow_html=True)
            fig2 = go.Figure(go.Pie(
                labels=["Pendiente","Aprobada","Anulada"],
                values=[pend, apro, anul], hole=0.55,
                marker=dict(colors=["#f59e0b","#00a884","#ef4444"], line=dict(color="#0d2137",width=2)),
                textinfo="label+percent", textfont=dict(size=11, color="#e2f0ff"),
            ))
            fig2.add_annotation(text=f"<b>{total_oc}</b>", x=0.5, y=0.5, showarrow=False,
                                 font=dict(size=20, color="#00ffd5"))
            fig2.update_layout(**LAYOUT, height=300, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns([1.6, 1])
        with c3:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">🔤 Análisis ABC de Productos</div>', unsafe_allow_html=True)
            mp2 = defaultdict(float); np2 = {}
            for d in detalles_d:
                pr = d.get("producto") or {}; pid = pr.get("id","?")
                mp2[pid] += float(d.get("subtotal") or d["cantidad"]*d["precio_unitario"])
                np2[pid]  = pr.get("nombre","—")
            sp = sorted(mp2.items(), key=lambda x: x[1], reverse=True)
            tot_abc = sum(v for _,v in sp) or 1; acum=0; abc=[]
            for pid, monto in sp:
                acum+=monto; pct=acum/tot_abc*100
                cls="A" if pct<=80 else ("B" if pct<=95 else "C")
                abc.append({"n": np2[pid][:28], "m": monto, "cls": cls, "pct": pct})
            cmap={"A":"#00a884","B":"#f59e0b","C":"#4a6b80"}
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=[a["n"] for a in abc], y=[a["m"] for a in abc],
                                  marker_color=[cmap[a["cls"]] for a in abc],
                                  text=[f"S/{a['m']:,.0f}" for a in abc], textposition="outside", yaxis="y",
                                  hovertemplate="<b>%{x}</b><br>S/ %{y:,.2f}<extra></extra>"))
            fig3.add_trace(go.Scatter(x=[a["n"] for a in abc], y=[a["pct"] for a in abc],
                                       mode="lines+markers", line=dict(color="#f87171",width=2,dash="dot"),
                                       marker=dict(size=6), yaxis="y2"))
            fig3.add_hline(y=80, yref="y2", line_dash="dash", line_color="#00a884", opacity=0.4)
            fig3.add_hline(y=95, yref="y2", line_dash="dash", line_color="#f59e0b", opacity=0.4)
            fig3.update_layout(**LAYOUT, height=320,
                xaxis=dict(tickangle=-35, tickfont=dict(size=9), gridcolor="#1a3d5a"),
                yaxis=dict(gridcolor="#1a3d5a"),
                yaxis2=dict(overlaying="y", side="right", range=[0,110], gridcolor="#1a3d5a"),
                legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">🏭 Top Proveedores</div>', unsafe_allow_html=True)
            pvm = defaultdict(float)
            for o in ordenes_d:
                pn = (o.get("proveedor") or {}).get("nombre","—")
                pvm[pn] += mpo.get(o["id"],0)
            top_p = sorted(pvm.items(), key=lambda x:x[1], reverse=True)[:7]
            fig4 = go.Figure(go.Bar(
                x=[m for _,m in top_p], y=[n[:20] for n,_ in top_p],
                orientation="h",
                marker_color=[f"rgba(0,168,132,{max(0.4, 1-i*0.12)})" for i in range(len(top_p))],
                text=[f"S/{m:,.0f}" for _,m in top_p], textposition="outside",
                hovertemplate="<b>%{y}</b><br>S/ %{x:,.2f}<extra></extra>",
            ))
            fig4.update_layout(**LAYOUT, height=320,
                xaxis=dict(gridcolor="#1a3d5a"),
                yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns([1.4, 1])
        with c5:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">🔄 Movimientos por Tipo</div>', unsafe_allow_html=True)
            tc = defaultdict(int); tq = defaultdict(int)
            for m in movs_d:
                tc[m["tipo"]]+=1; tq[m["tipo"]]+=int(m["cantidad"])
            tl = list(tc.keys())
            cmt = {"COMPRA":"#00a884","DEVOLUCION":"#00ffd5","VENTA":"#f87171","INHABILITADO":"#4a6b80","USO_INTERNO":"#f59e0b"}
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(x=[LABEL.get(t,t) for t in tl], y=[tc[t] for t in tl],
                                   marker_color=[cmt.get(t,"#7fa8c0") for t in tl],
                                   text=[tc[t] for t in tl], textposition="outside", yaxis="y", name="Nº Mov."))
            fig5.add_trace(go.Scatter(x=[LABEL.get(t,t) for t in tl], y=[tq[t] for t in tl],
                                       mode="lines+markers", line=dict(color="#a78bfa",width=2),
                                       marker=dict(size=8), yaxis="y2", name="Unidades"))
            fig5.update_layout(**LAYOUT, height=280,
                yaxis=dict(gridcolor="#1a3d5a"),
                yaxis2=dict(overlaying="y", side="right", gridcolor="#1a3d5a"),
                legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown('<div class="cp-card cp-card-danger">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section">⚠️ Alertas de Stock</div>', unsafe_allow_html=True)
            s0 = [s for s in stock_d if int(s["stock_actual"])<=0]
            sb2= [s for s in stock_d if 0<int(s["stock_actual"])<=int(s.get("stock_minimo") or 0)]
            if not s0 and not sb2:
                st.markdown("<div style='text-align:center;padding:24px 0;'><div style='font-size:30px;'>✅</div><div style='color:#00c2a0;font-weight:700;margin-top:6px;'>¡Todo en orden!</div></div>", unsafe_allow_html=True)
            else:
                if s0:
                    st.markdown(f"<div style='background:#2d0a0a;border:1px solid #991b1b;border-radius:6px;padding:6px 12px;color:#f87171;font-size:11px;font-weight:700;margin-bottom:6px;'>❌ SIN STOCK — {len(s0)} producto(s)</div>", unsafe_allow_html=True)
                    for s in s0[:4]:
                        st.markdown(f"<div style='padding:3px 12px;font-size:12px;color:#f87171;'>• {s['nombre'][:30]}</div>", unsafe_allow_html=True)
                if sb2:
                    st.markdown(f"<div style='background:#2d1400;border:1px solid #92400e;border-radius:6px;padding:6px 12px;color:#fbbf24;font-size:11px;font-weight:700;margin-top:8px;margin-bottom:6px;'>⚠️ STOCK BAJO — {len(sb2)} producto(s)</div>", unsafe_allow_html=True)
                    for s in sb2[:4]:
                        st.markdown(f"<div style='padding:3px 12px;font-size:12px;color:#fbbf24;'>• {s['nombre'][:30]} ({int(s['stock_actual'])})</div>", unsafe_allow_html=True)

            ok_c = len(stock_d) - len(s0) - len(sb2)
            fig6 = go.Figure(go.Pie(
                labels=["OK","Bajo","Sin stock"], values=[ok_c, len(sb2), len(s0)], hole=0.6,
                marker=dict(colors=["#00a884","#f59e0b","#ef4444"], line=dict(color="#0d2137",width=2)),
                textinfo="value+label", textfont=dict(size=10, color="#e2f0ff"),
            ))
            fig6.add_annotation(text=f"<b>{len(stock_d)}</b>", x=0.5, y=0.5, showarrow=False,
                                 font=dict(size=16, color="#00ffd5"))
            fig6.update_layout(**LAYOUT, height=200, showlegend=False)
            st.plotly_chart(fig6, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error en dashboard: {e}")