import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Forecast vs Order Intake", layout="wide")

st.title("📊 Forecast vs Order Intake Dashboard")

# =========================
# USER INPUT: MONTH
# =========================
month_code = st.text_input(
    "Enter Month (MMYYYY e.g. 112025 for Nov 2025)",
    value=""
)

if len(month_code) != 6:
    st.warning("Please enter month in MMYYYY format")
    st.stop()

month = int(month_code[:2])
year = int(month_code[2:])

# =========================
# FILE UPLOADS
# =========================
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Order Intake Excel", type=["xlsx"])

# =========================
# VARIANT MAPPING
# =========================
variant_map = {
    "1.3 GLI MT": [
        "YARIS 046D 1.3 MT"
    ],
    "1.3 GLI CVT": [
        "YARIS 046D 1.3 CVT"
    ],
    "1.3 ATIV MT": [
        "YARIS 046D 1.3 H MT"
    ],
    "1.3 ATIV CVT": [
        "YARIS 046D 1.3 H CVT"
    ],
    "1.5 ATIV X": [
        "YARIS 046D 1.5 CVT", "YARIS 046D 1.5 CVT X"
    ],
    "1.6 MT": [
        "ALTIS 1.6 MT M20"
    ],
    "1.6 AT": [
        "ALTIS 1.6 CVT M22", "ALTIS SE1.6CVT M22"
    ],
    "1.8L": [
        "ALTISGRANDECVT M20", "ALTISGRANDECVTM20X", "ALTIS 1.8 CVT M20"
    ],
    "CROSS": [
        "CROSS 164D 1.8X", "CROSS 164D 1.8",
        "CROSS 164D HV 1.8X", "CROSS 164D HV 1.8"
    ],
    "IMV-III": [
        "REVO 481D 4X4 G AT", "REVO 481D 4X4 V AT",
        "REVO 481D ROCCO", "REVO 481D 4X4 G MT",
        "REVO 481D GR-S"
    ],
    "Fortuner": [
        "FORTUNER 481D GR-S", "FORTUNER481D4X2GAT",
        "FORTUNER481D4X4VAT", "FORTUNER481D4X4SAT",
        "FORTUNER 481DLGNDR"
    ]
}

def normalize_variant(raw):
    for std, raws in variant_map.items():
        if raw in raws:
            return std
    return "IMV-I"

# =========================
# DATA PROCESSING
# =========================
def prepare_data(df):
    df.columns = df.columns.str.lower()

    variant_col = [c for c in df.columns if "variant" in c][0]
    date_col = [c for c in df.columns if "date" in c][0]

    qty_col = None
    for c in df.columns:
        if "qty" in c or "quantity" in c:
            qty_col = c

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df[(df[date_col].dt.month == month) & (df[date_col].dt.year == year)]

    df["std_variant"] = df[variant_col].apply(normalize_variant)
    df["qty"] = df[qty_col] if qty_col else 1

    return df.groupby("std_variant")["qty"].sum()

# =========================
# OUTPUT STRUCTURE
# =========================
variants = [
    "1.3 GLI MT","1.3 GLI CVT","1.3 ATIV MT","1.3 ATIV CVT","1.5 ATIV X",
    "1.6 MT","1.6 AT","1.8L","CROSS","Fortuner","IMV-III","IMV-I"
]

output = pd.DataFrame(
    index=[
        "Forecast",
        "Actual Month Closing",
        "Likely Closing",
        "% Achievement Actual"
    ],
    columns=variants
).fillna(0)

# =========================
# PROCESS FILES
# =========================
if forecast_file and actual_file:
    forecast_df = pd.read_excel(forecast_file)
    actual_df = pd.read_excel(actual_file)

    forecast_sum = prepare_data(forecast_df)
    actual_sum = prepare_data(actual_df)

    for v in variants:
        output.loc["Forecast", v] = int(forecast_sum.get(v, 0))
        output.loc["Actual Month Closing", v] = int(actual_sum.get(v, 0))

    # =========================
    # MANUAL LIKELY CLOSING
    # =========================
    st.subheader("Manual Likely Closing Input")
    cols = st.columns(4)
    for i, v in enumerate(variants):
        with cols[i % 4]:
            output.loc["Likely Closing", v] = st.number_input(
                v, min_value=0, step=1, key=v
            )

    # =========================
    # ACHIEVEMENT %
    # =========================
    for v in variants:
        f = output.loc["Forecast", v]
        a = output.loc["Actual Month Closing", v]
        output.loc["% Achievement Actual", v] = f"{int((a/f)*100)}%" if f > 0 else "-"

    st.subheader("📈 Output Table")
    st.dataframe(output, use_container_width=True)
