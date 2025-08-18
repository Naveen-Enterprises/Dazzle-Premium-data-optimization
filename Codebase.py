import streamlit as st
import pandas as pd
import os
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Interactive Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- DATA LOADING AND CLEANING ---
@st.cache_data
def load_and_clean_data(sheet_url):
    """
    Loads data directly from a public Google Sheets URL and performs
    necessary cleaning and transformations.
    
    Args:
        sheet_url: The public Google Sheets URL.
        
    Returns:
        A cleaned Pandas DataFrame or an empty DataFrame if an error occurs.
    """
    if not sheet_url:
        st.warning("Please enter a Google Sheets URL.")
        return pd.DataFrame()
        
    # Convert the public sharing URL to a CSV export URL
    try:
        # Example: https://docs.google.com/spreadsheets/d/1Xy_Jd2g9.../edit#gid=123
        # Becomes: https://docs.google.com/spreadsheets/d/1Xy_Jd2g9.../export?format=csv&gid=123
        url_parts = sheet_url.split('/d/')
        if len(url_parts) < 2:
            st.error("Invalid Google Sheets URL format. Please provide a full public URL.")
            return pd.DataFrame()
        
        sheet_id_part = url_parts[1].split('/edit')[0]
        gid_part = "0"
        if "gid=" in sheet_url:
            gid_part = sheet_url.split('gid=')[1].split('&')[0]
            
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id_part}/export?format=csv&gid={gid_part}"
        
        # Load data from the generated CSV URL
        df = pd.read_csv(csv_url)
        st.info(f"Raw data loaded. Total rows: {len(df)}")

    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        st.error("Please ensure the sheet is publicly accessible (File > Share > Anyone with the link).")
        return pd.DataFrame()

    if df.empty:
        st.warning("The Google Sheet is empty.")
        return df

    # --- Step 2: Data Cleaning & Preparation ---
    try:
        # Clean column names by removing leading/trailing whitespace
        df.columns = df.columns.str.strip()
        
        # Ensure all required columns exist before proceeding
        required_cols = ['Date', 'Price', 'Status', 'Customer Name']
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"The sheet must contain the following columns: {', '.join(required_cols)}")
            return pd.DataFrame()
        
        # Drop rows where all values are empty, which commonly appear in CSV exports
        df.dropna(how='all', inplace=True)
        
        # Use forward fill to fill empty cells in 'Date' column
        df['Date'].ffill(inplace=True)
        
        # Convert 'Date' column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Clean the 'Price' column: remove '$', commas, and convert to numeric
        if df['Price'].dtype == 'object':
            df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

        # Standardize the 'Status' column (e.g., trim whitespace, capitalize)
        df['Status'] = df['Status'].str.strip().str.title()
        
        # Drop rows where essential data is missing after cleaning
        df.dropna(subset=['Date', 'Price', 'Status'], inplace=True)
        
        # Sort by date to ensure proper plotting
        df.sort_values(by='Date', inplace=True)

        st.success(f"Data cleaned. Valid order rows: {len(df)}")
        return df
    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return pd.DataFrame()

# --- MAIN PAGE LAYOUT ---
st.title("📊 Interactive Sales Dashboard")
st.markdown("Analyze your sales data to uncover trends and insights.")

# --- URL INPUT AND LOAD BUTTON ---
st.sidebar.header("Google Sheets URL")
sheet_url = st.sidebar.text_input("Enter your public Google Sheets URL:", value="")
load_button = st.sidebar.button("Load Data")

# Load data only when the button is clicked
df = pd.DataFrame()
if load_button and sheet_url:
    df = load_and_clean_data(sheet_url)

if not df.empty:
    # --- SIDEBAR FILTERS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Data")

    # Date filter
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    date_range = st.sidebar.slider(
        "Select a Date Range:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    
    # Status filter
    all_statuses = ["All"] + sorted(list(df['Status'].unique()))
    selected_statuses = st.sidebar.multiselect(
        "Select Order Status(es):",
        options=all_statuses,
        default=["All"]
    )

    # --- FILTER THE DATAFRAME BASED ON USER SELECTIONS ---
    filtered_df = df[df['Date'].between(date_range[0], date_range[1])]
    
    if "All" not in selected_statuses:
        filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
    else:
        # --- KEY METRICS (KPIs) ---
        st.markdown("## 📈 Key Performance Indicators")
        
        fulfilled_orders = filtered_df[filtered_df['Status'] == 'Fulfilled']
        
        total_revenue = fulfilled_orders['Price'].sum()
        total_orders = len(filtered_df)
        fulfilled_count = len(fulfilled_orders)
        avg_order_value = total_revenue / fulfilled_count if fulfilled_count > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue (Fulfilled)", f"${total_revenue:,.2f}")
        col2.metric("Total Orders", f"{total_orders:,}")
        col3.metric("Average Order Value", f"${avg_order_value:,.2f}")

        st.markdown("---")

        # --- VISUALIZATIONS IN COLUMNS ---
        st.markdown("## 📊 Sales Trends")
        left_col, right_col = st.columns(2)

        # --- 1. Daily Orders (Line Chart) ---
        with left_col:
            st.subheader("Daily Order Volume")
            daily_orders = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index(name='Order Count')
            st.line_chart(daily_orders, x='Date', y='Order Count')

        # --- 2. Daily Revenue (Line Chart) ---
        with right_col:
            st.subheader("Daily Revenue")
            daily_revenue = filtered_df.groupby(filtered_df['Date'].dt.date)['Price'].sum().reset_index()
            st.line_chart(daily_revenue, x='Date', y='Price')
        
        st.markdown("---")
        
        st.markdown("## 📉 Sales Breakdown")
        left_col_2, right_col_2 = st.columns(2)

        # --- 3. Orders by Status (Donut Chart) ---
        # Note: Streamlit's native pie chart doesn't support a 'hole' for a donut chart.
        # We will use a bar chart instead to clearly show the breakdown.
        with left_col_2:
            st.subheader("Order Status Breakdown")
            status_counts = filtered_df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            st.bar_chart(status_counts.set_index('Status'))

        # --- 4. Top 10 Customers (Bar Chart) ---
        with right_col_2:
            st.subheader("Top 10 Customers by Spending")
            top_customers = fulfilled_orders.groupby("Customer Name")["Price"].sum().nlargest(10).reset_index()
            st.bar_chart(top_customers.sort_values('Price').set_index('Customer Name'))
        
        st.markdown("---")

        st.markdown("## 🌍 Geographic & Product Insights")
        left_col_3, right_col_3 = st.columns(2)

        # --- 5. Sales by Product Category (Bar Chart) ---
        if 'Product Category' in filtered_df.columns:
            with left_col_3:
                st.subheader("Sales by Product Category")
                category_sales = filtered_df.groupby('Product Category')['Price'].sum().sort_values(ascending=False).reset_index()
                st.bar_chart(category_sales.set_index('Product Category'))
        else:
            with left_col_3:
                st.info("The 'Product Category' column is not available in the dataset.")

        # --- 6. Sales by City (Map) ---
        # Note: Streamlit's native map functions require latitude/longitude,
        # and do not support dynamic scatter maps like Plotly.
        if 'City' in filtered_df.columns:
            with right_col_3:
                st.subheader("Sales by City")
                st.info("A map cannot be generated using Streamlit's native components without latitude and longitude data.")
                # Fallback to showing raw city data
                city_sales = filtered_df.groupby('City')['Price'].sum().reset_index()
                st.dataframe(city_sales)
        else:
            with right_col_3:
                st.info("The 'City' column is not available in the dataset. A map cannot be generated.")


        st.markdown("---")
        
        # --- 7. Weekly Order Patterns (Heatmap) ---
        # Note: Streamlit has no native heatmap component.
        # Displaying the raw data in a table is the best alternative.
        st.subheader("Weekly Order Patterns")
        filtered_df["DayOfWeek"] = filtered_df["Date"].dt.day_name()
        filtered_df["WeekOfMonth"] = filtered_df["Date"].dt.isocalendar().week
        
        heatmap_data = filtered_df.groupby(["DayOfWeek", "WeekOfMonth"]).size().unstack(fill_value=0)
        # Reorder days of the week
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = heatmap_data.reindex(day_order)
        
        st.dataframe(heatmap_data)

        # --- Raw Data Preview ---
        with st.expander("📄 View Raw Data"):
            st.dataframe(filtered_df)
