import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="July Orders Dashboard", layout="wide")

# Load data function with upload fallback
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    elif os.path.exists("july_orders_2025.csv"):
        return pd.read_csv("july_orders_2025.csv")
    else:
        st.error("No data file found. Please upload a CSV.")
        return pd.DataFrame()

# File uploader
uploaded = st.file_uploader("Upload July Orders CSV", type="csv")
df = load_data(uploaded)

if not df.empty:
    st.success("Data loaded successfully!")
    st.dataframe(df.head())

    # --- Ensure expected columns exist ---
    expected_columns = ["Date", "Price", "Quantity", "Category", "Product"]
    for col in expected_columns:
        if col not in df.columns:
            st.warning(f"Column '{col}' not found in the dataset. Some charts may not work.")

    # --- Convert Date column ---
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # --- Clean numeric columns ---
    if "Price" in df.columns:
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    # --- Add Revenue column ---
    if "Price" in df.columns and "Quantity" in df.columns:
        df["Revenue"] = df["Price"] * df["Quantity"]

    # --- Orders Over Time ---
    if "Date" in df.columns:
        st.subheader("Orders Over Time")
        daily_orders = df.groupby("Date").size()
        st.line_chart(daily_orders)

    # --- Revenue Over Time ---
    if "Date" in df.columns and "Revenue" in df.columns:
        st.subheader("Revenue Over Time")
        daily_revenue = df.groupby("Date")["Revenue"].sum()
        st.line_chart(daily_revenue)

    # --- Orders by Category ---
    if "Category" in df.columns:
        st.subheader("Orders by Category")
        category_counts = df["Category"].value_counts()
        st.bar_chart(category_counts)

    # --- Top Products by Revenue ---
    if "Product" in df.columns and "Revenue" in df.columns:
        st.subheader("Top Products by Revenue")
        top_products = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_products)

    # --- Heatmap: Orders by Day of Week vs Week of Month ---
    if "Date" in df.columns:
        st.subheader("Order Patterns (Heatmap)")
        df["DayOfWeek"] = df["Date"].dt.day_name()
        df["WeekOfMonth"] = df["Date"].dt.day.apply(lambda d: (d - 1) // 7 + 1)
        heatmap_data = df.groupby(["WeekOfMonth", "DayOfWeek"]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(heatmap_data, cmap="Blues", annot=True, fmt="d", ax=ax)
        st.pyplot(fig)
