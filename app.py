import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forecast vs Order Intake Dashboard", layout="wide")
st.title("📊 Forecast vs Order Intake Dashboard")

# ===============================
# Reporting Variants
# ===============================
REPORT_VARIANTS = [
    "1.3 GLI MT", "1.3 GLI CVT",
    "1.3 ATIV MT", "1.3 ATIV CVT", "1.5 ATIV X",
    "1.6 MT", "1.6 AT", "1.8L",
    "CROSS", "IMV-III", "Fortuner", "IMV-I"
]

# ===============================
# Variant Mapping (Order Intake)
# ===============================
VARIANT_MAP = {
    "YARIS 046D 1.3 CVT": "1.3 GLI CVT",
    "YARIS 046D 1.3 MT": "1.3 GLI MT",
    "YARIS 046D 1.3 H MT": "1.3 ATIV MT",
    "YARIS 046D 1.3 H CVT": "1.3 ATIV CVT",
    "YARIS 046D 1.5 CVT": "1.5 ATIV X",
    "YARIS 046D 1.5 CVT X": "1.5 ATIV X",

    "ALTIS 1.6 CVT M22": "1.6 AT",
    "ALTIS SE1.6CVT M22": "1.6 AT",
    "ALTIS 1.6 MT M20": "1.6 MT",

    "ALTISGRANDECVT M20": "1.8L",
    "ALTISGRANDECVTM20X": "1.8L",
    "ALTIS 1.8 CVT M20": "1.8L",

    "CROSS 164D 1.8X": "CROSS",
    "CROSS 164D 1.8": "CROSS",
    "CROSS 164D HV 1.8X": "CROSS",
    "CROSS 164D HV 1.8": "CROSS",

    "REVO 481D": "IMV-III",
    "FORTUNER 481D": "Fortuner",
}

# ===============================
# Uploads
# ===============================
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Actual Order Intake Excel", type=["xlsx"])

# ===============================
# Manual Likely Closing
# ===============================
st.subheader("Manual Likely Closing Input")
likely_closing = {}
cols = st.columns(6)
for i, v in enumerate(REPORT_VARIANTS):
    likely_closing[v] = cols[i % 6].number_input(v, min_value=0, step=1)

# ===============================
# Helper Functions
# ===============================
def find_column(df, keywords):
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None

def map_variant(raw):
    raw = str(raw).upper()
    for k, v in VARIANT_MAP.items():
        if k in raw:
            return v
    return "IMV-I"

# ===============================
# Main Processing
# ===============================
if forecast_file and actual_file:

    forecast_df = pd.read_excel(forecast_file)
    actual_df = pd.read_excel(actual_file)

    # Detect columns
    f_variant = find_column(forecast_df, ["variant", "model"])
    f_qty = find_column(forecast_df, ["qty", "quantity"])
    f_month = find_column(forecast_df, ["month"])

    a_variant = find_column(actual_df, ["variant", "model"])
    a_qty = find_column(actual_df, ["qty", "quantity"])

    if None in [f_variant, f_qty, f_month, a_variant, a_qty]:
        st.error("❌ Required columns missing (Variant / Quantity / Month)")
        st.stop()

    # Normalize
    forecast_df["REPORT_VARIANT"] = forecast_df[f_variant].apply(map_variant)
    actual_df["REPORT_VARIANT"] = actual_df[a_variant].apply(map_variant)

    forecast_df["MONTH"] = (
        pd.to_datetime(forecast_df[f_month], errors="coerce")
        .dt.strftime("%b")
        .str.upper()
    )

    # Month selector
    selected_month = st.selectbox(
        "Select Forecast Month",
        sorted(forecast_df["MONTH"].dropna().unique())
    )

    # Filter month
    forecast_month_df = forecast_df[forecast_df["MONTH"] == selected_month]

    # Aggregate Quantity
    forecast_sum = forecast_month_df.groupby("REPORT_VARIANT")[f_qty].sum()
    actual_sum = actual_df.groupby("REPORT_VARIANT")[a_qty].sum()

    # ===============================
    # Output Table
    # ===============================
    output = pd.DataFrame(
        index=[f"{selected_month} - Forecast", "Actual OI - Till Date", "Likely Closing (N)"],
        columns=REPORT_VARIANTS
    ).fillna(0)

    for v in REPORT_VARIANTS:
        output.loc[f"{selected_month} - Forecast", v] = int(forecast_sum.get(v, 0))
        output.loc["Actual OI - Till Date", v] = int(actual_sum.get(v, 0))
        output.loc["Likely Closing (N)", v] = likely_closing[v]

    output["Grand Total"] = output.sum(axis=1)

    st.subheader("📈 Output Table")
    st.dataframe(output, use_container_width=True)

else:
    st.info("⬆ Upload both Excel files to continue")
