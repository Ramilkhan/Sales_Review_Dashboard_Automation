import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forecast vs Order Intake", layout="wide")

st.title("📊 Forecast vs Order Intake Dashboard")

# -------------------------
# Variant Mapping
# -------------------------
variant_mapping = {
    "HMT": "ATIV MT",
    "HCVT": "ATIV CVT"
}

all_variants = [
    "GLI MT", "GLI CVT", "ATIV MT", "ATIV CVT", "ATIV X",
    "1.6 MT", "1.6 AT", "1.8L",
    "CROSS",
    "Fortuner", "IMV-III", "IMV-I"
]

# -------------------------
# File Uploads
# -------------------------
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Actual Order Intake Excel", type=["xlsx"])

# -------------------------
# Manual Likely Closing
# -------------------------
st.subheader("Manual Likely Closing Input")

likely_closing = {}
cols = st.columns(6)
for i, v in enumerate(all_variants):
    likely_closing[v] = cols[i % 6].number_input(v, min_value=0, step=1)

# -------------------------
# Helper Functions
# -------------------------
def find_variant_column(df):
    for col in df.columns:
        if "variant" in col.lower() or "model" in col.lower():
            return col
    return None

def prepare_data(df):
    variant_col = find_variant_column(df)

    if variant_col is None:
        st.error("❌ No Variant/Model column found in Excel")
        st.stop()

    df = df.copy()
    df["Variant"] = (
        df[variant_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace(variant_mapping)
    )

    return df

# -------------------------
# Process Data
# -------------------------
if forecast_file and actual_file:

    forecast_df = pd.read_excel(forecast_file)
    actual_df = pd.read_excel(actual_file)

    forecast_df = prepare_data(forecast_df)
    actual_df = prepare_data(actual_df)

    forecast_counts = forecast_df["Variant"].value_counts()
    actual_counts = actual_df["Variant"].value_counts()

    # -------------------------
    # Output Table
    # -------------------------
    output = pd.DataFrame(
        index=[
            "NOV - Forecast",
            "Actual OI - Till Date",
            "Likely Closing (N)"
        ],
        columns=all_variants
    ).fillna(0)

    for v in all_variants:
        output.loc["NOV - Forecast", v] = int(forecast_counts.get(v, 0))
        output.loc["Actual OI - Till Date", v] = int(actual_counts.get(v, 0))
        output.loc["Likely Closing (N)", v] = likely_closing[v]

    output["Grand Total"] = output.sum(axis=1)

    st.subheader("📈 Output Table")
    st.dataframe(output, use_container_width=True)

else:
    st.info("⬆ Upload both Excel files to see results")
