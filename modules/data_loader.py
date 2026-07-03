import json, os, glob

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

TECNOLOGIAS = {
    "solar_gd":                     "☀️  GD Solar < 0.7 MW",
    "solar_ac_aislado":              "☀️  Autoconsumo Solar — Aislado (≥ 0.7 MW)",
    "solar_ac_interconectado":       "☀️  Autoconsumo Solar — Interconectado (≥ 0.7 MW)",
    "gas_aislado_con_gas":           "⚡  Motor Gas — Aislado (con suministro de gas)",
    "gas_aislado_sin_gas":           "⚡  Motor Gas — Aislado (sin suministro de gas)",
    "gas_interconectado_con_gas":    "⚡  Motor Gas — Interconectado (con suministro de gas)",
    "gas_interconectado_sin_gas":    "⚡  Motor Gas — Interconectado (sin suministro de gas)",
    "bess":                          "🔋  BESS — Sistema de Almacenamiento de Energía",
}

def load(tech_id: str) -> dict:
    path = os.path.join(DATA_DIR, f"{tech_id}.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def all_ids():
    return list(TECNOLOGIAS.keys())

def label(tech_id: str) -> str:
    return TECNOLOGIAS.get(tech_id, tech_id)
