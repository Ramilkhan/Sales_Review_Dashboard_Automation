import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales Review Automation", layout="wide")

st.title("📊 Sales Review Dashboard Automation")

# -------------------------
# VARIANT MAPPING FUNCTION
# -------------------------
def map_variant(v):
    v = str(v).upper().replace(" ", "")

    mapping = {
        "1.3GLICVT": ["YARIS046D1.3CVT"],
        "1.3GLIMT": ["YARIS046D1.3MT"],
        "1.3ATIVMT": ["YARIS046D1.3HMT"],
        "1.3ATIVCVT": ["YARIS046D1.3HCVT"],
        "1.5ATIVX": ["YARIS046D1.5CVT", "YARIS046D1.5CVTX"],
        "1.6AT": ["ALTIS1.6CVTM22", "ALTISSE1.6CVTM22"],
        "1.6MT": ["ALTIS1.6MTM20"],
        "1.8L": ["ALTISGRANDECVTM20", "ALTISGRANDECVTM20X", "ALTIS1.8CVTM20"],
        "CROSS": ["CROSS164D"],
        "IMV-III": ["REVO481D"],
        "FORTUNER": ["FORTUNER481D"]
    }

    for k, values in mapping.items():
        for val in values:
            if val in v:
                return k
    return "IMV-I"

# -------------------------
# USER INPUT MONTH
# -------------------------
month_input = st.text_input("Enter Month (MMYYYY)", value="112025")

if len(month_input) != 6 or not month_input.isdigit():
    st.warning("⚠️ Enter valid format like 112025")
    st.stop()

month = int(month_input[:2])
year = int(month_input[2:])

# -------------------------
# FILE UPLOADS
# -------------------------
forecast_file = st.file_uploader("Upload Forecast Excel", type=["xlsx"])
actual_file = st.file_uploader("Upload Actual Order Intake Excel", type=["xlsx"])

if not forecast_file or not actual_file:
    st.stop()

# -------------------------
# READ FILES
# -------------------------
forecast_df = pd.read_excel(forecast_file)
actual_df = pd.read_excel(actual_file)

# -------------------------
# AUTO COLUMN DETECTION
# -------------------------
def detect_column(df, keywords):
    for col in df.columns:
        for k in keywords:
            if k in col.lower():
                return col
    return None

f_variant = detect_column(forecast_df, ["variant"])
f_date = detect_column(forecast_df, ["date", "month"])
f_qty = detect_column(forecast_df, ["qty", "quantity"])

a_variant = detect_column(actual_df, ["variant"])
a_date = detect_column(actual_df, ["date"])
a_qty = detect_column(actual_df, ["qty", "quantity"])

# fallback qty
if f_qty is None:
    forecast_df["QTY"] = 1
    f_qty = "QTY"

if a_qty is None:
    actual_df["QTY"] = 1
    a_qty = "QTY"

# -------------------------
# DATE FILTER
# -------------------------
forecast_df[f_date] = pd.to_datetime(forecast_df[f_date], errors="coerce")
actual_df[a_date] = pd.to_datetime(actual_df[a_date], errors="coerce")

forecast_df = forecast_df[
    (forecast_df[f_date].dt.month == month) &
    (forecast_df[f_date].dt.year == year)
]

actual_df = actual_df[
    (actual_df[a_date].dt.month == month) &
    (actual_df[a_date].dt.year == year)
]

# -------------------------
# APPLY VARIANT MAPPING
# -------------------------
forecast_df["Mapped Variant"] = forecast_df[f_variant].apply(map_variant)
actual_df["Mapped Variant"] = actual_df[a_variant].apply(map_variant)

# -------------------------
# AGGREGATION
# -------------------------
forecast_sum = forecast_df.groupby("Mapped Variant")[f_qty].sum()
actual_sum = actual_df.groupby("Mapped Variant")[a_qty].sum()

variants = sorted(set(forecast_sum.index).union(actual_sum.index))

# -------------------------
# MANUAL INPUT
# -------------------------
st.subheader("✍️ Manual Adjustment")
manual_data = {}
for v in variants:
    manual_data[v] = st.number_input(f"{v}", min_value=0, value=0)

# -------------------------
# OUTPUT TABLE
# -------------------------
output = pd.DataFrame(index=[
    "Forecast",
    "Actual OI - Till Date",
    "Manual Input"
], columns=variants).fillna(0)

for v in variants:
    output.loc["Forecast", v] = int(forecast_sum.get(v, 0))
    output.loc["Actual OI - Till Date", v] = int(actual_sum.get(v, 0))
    output.loc["Manual Input", v] = manual_data[v]

st.subheader("✅ Final Output Table")
st.dataframe(output, use_container_width=True)
