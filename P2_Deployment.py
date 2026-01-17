import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
        # Parse date
        if 'Year' in df.columns:
            df['Year'] = pd.to_datetime(df['Year'], format='%Y-%m-%d')
            df['Year_Display'] = df['Year'].dt.strftime('%Y')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is not None:
    st.success(f"✅ Data loaded successfully: {len(df)} records")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Create company display names: "Ticker - Company Name"
    df['Company_Display'] = df['Ticker'] + ' - ' + df['Name']
    
    # Get unique values
    company_options = sorted(df['Company_Display'].unique())
    sectors = sorted(df['Sector'].unique())
    clusters = sorted(df['Cluster'].unique())
    
    # Filters in sidebar
    selected_company_display = st.sidebar.selectbox(
        "Select Company:",
        company_options,
        index=0
    )
    
    # Extract ticker from selection
    selected_ticker = selected_company_display.split(' - ')[0] if selected_company_display else None
    
    selected_sector = st.sidebar.selectbox(
        "Select Sector:",
        sectors,
        index=0
    )
    
    selected_cluster = st.sidebar.selectbox(
        "Select Cluster:",
        clusters,
        index=0
    )
    
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
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Company View", "Sector View", "Cluster View", "📈 Visual Analysis"])
    
    with tab1:
        st.header("Company Analysis")
        if selected_ticker:
            company_data = df[df['Ticker'] == selected_ticker]
            
            if not company_data.empty:
                company_name = company_data['Name'].iloc[0]
                st.subheader(f"{company_name}")
                
                # Company info
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.write(f"**Ticker:** {selected_ticker}")
                    st.write(f"**Sector:** {company_data['Sector'].iloc[0]}")
                    st.write(f"**Industry:** {company_data['Industry'].iloc[0] if 'Industry' in company_data.columns else 'N/A'}")
                with info_col2:
                    st.write(f"**Cluster:** {company_data['Cluster'].iloc[0]}")
                    st.write(f"**Years of Data:** {company_data['Year'].nunique()}")
                    st.write(f"**Latest Year:** {company_data['Year'].max().strftime('%Y')}")
                
                st.divider()
                
                # Key metrics
                st.subheader("Key Financial Metrics")
                latest = company_data.iloc[-1] if len(company_data) > 0 else company_data.iloc[0]
                
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
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
                    if 'EBITDA_Margin' in latest:
                        st.metric("EBITDA Margin", f"{latest['EBITDA_Margin']:.2%}")
                    if 'Asset_Turnover' in latest:
                        st.metric("Asset Turnover", f"{latest['Asset_Turnover']:.2f}")
                
                with metrics_col4:
                    if 'Debt_to_Equity' in latest:
                        st.metric("Debt/Equity", f"{latest['Debt_to_Equity']:.2f}")
                    if 'Current_Ratio' in latest:
                        st.metric("Current Ratio", f"{latest['Current_Ratio']:.2f}")
                
                # Show company data
                st.subheader("Historical Data")
                st.dataframe(company_data.sort_values('Year', ascending=False), use_container_width=True)
    
    with tab2:
        st.header("Sector Analysis")
        sector_data = df[df['Sector'] == selected_sector]
        
        if not sector_data.empty:
            # Sector overview
            st.subheader(f"{selected_sector} Sector Overview")
            
            overview_col1, overview_col2, overview_col3 = st.columns(3)
            with overview_col1:
                st.metric("Companies", sector_data['Ticker'].nunique())
            with overview_col2:
                st.metric("Total Records", len(sector_data))
            with overview_col3:
                avg_roa = sector_data['ROA'].mean() if 'ROA' in sector_data.columns else 0
                st.metric("Average ROA", f"{avg_roa:.2%}")
            
            # Top companies
            st.subheader("Top Performing Companies")
            if 'ROA' in sector_data.columns:
                top_companies = sector_data.sort_values('ROA', ascending=False).head(10)
                display_cols = ['Ticker', 'Name', 'ROA', 'ROE', 'Net_Margin', 'Cluster']
                display_cols = [col for col in display_cols if col in top_companies.columns]
                st.dataframe(top_companies[display_cols], use_container_width=True)
    
    with tab3:
        st.header("Cluster Analysis")
        cluster_data = df[df['Cluster'] == selected_cluster]
        
        if not cluster_data.empty:
            # Cluster overview
            st.subheader(f"Cluster {selected_cluster} Overview")
            
            cluster_col1, cluster_col2, cluster_col3, cluster_col4 = st.columns(4)
            with cluster_col1:
                st.metric("Companies", cluster_data['Ticker'].nunique())
            with cluster_col2:
                st.metric("Sectors", cluster_data['Sector'].nunique())
            with cluster_col3:
                st.metric("Total Records", len(cluster_data))
            with cluster_col4:
                avg_roa = cluster_data['ROA'].mean() if 'ROA' in cluster_data.columns else 0
                st.metric("Average ROA", f"{avg_roa:.2%}")
            
            # Top companies in cluster
            st.subheader("Top Companies in Cluster")
            if 'ROA' in cluster_data.columns:
                top_cluster_companies = cluster_data.sort_values('ROA', ascending=False).head(10)
                display_cols = ['Ticker', 'Name', 'Sector', 'ROA', 'ROE', 'Net_Margin']
                display_cols = [col for col in display_cols if col in top_cluster_companies.columns]
                st.dataframe(top_cluster_companies[display_cols], use_container_width=True)
    
    with tab4:
        st.header("📈 Visual Analysis")
        
        # Create two columns for charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("1. Cluster Distribution")
            
            # Count companies per cluster
            cluster_counts = df['Cluster'].value_counts().reset_index()
            cluster_counts.columns = ['Cluster', 'Company Count']
            
            # Create donut chart
            fig1 = go.Figure(data=[go.Pie(
                labels=cluster_counts['Cluster'],
                values=cluster_counts['Company Count'],
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3),
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )])
            
            fig1.update_layout(
                title_text="Company Distribution by Cluster",
                title_font_size=16,
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Cluster summary table
            st.subheader("Cluster Summary")
            cluster_stats = df.groupby('Cluster').agg({
                'ROA': 'mean',
                'ROE': 'mean',
                'Ticker': 'nunique'
            }).round(4).reset_index()
            
            # Format percentages
            cluster_stats['ROA'] = cluster_stats['ROA'].apply(lambda x: f"{x:.2%}")
            cluster_stats['ROE'] = cluster_stats['ROE'].apply(lambda x: f"{x:.2%}")
            cluster_stats.columns = ['Cluster', 'Avg ROA', 'Avg ROE', 'Companies']
            
            st.dataframe(cluster_stats, use_container_width=True, hide_index=True)
        
        with col_right:
            st.subheader("2. Sector Performance")
            
            # Average ROA by sector
            sector_roa = df.groupby('Sector')['ROA'].mean().reset_index()
            sector_roa = sector_roa.sort_values('ROA', ascending=True)
            
            fig2 = px.bar(
                sector_roa,
                y='Sector',
                x='ROA',
                title='Average ROA by Sector',
                orientation='h',
                color='ROA',
                color_continuous_scale='Blues',
                text_auto='.2%'
            )
            
            fig2.update_layout(
                height=400,
                xaxis_title="Average ROA",
                yaxis_title="Sector",
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Top sectors by company count
            st.subheader("3. Top Sectors by Company Count")
            
            sector_counts = df['Sector'].value_counts().reset_index()
            sector_counts.columns = ['Sector', 'Company Count']
            sector_counts = sector_counts.head(8)  # Top 8 sectors
            
            fig3 = px.bar(
                sector_counts,
                x='Sector',
                y='Company Count',
                title='Number of Companies per Sector',
                color='Company Count',
                color_continuous_scale='Viridis',
                text_auto=True
            )
            
            fig3.update_layout(
                height=400,
                xaxis_title="Sector",
                yaxis_title="Number of Companies",
                xaxis_tickangle=45
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # Bottom section - Single line chart
        st.subheader("4. Top 5 Companies by ROA")
        
        # Get top 5 companies by average ROA
        company_avg_roa = df.groupby(['Ticker', 'Name']).agg({
            'ROA': 'mean',
            'Sector': 'first',
            'Cluster': 'first'
        }).reset_index()
        
        top_companies = company_avg_roa.nlargest(5, 'ROA')
        
        # Get historical data for these companies
        top_tickers = top_companies['Ticker'].tolist()
        top_data = df[df['Ticker'].isin(top_tickers)]
        
        if len(top_data) > 0:
            fig4 = px.line(
                top_data,
                x='Year_Display',
                y='ROA',
                color='Name',
                markers=True,
                title='ROA Trend for Top 5 Companies',
                line_shape='linear'
            )
            
            fig4.update_layout(
                height=400,
                xaxis_title="Year",
                yaxis_title="ROA",
                yaxis_tickformat=".0%",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig4, use_container_width=True)
            
            # Show top companies table
            top_companies_display = top_companies[['Ticker', 'Name', 'Sector', 'Cluster', 'ROA']]
            top_companies_display['ROA'] = top_companies_display['ROA'].apply(lambda x: f"{x:.2%}")
            top_companies_display.columns = ['Ticker', 'Company Name', 'Sector', 'Cluster', 'Average ROA']
            
            st.dataframe(top_companies_display, use_container_width=True, hide_index=True)
    
    # Info in sidebar
    st.sidebar.divider()
    st.sidebar.info("""
    **Dashboard Tabs:**
    1. **Company**: Detailed financials
    2. **Sector**: Sector-level analysis  
    3. **Cluster**: Cluster characteristics
    4. **Visual**: Key charts & insights
    """)
    
    # Download option
    st.sidebar.divider()
    if st.sidebar.button("📥 Download Dataset"):
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Click to Download",
            data=csv,
            file_name="financial_data.csv",
            mime="text/csv"
        )
else:
    st.error("Could not load data. Please check the CSV file.")
