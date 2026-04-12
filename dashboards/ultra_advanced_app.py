"""
=============================================================================
DASHBOARD ULTRA AVANCÉ - VISUALISATIONS SCIENTIFIQUES
=============================================================================
Graphiques scientifiques avancés avec Plotly
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plotly_template = "plotly_dark"

def load_data():
    files = sorted(glob.glob('data/processed/events_processed*.parquet'))
    if not files:
        return pd.DataFrame()
    df = pd.read_parquet(files[-1])
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['month'] = df['start_date'].dt.month
    df['day_of_week'] = df['start_date'].dt.dayofweek
    return df

app = dash.Dash(__name__)

colors = {
    'bg': '#0f1419',
    'card': '#1a1f26',
    'text': '#e4e6eb',
    'accent': '#0084f4',
}

app.layout = html.Div([
    html.Div([
        html.H1("🚀 ADVANCED ANALYTICS - Deep Dive", 
                style={'margin': 0, 'fontSize': 32, 'fontWeight': 700}),
    ], style={
        'padding': '24px 32px',
        'background': colors['card'],
        'borderBottom': f'2px solid {colors["accent"]}'
    }),
    
    html.Div([
        # Ligne 1: 3D Scatter + Violin
        html.Div([
            html.Div([dcc.Loading(dcc.Graph(id='scatter-3d'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
            html.Div([dcc.Loading(dcc.Graph(id='violin-plot'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
        ], style={'display': 'flex', 'gap': 16, 'marginBottom': 16}),
        
        # Ligne 2: Polar Radar
        html.Div([
            html.Div([dcc.Loading(dcc.Graph(id='polar-chart'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
            html.Div([dcc.Loading(dcc.Graph(id='histogram-2d'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
        ], style={'display': 'flex', 'gap': 16, 'marginBottom': 16}),
        
        # Ligne 3: Corr Matrix
        html.Div([dcc.Loading(dcc.Graph(id='correlation-matrix'))],
                style={'background': colors['card'], 'padding': 16, 'borderRadius': 8, 'marginBottom': 16}),
        
        # Ligne 4: Sankey + Funnel
        html.Div([
            html.Div([dcc.Loading(dcc.Graph(id='sankey-diagram'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
            html.Div([dcc.Loading(dcc.Graph(id='funnel-chart'))],
                    style={'flex': 1, 'background': colors['card'], 'padding': 16, 'borderRadius': 8}),
        ], style={'display': 'flex', 'gap': 16, 'marginBottom': 16}),
        
        # Ligne 5: Parallel Categories
        html.Div([dcc.Loading(dcc.Graph(id='parallel-categories'))],
                style={'background': colors['card'], 'padding': 16, 'borderRadius': 8, 'marginBottom': 16}),
        
        # Ligne 6: Calendar Heatmap Effect
        html.Div([dcc.Loading(dcc.Graph(id='temporal-heatmap'))],
                style={'background': colors['card'], 'padding': 16, 'borderRadius': 8, 'marginBottom': 16}),
    ],
    style={'padding': '0 32px 32px'}),
    
    dcc.Interval(id='interval-ultra', interval=15000, n_intervals=0),
], style={'backgroundColor': colors['bg'], 'minHeight': '100vh'})

@callback(
    [
        Output('scatter-3d', 'figure'),
        Output('violin-plot', 'figure'),
        Output('polar-chart', 'figure'),
        Output('histogram-2d', 'figure'),
        Output('correlation-matrix', 'figure'),
        Output('sankey-diagram', 'figure'),
        Output('funnel-chart', 'figure'),
        Output('parallel-categories', 'figure'),
        Output('temporal-heatmap', 'figure'),
    ],
    Input('interval-ultra', 'n_intervals')
)
def update_all(n):
    df = load_data()
    if df.empty:
        return [{} for _ in range(9)]
    
    # 1. 3D Scatter
    fig_3d = px.scatter_3d(
        df,
        x='latitude',
        y='longitude',
        z='severity_score',
        color='event_type',
        size='geometry_count',
        hover_name='title',
        title='3️⃣ 3D Space: Lat/Lon/Severity',
        template=plotly_template,
        height=400,
    )
    fig_3d.update_traces(marker=dict(size=5))
    
    # 2. Violin plot
    fig_violin = px.violin(
        df,
        x='event_type',
        y='severity_score',
        color='event_type',
        title='🎻 Severity Distribution Violin',
        template=plotly_template,
        height=400,
    )
    
    # 3. Polar/Radar
    severity_by_region = df.groupby('region')['severity_score'].mean().head(8)
    fig_polar = go.Figure(data=go.Scatterpolar(
        r=severity_by_region.values,
        theta=severity_by_region.index,
        fill='toself',
        name='Avg Severity'
    ))
    fig_polar.update_layout(
        title='🧭 Polar: Average Severity by Region',
        template=plotly_template,
        height=400,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        )
    )
    
    # 4. 2D Histogram
    fig_hist2d = px.density_heatmap(
        df,
        x='latitude',
        y='longitude',
        nbinsx=30,
        nbinsy=30,
        color_continuous_scale='Viridis',
        title='📊 2D Density: Geographic Hotspots',
        template=plotly_template,
        height=400,
    )
    
    # 5. Correlation Matrix
    numeric_cols = df[['severity_score', 'geometry_count', 'days_since_update']].select_dtypes(include=[np.number])
    corr_matrix = numeric_cols.corr()
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
    ))
    fig_corr.update_layout(
        title='🔗 Correlation Matrix',
        template=plotly_template,
        height=300,
    )
    
    # 6. Sankey Diagram
    source_regions = []
    target_types = []
    values = []
    
    for region in df['region'].unique()[:5]:
        for event_type in df['event_type'].unique()[:3]:
            count = len(df[(df['region'] == region) & (df['event_type'] == event_type)])
            if count > 0:
                source_regions.append(region)
                target_types.append(event_type)
                values.append(count)
    
    all_labels = list(set(source_regions + target_types))
    source_idx = [all_labels.index(r) for r in source_regions]
    target_idx = [all_labels.index(t) for t in target_types]
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(label=all_labels),
        link=dict(source=source_idx, target=target_idx, value=values)
    )])
    fig_sankey.update_layout(
        title='🌊 Sankey: Region → Event Type Flow',
        template=plotly_template,
        height=400,
    )
    
    # 7. Funnel Chart
    region_counts = df['region'].value_counts().head(8)
    fig_funnel = go.Figure(data=[go.Funnel(
        y=region_counts.index,
        x=region_counts.values,
    )])
    fig_funnel.update_layout(
        title='📉 Funnel: Top Regions Distribution',
        template=plotly_template,
        height=400,
    )
    
    # 8. Parallel Categories
    df_sample = df[['region', 'event_type', 'severity_category']].head(500)
    fig_parallel = px.parallel_categories(
        df_sample,
        dimensions=['region', 'event_type', 'severity_category'],
        title='🚂 Parallel Categories: Flow Analysis',
        template=plotly_template,
        height=400,
    )
    
    # 9. Temporal Heatmap (Events by Month and Event Type)
    temporal = df.groupby(['month', 'event_type']).size().unstack(fill_value=0)
    fig_temporal = go.Figure(data=go.Heatmap(
        z=temporal.values,
        x=temporal.columns,
        y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(temporal)],
        colorscale='YlOrRd',
    ))
    fig_temporal.update_layout(
        title='📅 Temporal Heatmap: Events by Month & Type',
        template=plotly_template,
        height=350,
    )
    
    return fig_3d, fig_violin, fig_polar, fig_hist2d, fig_corr, fig_sankey, fig_funnel, fig_parallel, fig_temporal

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
