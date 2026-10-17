"""Reusable Plotly visualizations for the climate dashboard."""

import numpy as np
import plotly.graph_objects as go
import xarray as xr


def build_state_heatmap(
    data: xr.DataArray,
    outline_coords: tuple[list[float], list[float]],
    state_name: str,
    variable_label: str,
    units: str,
    colorscale: str,
) -> go.Figure:
    """Build a boundary-masked state heatmap without external map services.

    The chart uses the dataset's longitude and latitude coordinates directly,
    which keeps the dashboard usable when an internet basemap is unavailable.
    NaN values outside the selected state remain transparent.
    """
    if data.ndim != 2 or "lat" not in data.coords or "lon" not in data.coords:
        raise ValueError("State heatmap data must have two dimensions: lat and lon.")

    lon_outline, lat_outline = outline_coords
    values = np.asarray(data.values, dtype=float)

    figure = go.Figure()
    figure.add_trace(
        go.Heatmap(
            x=data.lon.values,
            y=data.lat.values,
            z=values,
            colorscale=colorscale,
            colorbar={"title": units, "thickness": 14},
            hovertemplate=(
                "Longitude: %{x:.2f}°<br>"
                "Latitude: %{y:.2f}°<br>"
                f"{variable_label}: %{{z:.2f}} {units}<extra></extra>"
            ),
            zsmooth="best",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=lon_outline,
            y=lat_outline,
            mode="lines",
            line={"color": "#172033", "width": 2},
            hoverinfo="skip",
            name=f"{state_name} boundary",
            showlegend=False,
        )
    )
    figure.update_layout(
        title={"text": f"{state_name} · {variable_label}", "x": 0.02},
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        height=540,
        xaxis={"title": "Longitude", "showgrid": False},
        yaxis={
            "title": "Latitude",
            "showgrid": False,
            "scaleanchor": "x",
            "scaleratio": 1,
        },
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure
