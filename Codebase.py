import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Interactive Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- DATA LOADING AND CLEANING ---
@st.cache_data
def load_and_clean_data(uploaded_file=None):
    """
    Loads data from a CSV, either from an upload or a local file,
    and performs necessary cleaning and transformations.
    
    Args:
        uploaded_file: The file object from st.file_uploader.
        
    Returns:
        A cleaned Pandas DataFrame or an empty DataFrame if an error occurs.
    """
    df = None
    
    # Check if a file is uploaded, otherwise, use a fallback local file.
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}")
            return pd.DataFrame()
    elif os.path.exists("July - Sheet1.csv"):
        st.info("No file uploaded. Loading local data from 'July - Sheet1.csv'.")
        df = pd.read_csv("July - Sheet1.csv")
    else:
        st.error("No data file found. Please upload a CSV file to begin.")
        return pd.DataFrame()

    if df.empty:
        return df

    # --- Step 2: Data Cleaning & Preparation ---
    # Ensure all required columns exist before proceeding
    required_cols = ['Date', 'Price', 'Status', 'Customer Name']
    
    # Add optional columns for new visualizations
    optional_cols = ['Product Category', 'City']
    all_cols = required_cols + optional_cols
    
    if not all(col in df.columns for col in required_cols):
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_cols)}")
        return pd.DataFrame()

    try:
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

        return df
    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return pd.DataFrame()

# --- SIDEBAR FOR FILE UPLOAD AND FILTERS ---
with st.sidebar:
    st.header("Upload & Filter Data")
    uploaded_file = st.file_uploader("Upload your sales CSV file", type="csv")
    
    st.markdown("---")
    st.subheader("Filter Data")

# --- MAIN PAGE LAYOUT ---
st.title("📊 Interactive Sales Dashboard")
st.markdown("Analyze your sales data to uncover trends and insights.")

# Load the data using the function
df = load_and_clean_data(uploaded_file)

if not df.empty:
    st.success("Data loaded and processed successfully!")

    # Add filters to the sidebar based on loaded data
    with st.sidebar:
        # Date filter
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        date_range = st.slider(
            "Select a Date Range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD"
        )
        
        # Status filter
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
            fig_daily_orders = px.line(
                daily_orders,
                x='Date',
                y='Order Count',
                title="Orders per Day",
                markers=True,
                labels={'Order Count': 'Number of Orders'}
            )
            fig_daily_orders.update_layout(xaxis_title="Date", yaxis_title="Number of Orders")
            st.plotly_chart(fig_daily_orders, use_container_width=True)

        # --- 2. Daily Revenue (Line Chart) ---
        with right_col:
            st.subheader("Daily Revenue")
            daily_revenue = filtered_df.groupby(filtered_df['Date'].dt.date)['Price'].sum().reset_index()
            fig_daily_revenue = px.line(
                daily_revenue,
                x='Date',
                y='Price',
                title="Revenue per Day",
                markers=True,
                labels={'Price': 'Total Revenue ($)'}
            )
            fig_daily_revenue.update_layout(xaxis_title="Date", yaxis_title="Revenue ($)")
            st.plotly_chart(fig_daily_revenue, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("## 📉 Sales Breakdown")
        left_col_2, right_col_2 = st.columns(2)

        # --- 3. Orders by Status (Donut Chart) ---
        with left_col_2:
            st.subheader("Order Status Breakdown")
            status_counts = filtered_df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.pie(
                status_counts,
                names='Status',
                values='Count',
                title="Proportion of Order Statuses",
                hole=0.4,
                color_discrete_map={
                    'Fulfilled': 'green',
                    'Cancelled': 'red',
                    'High Risk Order': 'orange',
                    'Returns': 'blue'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)

        # --- 4. Top 10 Customers (Bar Chart) ---
        with right_col_2:
            st.subheader("Top 10 Customers by Spending")
            top_customers = fulfilled_orders.groupby("Customer Name")["Price"].sum().nlargest(10).reset_index()
            fig_customers = px.bar(
                top_customers.sort_values('Price', ascending=True),
                x='Price',
                y='Customer Name',
                orientation='h',
                title="Top 10 Customers (Fulfilled Orders)",
                labels={'Price': 'Total Spent ($)', 'Customer Name': 'Customer'},
                color='Price',
                color_continuous_scale=px.colors.sequential.Teal
            )
            st.plotly_chart(fig_customers, use_container_width=True)
        
        st.markdown("---")

        st.markdown("## 🌍 Geographic & Product Insights")
        left_col_3, right_col_3 = st.columns(2)

        # --- 5. Sales by Product Category (Bar Chart) ---
        if 'Product Category' in filtered_df.columns:
            with left_col_3:
                st.subheader("Sales by Product Category")
                category_sales = filtered_df.groupby('Product Category')['Price'].sum().sort_values(ascending=False).reset_index()
                fig_category = px.bar(
                    category_sales,
                    x='Product Category',
                    y='Price',
                    title="Revenue per Product Category",
                    labels={'Price': 'Total Revenue ($)'}
                )
                st.plotly_chart(fig_category, use_container_width=True)
        else:
            with left_col_3:
                st.info("The 'Product Category' column is not available in the dataset.")

        # --- 6. Sales by City (Scatter Map) ---
        if 'City' in filtered_df.columns:
            with right_col_3:
                st.subheader("Sales by City")
                city_sales = filtered_df.groupby('City')['Price'].sum().reset_index()
                # Create a simple placeholder for latitude/longitude if not present
                city_sales['lat'] = 0
                city_sales['lon'] = 0
                fig_map = px.scatter_mapbox(
                    city_sales,
                    lat="lat",
                    lon="lon",
                    size="Price",
                    hover_name="City",
                    hover_data={"Price": True},
                    zoom=1,
                    height=400,
                    title="Total Revenue by City"
                )
                fig_map.update_layout(mapbox_style="carto-positron")
                st.plotly_chart(fig_map, use_container_width=True)
        else:
            with right_col_3:
                st.info("The 'City' column is not available in the dataset. A map cannot be generated.")


        st.markdown("---")
        
        # --- 7. Heatmap of Orders ---
        st.subheader("Weekly Order Patterns")
        filtered_df["DayOfWeek"] = filtered_df["Date"].dt.day_name()
        filtered_df["WeekOfMonth"] = filtered_df["Date"].dt.isocalendar().week
        
        heatmap_data = filtered_df.groupby(["DayOfWeek", "WeekOfMonth"]).size().unstack(fill_value=0)
        # Reorder days of the week
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = heatmap_data.reindex(day_order)
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Week of the Year", y="Day of Week", color="Number of Orders"),
            title="Heatmap of Order Volume by Day and Week",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # --- Raw Data Preview ---
        with st.expander("📄 View Raw Data"):
            st.dataframe(filtered_df)
