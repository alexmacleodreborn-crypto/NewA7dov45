import streamlit as st
import pandas as pd
import numpy as np
import re

# =========================================================
# 1. LOAD WORKBOOK
# =========================================================

WORKBOOK_PATH = "A7DO_MASTER_SYSTEM_v48.xlsx"

@st.cache_data
def load_workbook(path: str):
    return pd.read_excel(
        path,
        sheet_name=None,
        engine="openpyxl",
        dtype=str
    )

wb = load_workbook(WORKBOOK_PATH)


# =========================================================
# 2. SHEET ROLE DETECTION (v48 conventions)
# =========================================================

ROLE_PREFIXES = {
    "ENGINE": ["ENG_", "ENGINE_", "SLED_", "SLW_", "GEN_", "GM_"],
    "BIOLOGY": ["BIO_", "CELL_", "ORG_", "ANAT_", "PHYS_"],
    "COGNITION": ["COG_", "MIND_", "MEM_", "EMO_", "DRIVE_"],
    "WORLD": ["WORLD_", "WRLD_", "ENV_", "MAP_", "LOC_"],
    "NPC": ["NPC_", "CHAR_", "AGENT_", "BEHAV_"],
    "TIMELINE": ["TIME_", "TIM_", "DEV_", "GROWTH_"],
    "STATE": ["STATE_", "SYSSTATE_", "RUNTIME_", "RUN_"],
    "SYSTEM": ["SYS_", "SYSTEM_", "CORE_", "CONFIG_"],
    "GENERIC": []
}

def detect_role(sheet_name: str):
    for role, prefixes in ROLE_PREFIXES.items():
        for p in prefixes:
            if sheet_name.upper().startswith(p):
                return role
    return "GENERIC"


sheet_roles = {name: detect_role(name) for name in wb.keys()}


# =========================================================
# 3. SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("A7DO v48 System App")

# Group sheets by role
grouped = {}
for name, role in sheet_roles.items():
    grouped.setdefault(role, []).append(name)

# Sidebar sections
selected_role = st.sidebar.selectbox("Category", list(grouped.keys()))
selected_sheet = st.sidebar.selectbox("Sheet", grouped[selected_role])

df = wb[selected_sheet]
role = sheet_roles[selected_sheet]

st.title(f"{selected_sheet}")
st.caption(f"Category: **{role}**")


# =========================================================
# 4. RENDERING FUNCTIONS
# =========================================================

def render_inputs(df):
    st.subheader("Inputs")
    values = {}
    for idx, row in df.iterrows():
        label = row.get("Input", f"Input {idx}")
        default = row.get("Value", "0")
        try:
            default = float(default)
        except:
            pass
        values[label] = st.number_input(label, value=default)
    return values


def render_parameters(df):
    st.subheader("Parameters")
    edited = st.data_editor(df, num_rows="dynamic")
    return edited


def render_outputs(df):
    st.subheader("Outputs")
    st.dataframe(df)


def render_state(df):
    st.subheader("System State")
    st.dataframe(df)


def render_generic(df):
    st.subheader("Table")
    st.dataframe(df)


ROLE_RENDERERS = {
    "ENGINE": render_parameters,
    "BIOLOGY": render_generic,
    "COGNITION": render_parameters,
    "WORLD": render_generic,
    "NPC": render_generic,
    "TIMELINE": render_generic,
    "STATE": render_state,
    "SYSTEM": render_parameters,
    "GENERIC": render_generic
}


# =========================================================
# 5. DISPLAY SHEET
# =========================================================

renderer = ROLE_RENDERERS.get(role, render_generic)
result = renderer(df)


# =========================================================
# 6. ENGINE EXECUTION HOOK
# =========================================================

st.divider()
st.subheader("A7DO Engine Runtime")

st.info("""
This section will execute the A7DO organism engines:
- SLED (Sensory‑Layer Engine Dynamics)
- Sandy’s Law (Predictive Field Engine)
- Genesis Mind (Cognitive Engine)
- Organism Runtime Loop

The hook is ready — connect your engine functions here.
""")

if st.button("Run Engine"):
    st.warning("Engine runtime not yet connected.")