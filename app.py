import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forecast vs Order Intake", layout="wide")

st.title("📊 Forecast vs Order Intake Automation")

# ---------------- VARIANT MAPPING ---------------- #
VARIANT_MAP = {
    # YARIS
    "YARIS 046D 1.3 CVT": "1.3 GLI CVT",
    "YARIS 046D 1.3 MT": "1.3 GLI MT",
    "YARIS 046D 1.3 H MT": "1.3 ATIV MT",
    "YARIS 046D 1.3 H CVT": "1.3 ATIV CVT",
    "YARIS 046D 1.5 CVT": "1.5 ATIV X",
    "YARIS 046D 1.5 CVT X": "1.5 ATIV X",

    # COROLLA
    "ALTIS 1.6 CVT M22": "1.6 AT",
    "ALTIS SE1.6CVT M22": "1.6 AT",
    "ALTIS 1.6 MT M20": "1.6 MT",
    "ALTISGRANDECVT M20": "1.8L",
    "ALTISGRANDECVTM20X": "1.8L",
    "ALTIS 1.8 CVT M20": "1.8L",

    # CROSS
    "CROSS 164D 1.8X": "CROSS",
    "CROSS 164D 1.8": "CROSS",
    "CROSS 164D HV 1.8X": "CROSS",
    "CROSS 164D HV 1.8": "CROSS",

    # IMVs
    "REVO 481D 4X4 G AT": "IMV-III",
    "REVO 481D 4X4 V AT": "IMV-III",
    "REVO 481D ROCCO": "IMV-III",
    "REVO 481D 4X4 G MT": "IMV-III",
    "REVO 481D GR-S": "IMV-III",

    "FORTUNER 481D GR-S": "Fortuner",
    "FORTUNER481D4X2GAT": "Fortuner",
    "FORTUNER481D4X4VAT": "Fortuner",
    "FORTUNER481D4X4SAT": "Fortuner",
    "FORTUNER 481DLGNDR": "Fortuner",
}

STANDARD_VARIANTS = [
    "1.3 GLI MT","1.3 GLI CVT","1.3 ATIV MT","1.3 ATIV CVT","1.5 ATIV X",
    "1.6 MT","1.6 AT","1.8L",
    "CROSS",
    "Fortuner","IMV-III","IMV-I"
]

# ---------------- FILE UPLOAD ---------------- #
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Actual Order Intake Excel", type=["xlsx"])

# ---------------- PROCESSING ---------------- #
if forecast_file and actual_file:

    forecast_df = pd.read_excel(forecast_file)
    actual_df = pd.read_excel(actual_file)

    forecast_df["Std Variant"] = forecast_df["Variant"].map(VARIANT_MAP).fillna("IMV-I")
    actual_df["Std Variant"] = actual_df["Variant"].map(VARIANT_MAP).fillna("IMV-I")

    forecast_summary = forecast_df.groupby("Std Variant")["Quantity"].sum()
    actual_summary = actual_df.groupby("Std Variant").size()

    # Manual Input
    st.subheader("✍ Manual Month Closing Input")
    manual_data = {}
    cols = st.columns(4)
    for i, v in enumerate(STANDARD_VARIANTS):
        manual_data[v] = cols[i % 4].number_input(v, min_value=0, step=1)

    # Build Output Table
    output = pd.DataFrame(index=[
        "OCT - Forecast",
        "Actual Month Closing",
        "% Achievement Actual"
    ], columns=STANDARD_VARIANTS)

    for v in STANDARD_VARIANTS:
        f = forecast_summary.get(v, 0)
        a = actual_summary.get(v, 0) + manual_data[v]

        output.loc["OCT - Forecast", v] = f
        output.loc["Actual Month Closing", v] = a
        output.loc["% Achievement Actual", v] = round((a / f * 100), 1) if f != 0 else "-"

    st.subheader("📈 Output Table")
    st.dataframe(output, use_container_width=True)

    # Download
    st.download_button(
        "⬇ Download Excel",
        output.to_excel(index=True),
        file_name="Forecast_vs_Actual.xlsx"
    )

else:
    st.info("Please upload both Forecast and Actual Order Intake files.")
