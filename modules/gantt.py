# -*- coding: utf-8 -*-
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Colores por responsable (para la columna de la izquierda)
_RESP_COLOR = {
    "Legal de LUXEM": "#6C3483", "Infraestructura de LUXEM": "#1F618D",
    "Gas Natural LUXEM": "#B9770E", "Energía LUXEM": "#1E8449",
    "Alta de Activos de LUXEM": "#A93226", "MARCOL": "#566573",
    "EPC/Proveedor": "#117A65", "Cliente": "#7B7D7D", "LUXEM": "#34495E",
}
_OP_OK, _OP_COND = 0.90, 0.32   # opacidad barra obligatoria vs condicional


def _rows(data):
    rows = []
    for fase in data["fases"]:
        for act in fase["actividades"]:
            rows.append({**act, "Fase": fase["nombre"], "Color": fase["color"]})
    return rows


def _via_badge(fig, data, xref="paper", yref="paper", x=0.0, y=1.0):
    via = data.get("via_label", "Vía Ordinaria")
    color = "#1D9E75" if data.get("via") == "vua" else "#7F8C8D"
    fig.add_annotation(xref=xref, yref=yref, x=x, y=y, xanchor="left", yanchor="bottom",
                       text=f"  Vía: <b>{via}</b>  ", showarrow=False,
                       font=dict(size=11, color="white"), bgcolor=color,
                       borderpad=3, opacity=0.95)


def build_gantt(data: dict, max_weeks: int = None) -> go.Figure:
    rows = _rows(data)
    if not rows:
        f = go.Figure(); f.add_annotation(text="Sin datos", showarrow=False); return f

    y_order = [r["nombre"] for r in rows]                 # orden top→bottom
    total_weeks = max_weeks or (data["plazo_max_semanas"] + 2)

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        column_widths=[0.26, 0.74], horizontal_spacing=0.008)

    # ── Columna izquierda: Responsable (alineado a la derecha, junto a las barras) ──
    for r in rows:
        c = _RESP_COLOR.get(r["responsable"], "#34495E")
        op = _OP_COND if r["condicional"] else 1.0
        fig.add_trace(go.Scatter(
            x=[1], y=[r["nombre"]], mode="text",
            text=[f"<span style='color:{c}'>{r['responsable']}</span>"],
            textposition="middle left", textfont=dict(size=9), opacity=op,
            hoverinfo="skip", showlegend=False), row=1, col=1)

    # ── Columna derecha: barras del Gantt ──
    seen = set()
    for r in rows:
        s, e = r["inicio"], r["fin"] - 0.05
        in_legend = r["Fase"] not in seen
        if in_legend: seen.add(r["Fase"])
        cond_tag = "  ·  (condicional — puede omitirse)" if r["condicional"] else ""
        hover = (f"<b>{r['nombre']}</b>{cond_tag}<br>"
                 f"<span style='color:#888'>Fase:</span> {r['Fase']}<br>"
                 f"<span style='color:#888'>Semanas:</span> {r['inicio']} → {r['fin']}<br>"
                 f"<span style='color:#888'>Tipo:</span> {r.get('tipo','')}<br>"
                 f"<span style='color:#888'>Responsable:</span> {r['responsable']}<br>"
                 f"<br><i>{r.get('nota','')}</i><br>"
                 f"<br><b>📋 Ref:</b> {r.get('referencia','')}")
        fig.add_trace(go.Bar(
            x=[max(r["fin"] - r["inicio"], 0.15)], y=[r["nombre"]], base=[s],
            orientation="h",
            marker=dict(color=r["Color"], opacity=_OP_COND if r["condicional"] else _OP_OK,
                        line=dict(width=0.5, color="white")),
            hovertemplate=hover + "<extra></extra>",
            name=r["Fase"], legendgroup=r["Fase"], showlegend=in_legend), row=1, col=2)

    # hitos + rejilla (sólo en la columna del gantt); etiquetas de hito ABAJO
    for h in data.get("hitos_clave", []):
        fig.add_shape(type="line", x0=h["semana"], x1=h["semana"], y0=-0.5, y1=len(rows) - 0.5,
                      line=dict(color="#E74C3C", width=1.1, dash="dot"), row=1, col=2)
        fig.add_annotation(x=h["semana"], y=-0.9, text=f"◆ S{h['semana']}",
                           showarrow=False, font=dict(size=8, color="#E74C3C"),
                           xanchor="center", yanchor="top", row=1, col=2)
    for w in range(0, total_weeks + 1, 4):
        fig.add_vline(x=w, line_width=0.5, line_color="rgba(0,0,0,0.06)", row=1, col=2)

    # cabeceras de columna + badge de vía
    fig.add_annotation(xref="paper", yref="paper", x=0.0, y=1.015, xanchor="left", yanchor="bottom",
                       text="<b>ACTIVIDAD</b>", showarrow=False, font=dict(size=9, color="#555"))
    fig.add_annotation(xref="paper", yref="paper", x=0.255, y=1.015, xanchor="right", yanchor="bottom",
                       text="<b>RESPONSABLE</b>", showarrow=False, font=dict(size=9, color="#555"))
    fig.add_annotation(xref="paper", yref="paper", x=0.30, y=1.015, xanchor="left", yanchor="bottom",
                       text="<b>CRONOGRAMA (semanas)</b>", showarrow=False, font=dict(size=9, color="#555"))
    _via_badge(fig, data, x=1.0, y=1.015)
    fig.layout.annotations[-1].update(xanchor="right")
    if data.get("vua_elegible"):
        fig.add_annotation(xref="paper", yref="paper", x=1.0, y=1.055, xanchor="right", yanchor="bottom",
                           text="ⓘ La vía (Ordinaria/VUA) no cambia el plazo total: lo define la construcción.",
                           showarrow=False, font=dict(size=8, color="#7F8C8D"))

    fig.update_xaxes(visible=False, range=[-0.15, 1.02], row=1, col=1)
    fig.update_xaxes(title_text="Semana del proyecto", range=[0, total_weeks], dtick=4,
                     gridcolor="rgba(0,0,0,0.05)", tickfont=dict(size=10), row=1, col=2)
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(y_order)),
                     tickfont=dict(size=9), gridcolor="rgba(0,0,0,0.03)")
    fig.update_layout(
        barmode="overlay", height=max(420, len(rows) * 25 + 150),
        margin=dict(l=248, r=30, t=46, b=80),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="left", x=0.26,
                    font=dict(size=8.5), itemsizing="constant", tracegroupgap=2),
        hoverlabel=dict(bgcolor="white", font_size=11, bordercolor="#CCC"),
        font=dict(family="Arial, sans-serif"))
    return fig


def build_gantt_dual(data_a: dict, data_b: dict) -> go.Figure:
    """Dos Gantts apilados con el mismo eje X. Útil para comparar Ordinaria vs VUA."""
    max_weeks = max(data_a["plazo_max_semanas"], data_b["plazo_max_semanas"]) + 2
    acts_a = sum(len(f["actividades"]) for f in data_a["fases"])
    acts_b = sum(len(f["actividades"]) for f in data_b["fases"])
    h_a, h_b = max(260, acts_a * 22 + 80), max(260, acts_b * 22 + 80)
    total_h = h_a + h_b + 90

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[h_a / (h_a + h_b), h_b / (h_a + h_b)], vertical_spacing=0.06,
                        subplot_titles=[
                            f"<b>{data_a['nombre_corto']}</b> — {data_a['via_label']} — {data_a['plazo_min_semanas']} sem",
                            f"<b>{data_b['nombre_corto']}</b> — {data_b['via_label']} — {data_b['plazo_min_semanas']} sem"])

    seen = set()
    for rn, data in [(1, data_a), (2, data_b)]:
        for fase in data["fases"]:
            for act in fase["actividades"]:
                s, e = act["inicio"], act["fin"] - 0.05
                key = f"{rn}_{fase['nombre']}"; leg = key not in seen
                if leg: seen.add(key)
                resp = act.get("responsable", "")
                cond = act.get("condicional", False)
                hover = (f"<b>{act['nombre']}</b>{' · (condicional)' if cond else ''}<br>"
                         f"Semanas: {act['inicio']} → {act['fin']}<br>Responsable: {resp}<br>"
                         f"<i>{act.get('nota','')}</i><br>📋 {act.get('referencia','')}")
                fig.add_trace(go.Bar(
                    x=[max(e - s, 0.15)], y=[act["nombre"]], base=[s], orientation="h",
                    marker=dict(color=fase["color"], opacity=_OP_COND if cond else 0.88,
                                line=dict(width=0.4, color="white")),
                    hovertemplate=hover + "<extra></extra>", name=fase["nombre"],
                    legendgroup=f"R{rn}_{fase['nombre']}",
                    legendgrouptitle_text=data["nombre_corto"] if leg else None,
                    showlegend=leg), row=rn, col=1)
        rc = sum(len(f["actividades"]) for f in data["fases"])
        for h in data.get("hitos_clave", []):
            fig.add_shape(type="line", x0=h["semana"], x1=h["semana"], y0=-0.5, y1=rc - 0.5,
                          line=dict(color="#E74C3C", width=1, dash="dot"), row=rn, col=1)
        for w in range(0, max_weeks + 1, 4):
            fig.add_vline(x=w, line_width=0.4, line_color="rgba(0,0,0,0.06)", row=rn, col=1)

    fig.update_xaxes(range=[0, max_weeks], dtick=2, tickfont=dict(size=9),
                     gridcolor="rgba(0,0,0,0.04)", title_text="Semana del proyecto", row=2, col=1)
    fig.update_xaxes(range=[0, max_weeks], dtick=2, showticklabels=False, row=1, col=1)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=8))
    fig.update_layout(barmode="overlay", height=total_h, margin=dict(l=230, r=30, t=64, b=50),
                      plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="v", x=1.01, y=1, font=dict(size=8),
                                  tracegroupgap=8, groupclick="toggleitem"),
                      hoverlabel=dict(bgcolor="white", font_size=11), font=dict(family="Arial, sans-serif"))
    return fig
