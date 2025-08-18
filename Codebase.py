import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="July Orders Dashboard", layout="wide")

# Load data function with upload fallback
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    elif os.path.exists("July - Sheet1.csv"):
        return pd.read_csv("July - Sheet1.csv")
    else:
        st.error("No data file found. Please upload a CSV.")
        return pd.DataFrame()

# File uploader
uploaded = st.file_uploader("Upload July Orders CSV", type="csv")
df = load_data(uploaded)

if not df.empty:
    st.success("Data loaded successfully!")

    # --- Ensure expected columns exist ---
    expected_columns = ["Date", "Day", "Order", "Customer Name", "Status", "Price"]
    for col in expected_columns:
        if col not in df.columns:
            st.warning(f"Column '{col}' not found in the dataset. Some charts may not work.")

    # --- Convert Date column ---
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # --- Clean numeric columns ---
    if "Price" in df.columns:
        df["Price"] = pd.to_numeric(df["Price"].str.replace('$','').str.replace(',',''), errors="coerce")

    # --- Orders Over Time ---
    if "Date" in df.columns:
        st.subheader("Orders Over Time")
        daily_orders = df.groupby("Date").size()
        st.line_chart(daily_orders)

    # --- Revenue Over Time ---
    if "Date" in df.columns and "Price" in df.columns:
        st.subheader("Revenue Over Time")
        daily_revenue = df.groupby("Date")["Price"].sum()
        st.line_chart(daily_revenue)

    # --- Orders by Status ---
    if "Status" in df.columns:
        st.subheader("Orders by Status")
        status_counts = df["Status"].value_counts()
        st.bar_chart(status_counts)

    # --- Top Customers by Spending ---
    if "Customer Name" in df.columns and "Price" in df.columns:
        st.subheader("Top Customers by Spending")
        top_customers = df.groupby("Customer Name")["Price"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_customers)

    # --- Heatmap-style Orders by Day of Week vs Week of Month ---
    if "Date" in df.columns:
        st.subheader("Order Patterns (Heatmap Style)")
        df["DayOfWeek"] = df["Date"].dt.day_name()
        df["WeekOfMonth"] = df["Date"].dt.day.apply(lambda d: (d - 1) // 7 + 1)
        heatmap_data = df.groupby(["WeekOfMonth", "DayOfWeek"]).size().unstack(fill_value=0)

        # Convert to long format for stacked bar chart
        heatmap_long = heatmap_data.reset_index().melt(id_vars="WeekOfMonth", var_name="DayOfWeek", value_name="Orders")
        pivot_for_chart = heatmap_long.pivot(index="WeekOfMonth", columns="DayOfWeek", values="Orders")

        st.bar_chart(pivot_for_chart)
