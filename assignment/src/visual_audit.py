import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class VisualAuditEngine:
    """
    Task 4: Visual Integrity Audit.
    Handles the rejection of 3D charts and implements Bivariate/Small Multiples alternatives.
    """
    
    def get_rejection_rationale(self) -> str:
        return (
            "The proposal for a 3D bar chart is REJECTED based on the following principles:\n"
            "1. **Lie Factor**: 3D perspective creates 'occlusion' where foreground bars hide background bars, "
            "and perspective distortion makes bars of equal value appear different sizes depending on their depth.\n"
            "2. **Data-Ink Ratio**: The 3D effect adds 'visual noise' (extra lines, shading, and depth axes) "
            "that does not represent data, lowering the efficiency of information transmission.\n"
            "3. **Scale Distortion**: It is notoriously difficult for humans to accurately map a 3D point back to "
            "a 2D axis scale, leading to misinterpretation of magnitudes."
        )

    def get_bivariate_mapping(self, df: pd.DataFrame) -> go.Figure:
        """
        Task 4: Implement a Bivariate Mapping solution.
        Bubble Chart: X=Pollution, Y=Population Density, Size=Pollution, Color=Region/Zone.
        """
        # Aggregate by station to get one point per sensor node
        agg_df = df.groupby(['locationId', 'city', 'zone']).agg({
            'pm25': 'mean',
            'pop_density': 'first'
        }).reset_index()

        # Filter for strictly positive PM2.5 to avoid Plotly size errors (requires size > 0)
        agg_df = agg_df[agg_df['pm25'] > 0].dropna(subset=['pm25'])

        fig = px.scatter(
            agg_df,
            x="pm25",
            y="pop_density",
            size="pm25",
            color="zone",
            hover_name="city",
            title="Bivariate Analysis: Pollution vs. Population Density",
            labels={
                "pm25": "Avg PM2.5 (µg/m³)",
                "pop_density": "Population Density (people/km²)",
                "zone": "City Zone"
            },
            template="simple_white"
        )
        
        # Remove grid clutter as per "No Graphical Ducks"
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        
        return fig

    def get_small_multiples(self, df: pd.DataFrame) -> go.Figure:
        """
        Task 4: Implement Small Multiples approach.
        Facetted view by Zone/Region.
        """
        # Monthly trend per zone
        trend_df = df.copy()
        trend_df['month'] = trend_df['date'].dt.month
        monthly_zone = trend_df.groupby(['zone', 'month'])['pm25'].mean().reset_index()
        
        fig = px.line(
            monthly_zone,
            x="month",
            y="pm25",
            facet_col="zone",
            title="Small Multiples: Seasonal Pollution Trends by Zone",
            labels={"pm25": "PM2.5", "month": "Month"},
            template="simple_white"
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        
        return fig

    def get_color_scale_justification(self) -> str:
        return (
            "We selected a **Sequential Luminance Scale** (e.g., Viridis or Blues) over a Rainbow scale. "
            "Rainbow scales (like Jet) lack 'perceptual uniformity'—the visual distance between colors does not "
            "match the numerical distance in the data. Sequential scales use monotonically increasing luminance, "
            "which aligns with human perception of 'more' vs 'less' and remains interpretable for colorblind "
            "users and black-and-white printing."
        )
