import streamlit as st
import pandas as pd
import io
import plotly.express as px

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
        return pd.DataFrame()
        
    # Convert the public sharing URL to a CSV export URL
    try:
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
        
        # Drop rows where all values are empty
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
st.title("🚀 Next-Gen Sales Dashboard")
st.markdown("A comprehensive tool for analyzing your sales performance and trends.")

# --- SIDEBAR FOR URL AND FILTERS ---
with st.sidebar:
    st.header("1. Data Source")
    sheet_url = st.text_input("Enter your public Google Sheets URL:", value="")
    load_button = st.button("Load Data")
    st.markdown("---")
    
    st.header("2. Filters")
    st.markdown("Refine your view by selecting a date range and order status.")

# Load data only when the button is clicked
df = pd.DataFrame()
if load_button and sheet_url:
    df = load_and_clean_data(sheet_url)

if not df.empty:
    # --- DYNAMIC FILTERS ---
    with st.sidebar:
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        date_range = st.slider(
            "Select a Date Range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD"
        )
        
        all_statuses = ["All"] + sorted(list(df['Status'].unique()))
        selected_statuses = st.multiselect(
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
        st.header("Summary of Key Metrics")
        
        fulfilled_orders = filtered_df[filtered_df['Status'] == 'Fulfilled']
        
        total_revenue = fulfilled_orders['Price'].sum()
        total_orders = len(filtered_df)
        fulfilled_count = len(fulfilled_orders)
        avg_order_value = total_revenue / fulfilled_count if fulfilled_count > 0 else 0
        
        # Delta calculation for a more insightful metric
        previous_period_df = df[df['Date'] < date_range[0]]
        previous_revenue = previous_period_df[previous_period_df['Status'] == 'Fulfilled']['Price'].sum()
        revenue_delta = total_revenue - previous_revenue if previous_revenue > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Revenue (Fulfilled)", f"${total_revenue:,.2f}", delta=f"{revenue_delta:,.2f} from previous period")
        with col2:
            st.metric("Total Orders", f"{total_orders:,}")
        with col3:
            st.metric("Average Order Value", f"${avg_order_value:,.2f}")
            
        st.markdown("---")
        
        # --- VISUALIZATIONS IN COLLAPSIBLE SECTIONS ---
        with st.expander("📈 Sales Trends & Patterns", expanded=True):
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Daily Revenue Trend")
                daily_revenue = filtered_df.groupby(filtered_df['Date'].dt.date)['Price'].sum().reset_index()
                fig = px.line(daily_revenue, x='Date', y='Price', title="Revenue Over Time", markers=True, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                
            with col_chart2:
                st.subheader("Daily Order Volume")
                daily_orders = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index(name='Order Count')
                fig = px.bar(daily_orders, x='Date', y='Order Count', title="Order Volume Over Time", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            st.subheader("Order Patterns by Day of the Week")
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            sales_by_day = filtered_df.groupby(filtered_df['Date'].dt.day_name())['Price'].sum().reindex(day_order).reset_index()
            fig = px.bar(sales_by_day, x='Date', y='Price', title="Total Revenue by Day of the Week", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📊 Sales Breakdown & Customer Insights"):
            col_chart3, col_chart4 = st.columns(2)
            
            with col_chart3:
                st.subheader("Order Status Breakdown")
                status_counts = filtered_df['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                fig = px.pie(status_counts, values='Count', names='Status', title="Order Status", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                
            with col_chart4:
                st.subheader("Top Customers by Spending")
                top_customers = fulfilled_orders.groupby("Customer Name")["Price"].sum().nlargest(10).reset_index()
                fig = px.bar(top_customers, x='Price', y='Customer Name', orientation='h', title="Top 10 Customers", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")

            st.subheader("Customer Value Treemap")
            fig = px.treemap(top_customers, path=[px.Constant("Top Customers"), 'Customer Name'], values='Price', title="Top Customers Treemap", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📄 Raw Data Table"):
            st.header("Raw Data Preview")
            st.dataframe(filtered_df)
```
<file path="requirements.txt">
plotly
pandas
streamlit
</fi
