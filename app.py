import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forecast vs Order Intake Dashboard", layout="wide")

st.title("📊 Forecast vs Order Intake Dashboard")

# -------------------------------
# Final Reporting Variants
# -------------------------------
REPORT_VARIANTS = [
    "1.3 GLI MT", "1.3 GLI CVT",
    "1.3 ATIV MT", "1.3 ATIV CVT", "1.5 ATIV X",
    "1.6 MT", "1.6 AT", "1.8L",
    "CROSS", "IMV-III", "Fortuner", "IMV-I"
]

# -------------------------------
# Order Intake Mapping
# -------------------------------
VARIANT_MAP = {
    # YARIS
    "YARIS 046D 1.3 CVT": "1.3 GLI CVT",
    "YARIS 046D 1.3 MT": "1.3 GLI MT",
    "YARIS 046D 1.3 H MT": "1.3 ATIV MT",
    "YARIS 046D 1.3 H CVT": "1.3 ATIV CVT",
    "YARIS 046D 1.5 CVT": "1.5 ATIV X",
    "YARIS 046D 1.5 CVT X": "1.5 ATIV X",

    # ALTIS
    "ALTIS 1.6 CVT M22": "1.6 AT",
    "ALTIS SE1.6CVT M22": "1.6 AT",
    "ALTIS 1.6 MT M20": "1.6 MT",

    # GRANDE
    "ALTISGRANDECVT M20": "1.8L",
    "ALTISGRANDECVTM20X": "1.8L",
    "ALTIS 1.8 CVT M20": "1.8L",

    # CROSS
    "CROSS 164D 1.8X": "CROSS",
    "CROSS 164D 1.8": "CROSS",
    "CROSS 164D HV 1.8X": "CROSS",
    "CROSS 164D HV 1.8": "CROSS",

    # REVO
    "REVO 481D 4X4 G AT": "IMV-III",
    "REVO 481D 4X4 V AT": "IMV-III",
    "REVO 481D ROCCO": "IMV-III",
    "REVO 481D 4X4 G MT": "IMV-III",
    "REVO 481D GR-S": "IMV-III",

    # FORTUNER
    "FORTUNER 481D GR-S": "Fortuner",
    "FORTUNER481D4X2GAT": "Fortuner",
    "FORTUNER481D4X4VAT": "Fortuner",
    "FORTUNER481D4X4SAT": "Fortuner",
    "FORTUNER 481DLGNDR": "Fortuner",
}

# -------------------------------
# Upload Files
# -------------------------------
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Actual Order Intake Excel", type=["xlsx"])

# -------------------------------
# Manual Likely Closing
# -------------------------------
st.subheader("Manual Likely Closing Input")

likely_closing = {}
cols = st.columns(6)
for i, v in enumerate(REPORT_VARIANTS):
    likely_closing[v] = cols[i % 6].number_input(v, min_value=0, step=1)

# -------------------------------
# Helpers
# -------------------------------
def find_variant_column(df):
    for c in df.columns:
        if "variant" in c.lower():
            return c
    return None

def map_variant(raw):
    raw = str(raw).strip().upper()
    for key, val in VARIANT_MAP.items():
        if key in raw:
            return val
    return "IMV-I"

# -------------------------------
# Processing
# -------------------------------
if forecast_file and actual_file:

    forecast_df = pd.read_excel(forecast_file)
    actual_df = pd.read_excel(actual_file)

    f_col = find_variant_column(forecast_df)
    a_col = find_variant_column(actual_df)

    if not f_col or not a_col:
        st.error("❌ 'Variant' column not found in one of the files")
        st.stop()

    forecast_df["REPORT_VARIANT"] = forecast_df[f_col].apply(map_variant)
    actual_df["REPORT_VARIANT"] = actual_df[a_col].apply(map_variant)

    forecast_count = forecast_df["REPORT_VARIANT"].value_counts()
    actual_count = actual_df["REPORT_VARIANT"].value_counts()

    # -------------------------------
    # Output Table
    # -------------------------------
    output = pd.DataFrame(
        index=["NOV - Forecast", "Actual OI - Till Date", "Likely Closing (N)"],
        columns=REPORT_VARIANTS
    ).fillna(0)

    for v in REPORT_VARIANTS:
        output.loc["NOV - Forecast", v] = forecast_count.get(v, 0)
        output.loc["Actual OI - Till Date", v] = actual_count.get(v, 0)
        output.loc["Likely Closing (N)", v] = likely_closing[v]

    output["Grand Total"] = output.sum(axis=1)

    st.subheader("📈 Output Table")
    st.dataframe(output, use_container_width=True)

else:
    st.info("⬆ Upload both Excel files")

