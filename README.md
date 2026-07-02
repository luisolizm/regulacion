# LUXEM ENERGÍA — Manual de Proyectos

Aplicativo web para visualizar líneas de tiempo, checklists regulatorios
y marcos normativos para proyectos de generación distribuida y autoconsumo en México.

## Requisitos

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

El app abre automáticamente en http://localhost:8501

## Tecnologías incluidas

| ID | Nombre | Plazo |
|----|--------|-------|
| solar_gd | GD Solar < 0.7 MW | 22–24 sem |
| solar_ac_aislado | Autoconsumo Solar Aislado | 28–36 sem |
| solar_ac_interconectado | Autoconsumo Solar Interconectado | 32–42 sem |
| gas_aislado_con_gas | Motor Gas Aislado (con gas) | 36–48 sem |
| gas_aislado_sin_gas | Motor Gas Aislado (sin gas) | 44–64 sem |
| gas_interconectado_con_gas | Motor Gas Interconectado (con gas) | 40–56 sem |
| gas_interconectado_sin_gas | Motor Gas Interconectado (sin gas) | 52–72 sem |
| bess | BESS — Almacenamiento | 24–44 sem |

## Marco normativo incorporado

- LSE (DOF 18/03/2025)
- RLSE (DOF 03/10/2025)
- DACG Autoconsumo (DOF 12/12/2025)
- DACG SAEE (DOF 16/04/2026)
- DACG GD / Guía CNE (DOF 08/05/2026)
- DACG Cogeneración (DOF 16/04/2026)
- DACG Permisos CNE (DOF 23/10/2025)
- Acuerdo Simplificado Autoconsumo 0.7–20 MW (DOF 06/08/2025)
- Manual Interconexión < 0.5 MW (DOF 15/12/2016)
- Manual Interconexión Centrales y CCC (DOF 09/02/2018)
- NOM-001-SEDE, NOM-002-SECRE, NOM-003-SECRE, NOM-031-STPS
- IEC 62116, IEC 61215, IEC 61730, IEC 62446, IEC 62619, IEC 62933

## Exportaciones disponibles

- 📥 Excel con Gantt visual (colores por fase, freeze panes)
- 🖼️ PNG del Gantt (requiere kaleido instalado)
- 📄 Word con checklist regulatorio completo (tablas, notas, referencias)

## Para abrir a clientes

Cambiar la línea `initial_sidebar_state="expanded"` por `"collapsed"` en app.py
para una vista más limpia. No se requiere login.

## Actualización de contenido

Los datos están en `data/*.json`. Para actualizar:
1. Editar el JSON de la tecnología correspondiente
2. No es necesario cambiar el código Python
3. Reiniciar el app con `streamlit run app.py`

---
LUXEM ENERGÍA · Junio 2026
