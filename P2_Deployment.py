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
            
            # Replace scatter with a simple bar chart
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
