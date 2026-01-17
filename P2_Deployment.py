import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Financial Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load the data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('clustered_firms_clean.csv')
        df['Year'] = pd.to_datetime(df['Year'], format='%Y-%m-%d')
        return df
    except FileNotFoundError:
        st.error("File not found. Please ensure 'clustered_firms_clean.csv' is uploaded.")
        return None

df = load_data()

if df is not None:
    # Title
    st.title("📊 Financial Performance Dashboard")
    st.subheader("Analysis of Clustered Firms")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get unique values
    tickers = sorted(df['Ticker'].unique())
    sectors = sorted(df['Sector'].unique())
    clusters = sorted(df['Cluster'].unique())
    
    # Filters in sidebar
    selected_ticker = st.sidebar.selectbox(
        "Select Company:",
        tickers,
        index=0
    )
    
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
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Company Analysis", 
        "📈 Sector Analysis", 
        "👥 Cluster Analysis", 
        "📋 Data Explorer"
    ])
    
    with tab1:
        st.header("Company Analysis")
        
        # Filter data for selected company
        company_data = df[df['Ticker'] == selected_ticker].sort_values('Year')
        if not company_data.empty:
            company_name = company_data['Name'].iloc[0]
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📈 Profitability Trends - {company_name}")
                
                # Profitability Trends Chart
                fig1 = go.Figure()
                margin_metrics = ['Gross_Margin', 'Operating_Margin', 'Net_Margin', 'EBITDA_Margin']
                colors = ['blue', 'green', 'red', 'orange']
                
                for metric, color in zip(margin_metrics, colors):
                    fig1.add_trace(go.Scatter(
                        x=company_data['Year'].dt.strftime('%Y-%m-%d'),
                        y=company_data[metric],
                        name=metric.replace('_', ' '),
                        mode='lines+markers',
                        line=dict(color=color, width=2)
                    ))
                
                fig1.update_layout(
                    height=400,
                    xaxis_title="Year",
                    yaxis_title="Margin",
                    yaxis_tickformat=".0%",
                    hovermode="x unified"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("📊 Financial Ratios - Latest Year")
                
                # Latest year data
                latest_data = company_data.iloc[-1]
                ratio_data = {
                    'ROE': latest_data['ROE'],
                    'ROA': latest_data['ROA'],
                    'Asset Turnover': latest_data['Asset_Turnover'],
                    'Interest Coverage': latest_data['Interest_Coverage'] if latest_data['Interest_Coverage'] != 0 else 0,
                    'Debt/Equity': latest_data['Debt_to_Equity']
                }
                
                fig2 = go.Figure(data=[
                    go.Bar(
                        x=list(ratio_data.keys()),
                        y=list(ratio_data.values()),
                        marker_color=['blue', 'green', 'orange', 'red', 'purple']
                    )
                ])
                fig2.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("💰 Working Capital Metrics")
                
                # Working Capital Chart
                fig3 = go.Figure()
                wc_metrics = ['Inventory_Days', 'Receivables_Days', 'Payables_Days']
                wc_names = ['Inventory Days', 'Receivables Days', 'Payables Days']
                wc_colors = ['blue', 'green', 'orange']
                
                for metric, name, color in zip(wc_metrics, wc_names, wc_colors):
                    fig3.add_trace(go.Scatter(
                        x=company_data['Year'].dt.strftime('%Y-%m-%d'),
                        y=company_data[metric],
                        name=name,
                        mode='lines+markers',
                        line=dict(color=color, width=2)
                    ))
                
                fig3.update_layout(
                    height=400,
                    xaxis_title="Year",
                    yaxis_title="Days",
                    hovermode="x unified"
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                st.subheader("🎯 ROA Prediction Comparison")
                
                # ROA Prediction
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    x=['Actual ROA', 'Predicted ROA'],
                    y=[latest_data['ROA'], latest_data['Predicted_ROA']],
                    marker_color=['blue', 'green']
                ))
                fig4.update_layout(
                    height=400,
                    yaxis_title="Value",
                    yaxis_tickformat=".1%",
                    showlegend=False
                )
                st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No data available for selected company.")
    
    with tab2:
        st.header("Sector Analysis")
        
        # Filter data for selected sector
        sector_data = df[df['Sector'] == selected_sector]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Sector Performance Trends")
            
            # Aggregate by year
            sector_data['Year_str'] = sector_data['Year'].dt.strftime('%Y-%m-%d')
            avg_by_year = sector_data.groupby('Year_str').agg({
                'ROA': 'mean',
                'ROE': 'mean',
                'Net_Margin': 'mean',
                'Gross_Margin': 'mean'
            }).reset_index()
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Average ROA', 'Average ROE', 'Average Net Margin', 'Average Gross Margin']
            )
            
            metrics = [('ROA', 1, 1), ('ROE', 1, 2), 
                       ('Net_Margin', 2, 1), ('Gross_Margin', 2, 2)]
            
            for metric, row, col in metrics:
                fig.add_trace(
                    go.Scatter(
                        x=avg_by_year['Year_str'],
                        y=avg_by_year[metric],
                        mode='lines+markers',
                        line=dict(width=3),
                        marker=dict(size=10)
                    ),
                    row=row, col=col
                )
                
                fig.update_yaxes(tickformat=".1%", row=row, col=col)
                fig.update_xaxes(title_text="Year", row=row, col=col)
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(f"📦 Cluster Distribution in {selected_sector}")
            
            # Cluster Distribution Pie Chart
            cluster_counts = sector_data['Cluster'].value_counts().reset_index()
            cluster_counts.columns = ['Cluster', 'Count']
            
            fig_pie = px.pie(
                cluster_counts,
                values='Count',
                names=[f'Cluster {c}' for c in cluster_counts['Cluster']],
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.subheader("📊 Performance by Cluster")
            
            # Box plots for comparison
            fig_box = go.Figure()
            comparison_metric = st.selectbox(
                "Select metric for comparison:",
                ['ROA', 'Net_Margin', 'Debt_to_Equity', 'Current_Ratio'],
                key="sector_metric"
            )
            
            clusters_in_sector = sector_data['Cluster'].unique()
            for cluster in clusters_in_sector:
                cluster_data = sector_data[sector_data['Cluster'] == cluster][comparison_metric]
                fig_box.add_trace(go.Box(
                    y=cluster_data,
                    name=f'Cluster {cluster}',
                    boxpoints='outliers'
                ))
            
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.header("Cluster Analysis")
        
        # Filter data for selected cluster
        cluster_data = df[df['Cluster'] == selected_cluster]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📈 Performance by Sector - Cluster {selected_cluster}")
            
            # Aggregate by sector
            avg_by_sector = cluster_data.groupby('Sector').agg({
                'ROA': 'mean',
                'ROE': 'mean',
                'Net_Margin': 'mean'
            }).reset_index()
            
            fig_cluster = go.Figure(data=[
                go.Bar(name='ROA', x=avg_by_sector['Sector'], y=avg_by_sector['ROA']),
                go.Bar(name='ROE', x=avg_by_sector['Sector'], y=avg_by_sector['ROE']),
                go.Bar(name='Net Margin', x=avg_by_sector['Sector'], y=avg_by_sector['Net_Margin'])
            ])
            
            fig_cluster.update_layout(
                barmode='group',
                height=500,
                yaxis_title="Value",
                yaxis_tickformat=".1%",
                xaxis_title="Sector"
            )
            st.plotly_chart(fig_cluster, use_container_width=True)
        
        with col2:
            st.subheader(f"🎯 Cluster Profile - Radar Chart")
            
            # Average metrics for radar chart
            avg_metrics = cluster_data[['ROA', 'ROE', 'Net_Margin', 'Gross_Margin', 
                                        'Current_Ratio', 'Asset_Turnover']].mean()
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=avg_metrics.values,
                theta=avg_metrics.index.str.replace('_', ' '),
                fill='toself',
                line_color='blue',
                opacity=0.8
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(avg_metrics.values) * 1.2]
                    )
                ),
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        st.subheader(f"🔍 ROA vs Debt/Equity - Cluster {selected_cluster}")
        
        # Scatter plot
        cluster_data['Year_display'] = cluster_data['Year'].dt.strftime('%Y-%m-%d')
        fig_scatter = px.scatter(
            cluster_data,
            x='Debt_to_Equity',
            y='ROA',
            color='Sector',
            size='Current_Ratio',
            hover_data=['Ticker', 'Name', 'Year_display'],
            title=f'ROA vs Debt/Equity'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.header("Data Explorer")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📋 Financial Data")
            
            # Filter options
            filter_option = st.radio(
                "Filter by:",
                ["All Data", "Selected Company", "Selected Sector", "Selected Cluster"],
                horizontal=True
            )
            
            if filter_option == "Selected Company":
                display_df = df[df['Ticker'] == selected_ticker]
            elif filter_option == "Selected Sector":
                display_df = df[df['Sector'] == selected_sector]
            elif filter_option == "Selected Cluster":
                display_df = df[df['Cluster'] == selected_cluster]
            else:
                display_df = df.copy()
            
            # Format for display
            display_df = display_df.copy()
            
            # Format Year for display
            display_df['Year_display'] = display_df['Year'].dt.strftime('%Y-%m-%d')
            
            # Format percentage columns
            pct_cols = ['Gross_Margin', 'Operating_Margin', 'Net_Margin', 'EBITDA_Margin', 
                        'ROE', 'ROA', 'Predicted_ROA']
            for col in pct_cols:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
            
            # Select columns to display
            cols_to_show = ['Ticker', 'Name', 'Sector', 'Industry', 'Year_display', 
                           'Gross_Margin', 'Operating_Margin', 'Net_Margin', 'ROA', 'ROE',
                           'Cluster', 'Predicted_ROA']
            display_cols = [col for col in cols_to_show if col in display_df.columns]
            
            st.dataframe(display_df[display_cols], height=400)
        
        with col2:
            st.subheader("📊 Summary Statistics")
            
            # Basic stats
            st.metric("Total Records", len(df))
            st.metric("Unique Companies", df['Ticker'].nunique())
            st.metric("Sectors", df['Sector'].nunique())
            st.metric("Clusters", df['Cluster'].nunique())
            
            st.divider()
            
            # Selected metric statistics
            selected_metric = st.selectbox(
                "View statistics for:",
                ['ROA', 'ROE', 'Net_Margin', 'Gross_Margin', 'Debt_to_Equity'],
                key="stats_metric"
            )
            
            if selected_metric in df.columns:
                col = df[selected_metric]
                st.write(f"**{selected_metric.replace('_', ' ')}**")
                st.write(f"Mean: {col.mean():.4f}")
                st.write(f"Min: {col.min():.4f}")
                st.write(f"Max: {col.max():.4f}")
                st.write(f"Std: {col.std():.4f}")
    
    # Add some info in sidebar
    st.sidebar.divider()
    st.sidebar.info("""
    **Dashboard Features:**
    - Company financial analysis
    - Sector performance comparison
    - Cluster profiling
    - Interactive data exploration
    """)
else:
    st.error("Please upload 'clustered_firms_clean.csv' to use this dashboard.")