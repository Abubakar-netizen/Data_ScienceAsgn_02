import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional

# Minimalist design constraints
TEMPLATE = "simple_white"

def plot_pca_scatter(df: pd.DataFrame, x: str = 'PC1', y: str = 'PC2', color: str = 'Cluster') -> go.Figure:
    """
    2D PCA Projection Visualization.
    """
    fig = px.scatter(
        df, 
        x=x, 
        y=y, 
        color=color,
        hover_data=['city', 'pm25', 'no2'],
        title="PCA: Environmental Zones (2D Projection)",
        template=TEMPLATE,
        opacity=0.7
    )
    fig.update_layout(
        xaxis_title="Principal Component 1",
        yaxis_title="Principal Component 2",
        legend_title="Cluster Zone"
    )
    return fig

def plot_pca_loadings(loadings: pd.DataFrame) -> go.Figure:
    """
    Visualizes the axis loadings (feature importance).
    """
    # Loadings heatmap or bar
    fig = px.imshow(
        loadings,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="PCA Loadings: Feature Contributions",
        template=TEMPLATE
    )
    return fig

def plot_high_density_heatmap(matrix: pd.DataFrame, metric: str = "PM2.5") -> go.Figure:
    """
    High-density temporal heatmap (Stations x Time).
    """
    fig = px.imshow(
        matrix,
        aspect="auto",
        color_continuous_scale="Viridis", # robust for colorblindness usually, or standard sequential
        title=f"High-Density Temporal Map: {metric} across 100 Stations",
        template=TEMPLATE
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Station ID"
    )
    return fig

def plot_daily_pattern(daily_pattern: pd.DataFrame) -> go.Figure:
    """
    Line chart for daily average cycles.
    """
    fig = px.line(
        daily_pattern, 
        title="Average Daily Pollution Cycle (24h)",
        template=TEMPLATE,
        labels={"value": "Pollution Level", "date": "Hour of Day"}
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def plot_distribution_peaks(df: pd.DataFrame, col: str = "pm25") -> go.Figure:
    """
    Task 3: Histogram revealing peaks (linear scale).
    """
    fig = px.histogram(
        df, 
        x=col, 
        nbins=50,
        title=f"Distribution of {col.upper()}: Peak Analysis",
        template=TEMPLATE,
        color_discrete_sequence=['#2ecc71']
    )
    fig.update_layout(xaxis_title=f"{col.upper()} (µg/m³)", yaxis_title="Frequency")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def plot_distribution_tails(ccdf_df: pd.DataFrame, col: str = "pm25") -> go.Figure:
    """
    Task 3: CCDF plot revealing tails (Log execution).
    """
    fig = px.line(
        ccdf_df, 
        x="value", 
        y="ccdf",
        title=f"Tail Integrity: Log-CCDF of {col.upper()}",
        template=TEMPLATE,
        log_y=True
    )
    fig.update_layout(xaxis_title=f"{col.upper()} Value", yaxis_title="P(X > x) [Log Scale]")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig
