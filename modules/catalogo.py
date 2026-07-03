# -*- coding: utf-8 -*-
"""LUXEM — Catálogo normalizado de proyectos (fuente única de verdad).

load(figura, via) genera, por modalidad, la línea de tiempo y el checklist en
semanas desde T0 = aceptación de la oferta. Compatible con data_loader:
expone all_ids(), label(id), load(id, via), vua_elegible(id).

Reglas clave:
- Duración única realista por tarea (sin banda min/max inflada).
- Las tareas CONDICIONALES se dibujan pero NO bloquean a las obligatorias ni
  cuentan en el plazo base (se pueden omitir). Llevan el flag 'condicional'.
- via='vua' aplica overrides (trámites en paralelo) sólo a figuras elegibles.
"""
import json, os

_DIR = os.path.dirname(os.path.abspath(__file__))
def _read(n):
    with open(os.path.join(_DIR, n), encoding="utf-8") as f:
        return json.load(f)

_CAT = _read("tramites.json"); _FIG = _read("figuras.json"); _REF = _read("referencias.json")
_TRAM = {t["id"]: t for t in _CAT["tramites"]}
_AMB = _CAT["_meta"]["ambitos"]

_COLOR_AMBITO = {"1":"#2E86AB","2":"#BA7517","3":"#D85A30","4":"#7F77DD","5":"#185FA5","6":"#1D9E75"}


def _aplica(t, tags):
    return all(x in tags for x in t["aplica_a"])

def _tramites_de(fig_id, via):
    tags = set(_FIG[fig_id]["tags"])
    usa_vua = (via == "vua") and _FIG[fig_id].get("vua_elegible", False)
    subset = {}
    for tid, t in _TRAM.items():
        if not _aplica(t, tags):
            continue
        item = dict(t)
        if usa_vua and "vua" in t:
            item.update(t["vua"])
        subset[tid] = item
    return subset


def _es_cond(subset, tid):
    return subset.get(tid, _TRAM.get(tid, {})).get("nivel") == "condicional"


def _blocking(tid, subset, cache):
    """Predecesores que bloquean el inicio de tid.
    - Un predecesor CONDICIONAL no bloquea a un sucesor OBLIGATORIO (se salta hacia
      sus ancestros bloqueantes), pero sí bloquea a otro condicional (para dibujar cadenas).
    - Un predecesor filtrado (no aplicable) se resuelve transitivamente."""
    if tid in cache:
        return cache[tid]
    t_cond = _es_cond(subset, tid)
    out = set()
    def add(d):
        if d in subset:
            if _es_cond(subset, d) and not t_cond:
                out.update(_blocking(d, subset, cache))
            else:
                out.add(d)
        elif d in _TRAM:
            for a in _TRAM[d]["dep"]:
                add(a)
    for d in subset[tid]["dep"]:
        add(d)
    cache[tid] = out
    return out


def _agenda(subset):
    cache = {}
    blk = {tid: _blocking(tid, subset, cache) for tid in subset}
    ini, fin = {}, {}
    def resolver(tid, pila):
        if tid in fin: return
        if tid in pila:
            ini[tid] = 0; fin[tid] = subset[tid]["dur"]; return
        pila = pila | {tid}
        base = 0
        for d in blk[tid]:
            resolver(d, pila); base = max(base, fin[d])
        ini[tid] = base; fin[tid] = base + subset[tid]["dur"]
    for tid in subset: resolver(tid, set())
    return ini, fin, blk


def _ruta_critica(subset, fin, blk, meta="O04"):
    if meta not in subset:
        obl = [k for k in subset if not _es_cond(subset, k)]
        meta = max(obl, key=lambda k: fin[k]) if obl else max(subset, key=lambda k: fin[k])
    cadena, cur = [], meta
    while cur:
        cadena.append(cur)
        cand = [(fin[d], d) for d in blk[cur] if not _es_cond(subset, d)]
        cur = max(cand)[1] if cand else None
    return list(reversed(cadena))


def _ref_label(k):
    if not k: return "—"
    r = _REF.get(k)
    return f"{r['instrumento']} (DOF {r['dof']})" if r else k


def _dict_figura(fig_id, via):
    fig = _FIG[fig_id]
    elegible = fig.get("vua_elegible", False)
    via = "vua" if (via == "vua" and elegible) else "ordinaria"
    subset = _tramites_de(fig_id, via)
    ini, fin, blk = _agenda(subset)

    # plazo base = fin de la última OBLIGATORIA (O04)
    obl = [k for k in subset if not _es_cond(subset, k)]
    plazo = fin.get("O04", max((fin[k] for k in obl), default=0))
    rc_ids = _ruta_critica(subset, fin, blk)
    ruta = "  →  ".join(subset[i]["nombre"] for i in rc_ids if subset[i]["dur"] > 0)

    fases, checklist = [], []
    orden = sorted(subset, key=lambda k: (ini[k], k))
    for amb in sorted(_AMB):
        acts, items = [], []
        for tid in orden:
            t = subset[tid]
            if t["ambito"] != amb: continue
            cond = _es_cond(subset, tid)
            acts.append({"id": tid, "nombre": t["nombre"], "tipo": t["tipo"],
                         "inicio": ini[tid], "duracion": max(t["dur"], 0),
                         "fin": ini[tid] + max(t["dur"], 0),
                         "responsable": t["responsable"], "referencia": _ref_label(t["ref"]),
                         "condicional": cond,
                         "nota": t["nota"] or ("★ Ruta crítica" if tid in rc_ids else "")})
            items.append({"codigo": tid,
                          "item": t["nombre"] + ("  (condicional)" if cond else ""),
                          "descripcion": t["descripcion"], "responsable": t["responsable"],
                          "referencia": _ref_label(t["ref"]), "condicional": cond, "nota": t["nota"]})
        if acts:
            fases.append({"id": amb, "nombre": f"{amb}. {_AMB[amb]}",
                          "color": _COLOR_AMBITO.get(amb, "#2E86AB"), "actividades": acts})
            checklist.append({"seccion": f"{amb}. {_AMB[amb]}", "items": items})

    usados, marco = [], []
    for tid in orden:
        r = subset[tid]["ref"]
        if r and r not in usados: usados.append(r)
    for k in usados:
        r = _REF.get(k)
        if r: marco.append({"instrumento": r["instrumento"], "dof": r["dof"], "relevancia": r["relevancia"]})

    hitos = []
    for tid in ("D01", "D02", "P05", "P09", "I03", "I06", "O04"):
        if tid in subset: hitos.append({"semana": ini[tid], "nombre": subset[tid]["nombre"]})
    hitos = sorted(hitos, key=lambda h: h["semana"])

    return {"id": fig_id, "nombre": fig["nombre"], "nombre_corto": fig["nombre_corto"],
            "descripcion": fig["descripcion"], "modalidad": fig["modalidad"], "energia": fig["energia"],
            "via": via, "via_label": "Ventanilla Única (VUA)" if via == "vua" else "Ordinaria",
            "vua_elegible": elegible,
            "plazo_min_semanas": plazo, "plazo_max_semanas": plazo,
            "ruta_critica": ruta, "fases": fases, "checklist": checklist,
            "marco_normativo": marco, "hitos_clave": hitos}


_ORDER = list(_FIG.keys())
def all_ids(): return list(_ORDER)
def label(i): return _FIG[i]["nombre"]
def vua_elegible(i): return _FIG[i].get("vua_elegible", False)
def load(fig_id, via="ordinaria"): return _dict_figura(fig_id, via)


if __name__ == "__main__":
    for fid in all_ids():
        d = load(fid)
        na = sum(len(f["actividades"]) for f in d["fases"])
        nc = sum(1 for f in d["fases"] for a in f["actividades"] if a["condicional"])
        extra = ""
        if vua_elegible(fid):
            extra = f" | VUA {load(fid,'vua')['plazo_min_semanas']}"
        print(f"{fid:30s} | Ordinaria {d['plazo_min_semanas']:>3} sem{extra:>10} | {na} activs ({nc} cond)")
