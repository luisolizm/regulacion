"""LUXEM ENERGÍA — Manual de Proyectos de Generación Distribuida y Autoconsumo"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules import catalogo as data_loader
from modules.gantt import build_gantt, build_gantt_dual
from modules.exportar import export_checklist_word, export_gantt_excel, export_gantt_png

st.set_page_config(
    page_title="LUXEM — Manual de Proyectos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1B4F72; }
[data-testid="stSidebar"] * { color: #ECF0F1 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #AED6F1 !important; font-weight:600; }
.metric-card { background:#EBF5FB; border-left:4px solid #2E86AB;
               border-radius:6px; padding:12px 16px; margin-bottom:8px; }
.metric-label { font-size:11px; color:#7F8C8D; text-transform:uppercase; margin-bottom:2px; }
.metric-value { font-size:22px; font-weight:700; color:#1B4F72; }
.alert-orange { background:#FDEBD0; border-left:4px solid #CA6F1E;
                border-radius:6px; padding:10px 14px; margin-bottom:8px; }
.ref-tag { background:#D6EAF8; color:#1A5276; border-radius:4px;
           padding:2px 6px; font-size:11px; font-weight:600; }
.checklist-item { border-bottom:1px solid #F0F0F0; padding:10px 0; }
.checklist-item:hover { background:#FAFAFA; }
.marco-card { background:#FDFEFE; border:1px solid #D5DBDB;
              border-radius:6px; padding:10px 14px; margin-bottom:6px; }
.onboard-card { background:white; border:1.5px solid #D6EAF8; border-radius:10px;
                padding:20px 22px; margin-bottom:12px; cursor:pointer;
                transition: border-color 0.2s; }
.onboard-card:hover { border-color:#2E86AB; }
.tag-solar { background:#FEF9E7; color:#7E5109; border-radius:4px; padding:2px 8px; font-size:12px; }
.tag-gas   { background:#FDEBD0; color:#6E2C00; border-radius:4px; padding:2px 8px; font-size:12px; }
.tag-bess  { background:#EAF2FF; color:#154360; border-radius:4px; padding:2px 8px; font-size:12px; }
h1 { color:#1B4F72 !important; }
h2 { color:#2E86AB !important; border-bottom:2px solid #EBF5FB; padding-bottom:4px; }
h3 { color:#1B4F72 !important; }
.stButton > button { border-radius:6px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Mapa de respuestas del onboarding a tech_id ───────────────────────────────
ONBOARD_MAP = {
    ("Solar", "GD (< 0.7 MW)", None):                 "solar_gd",
    ("Solar", "Autoconsumo Aislado", None):            "solar_ac_aislado",
    ("Solar", "Autoconsumo Interconectado", None):     "solar_ac_interconectado",
    ("Gas",   "Autoconsumo Aislado", "Sí"):            "gas_aislado_con_gas",
    ("Gas",   "Autoconsumo Aislado", "No"):            "gas_aislado_sin_gas",
    ("Gas",   "Autoconsumo Interconectado", "Sí"):     "gas_interconectado_con_gas",
    ("Gas",   "Autoconsumo Interconectado", "No"):     "gas_interconectado_sin_gas",
    ("BESS",  None, None):                             "bess",
}

# ── Session state defaults ────────────────────────────────────────────────────
if 'tech_id' not in st.session_state:
    st.session_state.tech_id = None
if 'vista' not in st.session_state:
    st.session_state.vista = "📅 Línea de Tiempo"
if 'via' not in st.session_state:
    st.session_state.via = "ordinaria"

# ── Sidebar (solo visible si ya hay tech_id elegido) ─────────────────────────
with st.sidebar:
    st.markdown("## ⚡ LUXEM ENERGÍA")
    st.markdown("**Manual de Proyectos**")
    st.markdown("---")

    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.tech_id = None
        st.rerun()

    if st.session_state.tech_id:
        st.markdown("---")
        ids    = data_loader.all_ids()
        labels = [data_loader.label(i) for i in ids]
        cur_idx = ids.index(st.session_state.tech_id)
        sel_idx = st.selectbox(
            "Cambiar tecnología",
            range(len(ids)),
            format_func=lambda i: labels[i],
            index=cur_idx,
        )
        if ids[sel_idx] != st.session_state.tech_id:
            st.session_state.tech_id = ids[sel_idx]
            st.rerun()

        st.markdown("---")
        vista = st.radio("Vista", [
            "📅 Línea de Tiempo",
            "✅ Checklist Regulatorio",
            "⚖️  Comparador",
            "📋 Marco Normativo",
        ], index=["📅 Línea de Tiempo","✅ Checklist Regulatorio",
                  "⚖️  Comparador","📋 Marco Normativo"].index(st.session_state.vista))
        st.session_state.vista = vista

        st.markdown("---")
        if data_loader.vua_elegible(st.session_state.tech_id):
            st.session_state.via = st.radio(
                "Vía de tramitación", ["ordinaria", "vua"],
                format_func=lambda v: "Vía Ordinaria" if v == "ordinaria" else "Ventanilla Única (VUA)",
                index=["ordinaria", "vua"].index(st.session_state.get("via", "ordinaria")),
            )
        else:
            st.session_state.via = "ordinaria"
            st.caption("Esta figura no aplica a la Ventanilla Única de Autoconsumo.")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#7FB3D3; line-height:1.7'>
    <b>Marco normativo vigente:</b><br>
    • LSE (DOF 18/03/2025)<br>
    • RLSE (DOF 03/10/2025)<br>
    • DACG Autoconsumo (DOF 12/12/2025)<br>
    • DACG SAEE (DOF 16/04/2026)<br>
    • VUA — Ventanilla Única Autoconsumo (DOF 08/05/2026)<br>
    • Manual Interconexión (DOF 15/12/2016)
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 0 — ONBOARDING
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.tech_id:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding: 8px 0 24px'>
        <span style='font-size:36px'>⚡</span><br>
        <span style='font-size:28px; font-weight:700; color:#1B4F72'>LUXEM ENERGÍA</span><br>
        <span style='font-size:16px; color:#5D6D7E'>Manual de Proyectos — Generación Distribuida y Autoconsumo</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ¿Qué tipo de proyecto estás evaluando?")
    st.caption("Responde tres preguntas y te llevamos directo a la información correcta.")
    st.markdown("---")

    # ── Pregunta 1: Energético ────────────────────────────────────────────────
    st.markdown("**1 · ¿Cuál es la fuente de energía?**")
    col_s, col_g, col_b = st.columns(3)

    ENERGETICO_MAP = {
        "☀️  Solar": "Solar",
        "⚡  Gas Natural (Motor/Turbina)": "Gas",
        "🔋  BESS (Almacenamiento)": "BESS",
    }

    with col_s:
        if st.button("☀️  Solar", use_container_width=True):
            st.session_state['_ener'] = "Solar"
    with col_g:
        if st.button("⚡  Gas Natural\n(Motor / Turbina)", use_container_width=True):
            st.session_state['_ener'] = "Gas"
    with col_b:
        if st.button("🔋  BESS\n(Almacenamiento)", use_container_width=True):
            st.session_state['_ener'] = "BESS"
            st.session_state.tech_id = "bess"
            st.session_state.vista = "📅 Línea de Tiempo"
            st.rerun()

    ener = st.session_state.get('_ener')

    if ener:
        st.markdown(f"*Seleccionado: **{ener}***")
        st.markdown("---")

        # ── Pregunta 2: Modalidad ─────────────────────────────────────────────
        st.markdown("**2 · ¿Cuál es la modalidad del proyecto?**")

        modalidades = {
            "Solar": [
                ("GD (< 0.7 MW)", "Generadora Exenta. Sin permiso CNE. Conectada a red CFE. La opción más simple.", "solar_gd"),
                ("Autoconsumo Aislado (≥ 0.7 MW)", "Sin conexión a la red CFE. Permiso CNE obligatorio. Toda la energía se consume en sitio.", "solar_ac_aislado"),
                ("Autoconsumo Interconectado (≥ 0.7 MW)", "Conectada a la red CFE. Permiso CNE + Contrato de Interconexión. Vende excedentes a CFE.", "solar_ac_interconectado"),
            ],
            "Gas": [
                ("Autoconsumo Aislado", "Sin conexión a la red CFE. Permiso CNE obligatorio.", None),
                ("Autoconsumo Interconectado", "Conectada a la red CFE. Permiso CNE + Estudios CENACE + Contrato de Interconexión.", None),
            ],
        }.get(ener, [])

        for label, desc, direct_id in modalidades:
            if st.button(f"**{label}** — {desc}", use_container_width=True, key=f"mod_{label}"):
                st.session_state['_modal'] = label
                if direct_id:
                    st.session_state.tech_id = direct_id
                    st.session_state.vista = "📅 Línea de Tiempo"
                    # clean temp keys
                    for k in ['_ener', '_modal', '_gas']:
                        st.session_state.pop(k, None)
                    st.rerun()
                else:
                    st.rerun()

        modal = st.session_state.get('_modal')

        if modal and ener == "Gas":
            st.markdown("---")
            # ── Pregunta 3: Suministro de gas ─────────────────────────────────
            st.markdown("**3 · ¿El cliente ya tiene suministro de gas natural contratado?**")
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("✅  Sí, ya tiene gas", use_container_width=True):
                    st.session_state['_gas'] = "Sí"
            with col_no:
                if st.button("❌  No, hay que tramitarlo", use_container_width=True):
                    st.session_state['_gas'] = "No"

            gas = st.session_state.get('_gas')
            if gas:
                key = ("Gas", modal, gas)
                tech_id = ONBOARD_MAP.get(key)
                if tech_id:
                    st.session_state.tech_id = tech_id
                    st.session_state.vista = "📅 Línea de Tiempo"
                    for k in ['_ener', '_modal', '_gas']:
                        st.session_state.pop(k, None)
                    st.rerun()

    st.markdown("---")
    st.markdown("**O selecciona directamente:**")
    ids    = data_loader.all_ids()
    labels = [data_loader.label(i) for i in ids]
    sel = st.selectbox("Ver tecnología específica:", ["— elige —"] + labels)
    if sel != "— elige —":
        idx = labels.index(sel)
        st.session_state.tech_id = ids[idx]
        st.session_state.vista = "📅 Línea de Tiempo"
        for k in ['_ener', '_modal', '_gas']:
            st.session_state.pop(k, None)
        st.rerun()

    st.stop()

# ════════════════════════════════════════════════════════════════════════════════
# PANTALLAS PRINCIPALES (tech_id ya definido)
# ════════════════════════════════════════════════════════════════════════════════
data  = data_loader.load(st.session_state.tech_id, st.session_state.get("via", "ordinaria"))
vista = st.session_state.vista

# ── Helpers ───────────────────────────────────────────────────────────────────
def metric_card(label, value):
    return f"""<div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
    </div>"""

def alert(text, level="orange"):
    return f"<div class='alert-orange'>{text}</div>"

# ════════════════════════════════════════════════════════════════════════════════
# VISTA 1 — LÍNEA DE TIEMPO
# ════════════════════════════════════════════════════════════════════════════════
if vista == "📅 Línea de Tiempo":
    st.title(f"📅 {data['nombre']}")
    st.markdown(f"*{data['descripcion']}*")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    total_acts = sum(len(f['actividades']) for f in data['fases'])
    with col1: st.markdown(metric_card("Plazo Estimado", f"{data['plazo_min_semanas']}–{data['plazo_max_semanas']} sem"), unsafe_allow_html=True)
    with col2: st.markdown(metric_card("Actividades", total_acts), unsafe_allow_html=True)
    with col3: st.markdown(metric_card("Fases", len(data['fases'])), unsafe_allow_html=True)
    with col4: st.markdown(metric_card("Hitos Clave", len(data.get('hitos_clave', []))), unsafe_allow_html=True)

    st.markdown(f"<div class='alert-orange'><b>★ Ruta Crítica:</b> {data['ruta_critica']}</div>",
                unsafe_allow_html=True)

    st.markdown("### Gantt del Proyecto")
    st.caption("Pasa el cursor sobre las barras para ver el detalle de cada actividad. Las líneas rojas punteadas marcan hitos clave.")

    fig = build_gantt(data)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col_a, col_b, col_c = st.columns([1, 1, 3])
    with col_a:
        st.download_button("📥 Exportar Excel", data=export_gantt_excel(data),
            file_name=f"LUXEM_Gantt_{st.session_state.tech_id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_b:
        archivo, ext = export_gantt_png(fig)
        st.download_button(
            "🖼️ Descargar Gantt",
            data=archivo,
            file_name=f"LUXEM_Gantt_{st.session_state.tech_id}.{ext}",
            mime="image/png" if ext == "png" else "text/html",
        )

    with st.expander("📋 Ver tabla completa de actividades", expanded=False):
        rows = []
        for fase in data['fases']:
            for act in fase['actividades']:
                rows.append({
                    "Fase": fase['nombre'], "Actividad": act['nombre'],
                    "Tipo": act.get('tipo',''), "Inicio": act['inicio'],
                    "Duración": act['duracion'], "Fin": act['inicio'] + act['duracion'],
                    "Responsable": act.get('responsable',''),
                    "Referencia": act.get('referencia',''), "Nota": act.get('nota',''),
                })
        df = pd.DataFrame(rows)
        fases_opt = ["Todas"] + [f['nombre'] for f in data['fases']]
        sel_fase = st.selectbox("Filtrar por fase:", fases_opt, key="tbl_fase")
        if sel_fase != "Todas":
            df = df[df["Fase"] == sel_fase]
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={"Nota": st.column_config.TextColumn(width="large")})

# ════════════════════════════════════════════════════════════════════════════════
# VISTA 2 — CHECKLIST REGULATORIO (con búsqueda)
# ════════════════════════════════════════════════════════════════════════════════
elif vista == "✅ Checklist Regulatorio":
    st.title(f"✅ {data['nombre']} — Checklist Regulatorio")
    st.markdown(f"*{data['descripcion']}*")
    st.markdown("---")

    total_items = sum(len(s['items']) for s in data['checklist'])
    col1, col2 = st.columns(2)
    with col1: st.markdown(metric_card("Ítems regulatorios", f"{total_items} en {len(data['checklist'])} secciones"), unsafe_allow_html=True)
    with col2: st.markdown(metric_card("Plazo total", f"{data['plazo_min_semanas']}–{data['plazo_max_semanas']} semanas"), unsafe_allow_html=True)

    col_exp, _ = st.columns([1, 3])
    with col_exp:
        st.download_button("📄 Exportar a Word", data=export_checklist_word(data),
            file_name=f"LUXEM_Checklist_{st.session_state.tech_id}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown("---")

    # ── Búsqueda + filtro de sección ──────────────────────────────────────────
    col_search, col_sec = st.columns([2, 1])
    with col_search:
        query = st.text_input("🔍 Buscar en el checklist…",
                              placeholder="Escribe: MISSE, permiso, CFE, IEC, gas…",
                              key="cl_search")
    with col_sec:
        secciones_opt = ["Todas las secciones"] + [s['seccion'] for s in data['checklist']]
        sel_sec = st.selectbox("Sección:", secciones_opt, key="cl_sec")

    q = query.strip().lower()

    total_mostrados = 0
    for sec in data['checklist']:
        if sel_sec != "Todas las secciones" and sec['seccion'] != sel_sec:
            continue

        # Filter items by search query
        items_filtrados = sec['items']
        if q:
            items_filtrados = [
                it for it in sec['items']
                if q in it['item'].lower()
                or q in it['descripcion'].lower()
                or q in it.get('referencia','').lower()
                or q in it.get('nota','').lower()
                or q in it['codigo'].lower()
            ]
        if not items_filtrados:
            continue

        total_mostrados += len(items_filtrados)
        expanded = bool(q) or sel_sec != "Todas las secciones"

        with st.expander(
            f"**{sec['seccion']}** — {len(items_filtrados)} ítem{'s' if len(items_filtrados)!=1 else ''}",
            expanded=expanded
        ):
            for item in items_filtrados:
                # Highlight search term in title
                titulo = item['item']
                if q and q in titulo.lower():
                    idx = titulo.lower().find(q)
                    titulo = (titulo[:idx] +
                              f"<mark style='background:#FFF9C4;border-radius:2px'>{titulo[idx:idx+len(q)]}</mark>" +
                              titulo[idx+len(q):])

                nota_html = ""
                if item.get('nota') and item['nota'] != '—':
                    nota_html = f"<br><span style='color:#CA6F1E;font-size:12px;font-style:italic'>📝 {item['nota']}</span>"

                st.markdown(f"""
                <div class='checklist-item'>
                    <b><span style='color:#1B4F72'>{item['codigo']}</span> — {titulo}</b><br>
                    <span style='color:#2C3E50;font-size:13px'>{item['descripcion']}</span><br>
                    <span style='color:#7F8C8D;font-size:12px'>👤 {item['responsable']}</span>
                    &nbsp;&nbsp;<span class='ref-tag'>📋 {item['referencia']}</span>
                    {nota_html}
                </div>
                """, unsafe_allow_html=True)

    if q and total_mostrados == 0:
        st.warning(f"No se encontraron ítems que contengan **'{query}'**. Intenta con otro término.")
    elif q:
        st.caption(f"Se muestran {total_mostrados} ítem(s) que coinciden con «{query}»")

# ════════════════════════════════════════════════════════════════════════════════
# VISTA 3 — COMPARADOR (Gantt apilado real)
# ════════════════════════════════════════════════════════════════════════════════
elif vista == "⚖️  Comparador":
    st.title("⚖️  Comparador de Tecnologías")
    st.markdown("Compara plazos, regulación y complejidad entre dos tipos de proyecto en el mismo eje de tiempo.")
    st.markdown("---")

    ids    = data_loader.all_ids()
    labels = [data_loader.label(i) for i in ids]
    cur_idx = ids.index(st.session_state.tech_id)

    col_a, col_b = st.columns(2)
    with col_a:
        idx_a = st.selectbox("Tecnología A:", range(len(ids)),
                             format_func=lambda i: labels[i], index=cur_idx, key="cmp_a")
    with col_b:
        idx_b = st.selectbox("Tecnología B:", range(len(ids)),
                             format_func=lambda i: labels[i],
                             index=(cur_idx + 3) % len(ids), key="cmp_b")

    da = data_loader.load(ids[idx_a], st.session_state.get("via", "ordinaria"))
    db = data_loader.load(ids[idx_b], st.session_state.get("via", "ordinaria"))

    # ── Cards de resumen lado a lado ──────────────────────────────────────────
    st.markdown("### Resumen comparativo")
    col_a2, col_b2 = st.columns(2)

    for col, d in [(col_a2, da), (col_b2, db)]:
        with col:
            total_acts  = sum(len(f['actividades']) for f in d['fases'])
            total_items = sum(len(s['items'])       for s in d['checklist'])
            diff_plazo  = abs(da['plazo_min_semanas'] - db['plazo_min_semanas'])
            is_longer   = d['plazo_min_semanas'] == max(da['plazo_min_semanas'], db['plazo_min_semanas'])
            badge = f"<span style='background:#FADBD8;color:#922B21;border-radius:4px;padding:2px 8px;font-size:11px'>+{diff_plazo} sem más largo</span>" if is_longer and diff_plazo > 0 else ""
            st.markdown(f"""
            <div style='background:#EBF5FB;border-radius:8px;padding:18px;border-left:5px solid #2E86AB;'>
                <b style='color:#1B4F72;font-size:14px'>{d['nombre']}</b> {badge}<br><br>
                <span style='color:#7F8C8D;font-size:11px'>PLAZO ESTIMADO</span><br>
                <span style='color:#1B4F72;font-size:26px;font-weight:700'>{d['plazo_min_semanas']}–{d['plazo_max_semanas']} sem</span><br><br>
                <span style='color:#7F8C8D;font-size:11px'>MODALIDAD · ENERGÉTICO</span><br>
                <span style='color:#2C3E50;font-size:12px'>{d['modalidad']}<br>{d['energia']}</span><br><br>
                <span style='color:#7F8C8D;font-size:11px'>ACTIVIDADES · FASES · ÍTEMS CHECKLIST</span><br>
                <span style='color:#2C3E50;font-size:12px'>{total_acts} actvs · {len(d['fases'])} fases · {total_items} ítems</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='alert-orange'><b>★ Ruta Crítica:</b><br><span style='font-size:12px'>{d['ruta_critica']}</span></div>",
                        unsafe_allow_html=True)

    # ── Gantt apilado con eje X compartido ────────────────────────────────────
    st.markdown("---")
    st.markdown("### Gantt comparativo — mismo eje de tiempo")
    st.caption("Los dos proyectos comparten la misma escala temporal. La diferencia de plazo es visualmente inmediata.")

    fig_dual = build_gantt_dual(da, db)
    st.plotly_chart(fig_dual, use_container_width=True)

    # ── Diff de marco normativo ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Diferencias en Marco Normativo")
    refs_a = {nm['instrumento'] for nm in da.get('marco_normativo', [])}
    refs_b = {nm['instrumento'] for nm in db.get('marco_normativo', [])}
    only_a, only_b, both = refs_a - refs_b, refs_b - refs_a, refs_a & refs_b

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown(f"**Solo en {da['nombre_corto']}** ({len(only_a)})")
        for r in sorted(only_a): st.markdown(f"• {r}")
        if not only_a: st.caption("*(todos compartidos)*")
    with col_d2:
        st.markdown(f"**Solo en {db['nombre_corto']}** ({len(only_b)})")
        for r in sorted(only_b): st.markdown(f"• {r}")
        if not only_b: st.caption("*(todos compartidos)*")
    with col_d3:
        st.markdown(f"**Comunes** ({len(both)})")
        for r in sorted(both): st.markdown(f"• {r}")

# ════════════════════════════════════════════════════════════════════════════════
# VISTA 4 — MARCO NORMATIVO (con panel lateral desde Gantt)
# ════════════════════════════════════════════════════════════════════════════════
elif vista == "📋 Marco Normativo":
    st.title(f"📋 Marco Normativo — {data['nombre']}")
    st.markdown("*Instrumentos regulatorios aplicables a este tipo de proyecto.*")
    st.markdown("---")

    # ── Gantt con hover que muestra referencia en panel ───────────────────────
    st.markdown("### Gantt con referencias normativas")
    st.caption("Pasa el cursor sobre cualquier actividad para ver su referencia normativa directamente.")

    fig = build_gantt(data)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Referencia por actividad: selector + panel ────────────────────────────
    st.markdown("### Explorar referencia por actividad")

    all_acts = []
    for fase in data['fases']:
        for act in fase['actividades']:
            ref = act.get('referencia', '—')
            if ref and ref != '—':
                all_acts.append({
                    "label": f"[{fase['id']}] {act['nombre']}",
                    "referencia": ref,
                    "nota": act.get('nota', ''),
                    "tipo": act.get('tipo', ''),
                    "responsable": act.get('responsable', ''),
                    "descripcion": act.get('nota', ''),
                })

    if all_acts:
        sel_act = st.selectbox(
            "Selecciona una actividad:",
            range(len(all_acts)),
            format_func=lambda i: all_acts[i]['label'],
            key="mn_act"
        )
        act_sel = all_acts[sel_act]

        # Find the full normative entry for this reference
        ref_key = act_sel['referencia']
        nm_match = next((nm for nm in data.get('marco_normativo', [])
                         if any(part in nm['instrumento'] for part in ref_key.split(' / '))), None)

        col_act, col_ref = st.columns([1, 1])
        with col_act:
            st.markdown(f"""
            <div style='background:#EBF5FB;border-radius:8px;padding:16px;'>
                <b style='color:#1B4F72'>Actividad seleccionada</b><br><br>
                <b>{act_sel['label']}</b><br>
                <span style='color:#7F8C8D;font-size:12px'>Tipo: {act_sel['tipo']} · Responsable: {act_sel['responsable']}</span><br><br>
                <span class='ref-tag'>📋 {act_sel['referencia']}</span><br><br>
                {"<span style='color:#CA6F1E;font-size:13px;font-style:italic'>📝 " + act_sel['nota'] + "</span>" if act_sel['nota'] and act_sel['nota'] != '—' else ''}
            </div>
            """, unsafe_allow_html=True)
        with col_ref:
            if nm_match:
                st.markdown(f"""
                <div class='marco-card' style='border-left:4px solid #2E86AB;'>
                    <b style='color:#1B4F72'>{nm_match['instrumento']}</b><br>
                    <span class='ref-tag'>DOF: {nm_match['dof']}</span><br><br>
                    <span style='color:#2C3E50;font-size:13px'>{nm_match['relevancia']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='marco-card'>
                    <b style='color:#1B4F72'>Referencia: {ref_key}</b><br>
                    <span style='color:#7F8C8D;font-size:13px'>Consultar el instrumento oficial en el DOF o en el portal de la CNE (gob.mx/cne).</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Todos los instrumentos normativos aplicables")

    for nm in data.get('marco_normativo', []):
        st.markdown(f"""
        <div class='marco-card'>
            <b style='color:#1B4F72'>{nm['instrumento']}</b>
            &nbsp;&nbsp;<span class='ref-tag'>DOF: {nm['dof']}</span><br>
            <span style='color:#2C3E50;font-size:13px;margin-top:4px;display:block'>{nm['relevancia']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_h, col_rc = st.columns(2)
    with col_h:
        st.markdown("### Hitos Clave")
        for h in data.get('hitos_clave', []):
            st.markdown(f"◆ **Semana {h['semana']}** — {h['nombre']}")
    with col_rc:
        st.markdown("### Ruta Crítica")
        st.markdown(f"<div class='alert-orange'>{data['ruta_critica']}</div>", unsafe_allow_html=True)

    st.download_button("📄 Exportar Checklist a Word", data=export_checklist_word(data),
        file_name=f"LUXEM_Checklist_{st.session_state.tech_id}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
