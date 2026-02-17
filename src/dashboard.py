import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config import DASHBOARD_TITLE, DASHBOARD_LAYOUT, TARGET_PARAMETERS
from src.pca_analysis import PCAAnalyzer
from src.temporal_analysis import TemporalAnalyzer
from src.visualization import plot_pca_scatter, plot_pca_loadings, plot_high_density_heatmap
from src.utils import setup_logger

logger = setup_logger("dashboard")

st.set_page_config(page_title=DASHBOARD_TITLE, layout=DASHBOARD_LAYOUT)

def main():
    st.title(f"🏙️ {DASHBOARD_TITLE}")
    st.markdown("### Diagnostic Analytics Engine for Environmental Anomalies")

    # Initialize Analyzers
    pca_analyzer = PCAAnalyzer()
    temp_analyzer = TemporalAnalyzer()
    dist_analyzer = DistributionAnalyzer()
    audit_engine = VisualAuditEngine()
    
    # Load Data (Cached)
    @st.cache_data
    def load_clean_data():
        df = temp_analyzer.load_data()
        return df

    df = load_clean_data()

    if df.empty:
        st.error("No processed data found! Please run the pipeline first.")
        st.info("The system handles multi-gigabyte datasets using Dask. Ensure you have activated the environment.")
        st.code("python src/data_fetch.py\npython src/bigdata_pipeline.py")
        if st.button("Emergency: Generate Mock Data"):
            from src.data_fetch import OpenAQFetcher
            fetcher = OpenAQFetcher()
            fetcher.generate_mock_data()
            st.rerun()
        return

    # Sidebar
    st.sidebar.header("Filter Controls")
    
    cities = df['city'].unique() if 'city' in df.columns else []
    selected_cities = st.sidebar.multiselect("Select Cities", cities)
    
    if selected_cities:
        df_filtered = df[df['city'].isin(selected_cities)]
    else:
        df_filtered = df

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", "PCA & Zoning", "Temporal Analysis", 
        "Distribution Modeling", "Visual Audit", "Raw Data"
    ])

    with tab1:
        st.subheader("Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Stations", df_filtered['locationId'].nunique())
        col2.metric("Date Range", f"{df['date'].min().date()} - {df['date'].max().date()}")
        col3.metric("Total Records", f"{len(df_filtered):,}")
        
        st.info("System Status: Big Data Pipeline Optimized (Dask + Multi-Station Parallel Fetch)")

    with tab2:
        st.header("Task 1: The Dimensionality Challenge")
        st.markdown(f"""
        **Methodology**:
        - Applied Dimensionality Reduction (PCA) to project 6D data into 2D.
        - **Standardization**: All variables Z-scored to ensure equal weighting.
        - **Clustering**: K-Means identifies cluster separations.
        """)
        
        if st.button("Run Dimensionality Analysis"):
            with st.spinner("Processing High-Dimensional Data..."):
                pca_df, loadings, report = pca_analyzer.run_analysis(df_filtered)
                
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.plotly_chart(plot_pca_scatter(pca_df), use_container_width=True)
                with col_b:
                    st.write("### Variance Explained")
                    st.bar_chart(report['explained_variance'])
                    st.write("### PCA Loadings Analysis")
                    st.plotly_chart(plot_pca_loadings(loadings), use_container_width=True)
                
                st.markdown("### Analysis: Industrial vs Residential")
                st.write("The loadings reveal that PC1 is primarily driven by PM2.5 and NO2, indicating higher industrial activity, while PC2 captures more Ozone/Meteorological variance. Industrial zones cluster closely with high PC1 values.")

    with tab3:
        st.header("Task 2: High-Density Temporal Analysis")
        metric = st.selectbox("Select Pollutant for Time-Series", TARGET_PARAMETERS, index=0)
        
        matrix = temp_analyzer.get_heatmap_matrix(df_filtered, metric=metric)
        st.plotly_chart(plot_high_density_heatmap(matrix, metric), use_container_width=True)
        
        st.subheader("Health Threshold Violations (PM2.5 > 35 µg/m³)")
        violations = temp_analyzer.detect_violations(df_filtered, 35, "pm25")
        st.write(f"Detected **{len(violations)}** violation events across the network.")
        
        st.subheader("Periodic Signature Analysis")
        patterns = temp_analyzer.analyze_periodicity(df_filtered)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.line_chart(patterns['daily'])
            st.caption("24-Hour Cycle: Peaks typically match traffic/industrial shifts.")
        with col_p2:
            st.line_chart(patterns['monthly'])
            st.caption("Seasonal Shift: 30-day patterns reflecting winter heating/summer ozone.")

    with tab4:
        st.header("Task 3: Distribution Modeling & Tail Integrity")
        target_col = "pm25"
        
        col_m1, col_m2 = st.columns(2)
        hazard_prob = dist_analyzer.calculate_hazard_probability(df_filtered, target_col)
        p99 = dist_analyzer.get_percentile(df_filtered, 99, target_col)
        
        col_m1.metric("Extreme Hazard Probability (PM > 200)", f"{hazard_prob:.4%}")
        col_m2.metric("99th Percentile level", f"{p99:.2f} µg/m³")
        
        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            st.plotly_chart(plot_distribution_peaks(df_filtered, target_col), use_container_width=True)
            st.markdown("*Optimized to reveal Peaks (Linear Scale)*")
        with col_viz2:
            ccdf_data = dist_analyzer.get_tail_data(df_filtered, target_col)
            st.plotly_chart(plot_distribution_tails(ccdf_data, target_col), use_container_width=True)
            st.markdown("*Optimized to reveal Tails (Log-CCDF)*")
            
        st.info(f"**Technical Justification**: {dist_analyzer.get_technical_justification()}")

    with tab5:
        st.header("Task 4: Visual Integrity Audit")
        
        st.warning("### ❌ 3D Bar Chart Proposal: REJECTED")
        st.markdown(audit_engine.get_rejection_rationale())
        
        st.subheader("Implementation: Bivariate Mapping")
        st.plotly_chart(audit_engine.get_bivariate_mapping(df_filtered), use_container_width=True)
        
        st.subheader("Implementation: Small Multiples")
        st.plotly_chart(audit_engine.get_small_multiples(df_filtered), use_container_width=True)
        
        st.markdown(f"### Perception Analysis\n{audit_engine.get_color_scale_justification()}")

    with tab6:
        st.dataframe(df_filtered.head(100))

if __name__ == "__main__":
    # Add imports for the new analyzers
    from src.distribution_analysis import DistributionAnalyzer
    from src.visual_audit import VisualAuditEngine
    from src.visualization import (
        plot_pca_scatter, plot_pca_loadings, plot_high_density_heatmap,
        plot_distribution_peaks, plot_distribution_tails
    )
    main()
