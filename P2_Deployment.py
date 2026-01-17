import pandas as pd
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Performance Dashboard")
st.write("Analysis of Clustered Firms")

# Load the data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('clustered_firms_clean.csv')
        # Try to parse date if exists
        if 'Year' in df.columns:
            try:
                df['Year'] = pd.to_datetime(df['Year'], format='%Y-%m-%d')
            except:
                pass
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is not None:
    st.success(f"✅ Data loaded successfully: {len(df)} records")
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Companies", df['Ticker'].nunique())
    with col3:
        st.metric("Sectors", df['Sector'].nunique())
    with col4:
        st.metric("Clusters", df['Cluster'].nunique())
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_ticker = st.sidebar.selectbox(
        "Select Company:",
        sorted(df['Ticker'].unique())
    )
    
    selected_sector = st.sidebar.selectbox(
        "Select Sector:",
        sorted(df['Sector'].unique())
    )
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Company View", "Sector View", "Data Explorer"])
    
    with tab1:
        st.header("Company Analysis")
        company_data = df[df['Ticker'] == selected_ticker]
        
        if not company_data.empty:
            company_name = company_data['Name'].iloc[0]
            st.subheader(f"{company_name}")
            
            # Display metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            latest = company_data.iloc[-1] if len(company_data) > 0 else company_data.iloc[0]
            
            with metrics_col1:
                if 'ROA' in latest:
                    st.metric("ROA", f"{latest['ROA']:.2%}")
                if 'ROE' in latest:
                    st.metric("ROE", f"{latest['ROE']:.2%}")
            
            with metrics_col2:
                if 'Gross_Margin' in latest:
                    st.metric("Gross Margin", f"{latest['Gross_Margin']:.2%}")
                if 'Net_Margin' in latest:
                    st.metric("Net Margin", f"{latest['Net_Margin']:.2%}")
            
            with metrics_col3:
                if 'Debt_to_Equity' in latest:
                    st.metric("Debt/Equity", f"{latest['Debt_to_Equity']:.2f}")
                if 'Current_Ratio' in latest:
                    st.metric("Current Ratio", f"{latest['Current_Ratio']:.2f}")
            
            # Show company data
            st.dataframe(company_data, use_container_width=True)
        else:
            st.warning("No data for selected company")
    
    with tab2:
        st.header("Sector Analysis")
        sector_data = df[df['Sector'] == selected_sector]
        
        if not sector_data.empty:
            # Sector stats
            st.subheader(f"{selected_sector} Sector")
            st.write(f"**Companies in sector:** {sector_data['Ticker'].nunique()}")
            
            # Average metrics
            avg_roa = sector_data['ROA'].mean() if 'ROA' in sector_data.columns else 0
            avg_roe = sector_data['ROE'].mean() if 'ROE' in sector_data.columns else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average ROA", f"{avg_roa:.2%}")
            with col2:
                st.metric("Average ROE", f"{avg_roe:.2%}")
            
            # Top companies in sector
            st.subheader("Top Companies by ROA")
            if 'ROA' in sector_data.columns and 'Ticker' in sector_data.columns and 'Name' in sector_data.columns:
                top_companies = sector_data.sort_values('ROA', ascending=False)[['Ticker', 'Name', 'ROA', 'ROE']].head(10)
                st.dataframe(top_companies, use_container_width=True)
            
            # Cluster distribution
            st.subheader("Cluster Distribution")
            if 'Cluster' in sector_data.columns:
                cluster_counts = sector_data['Cluster'].value_counts()
                for cluster, count in cluster_counts.items():
                    st.write(f"**Cluster {cluster}:** {count} companies")
        else:
            st.warning("No data for selected sector")
    
    with tab3:
        st.header("Data Explorer")
        
        # Filter options
        filter_option = st.radio(
            "Show:",
            ["All Data", "Selected Company", "Selected Sector"],
            horizontal=True
        )
        
        if filter_option == "Selected Company":
            display_df = df[df['Ticker'] == selected_ticker]
        elif filter_option == "Selected Sector":
            display_df = df[df['Sector'] == selected_sector]
        else:
            display_df = df
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="financial_data.csv",
            mime="text/csv"
        )
    
    # Info in sidebar
    st.sidebar.divider()
    st.sidebar.info("""
    **Dashboard Features:**
    - Company financial metrics
    - Sector performance analysis  
    - Interactive data exploration
    """)
else:
    st.error("Could not load data. Please check the CSV file.")
