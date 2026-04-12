"""
=============================================================================
DASHBOARD AVANCÉ - VISUALISATIONS ENRICHIES
=============================================================================
Graphiques avancés et analyses interactives complètes
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import numpy as np
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Plotly
plotly_template = "plotly_dark"

# Charger les données
def load_data():
    """Charge le dernier fichier parquet"""
    files = sorted(glob.glob('data/processed/events_processed*.parquet'))
    if not files:
        logger.error("Aucun fichier parquet trouvé")
        return pd.DataFrame()
    
    latest_file = files[-1]
    logger.info(f"Chargement: {latest_file}")
    df = pd.read_parquet(latest_file)
    df['start_date'] = pd.to_datetime(df['start_date'])
    return df

# Initialiser l'application
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Couleurs
colors = {
    'bg': '#0f1419',
    'card': '#1a1f26',
    'text': '#e4e6eb',
    'accent': '#0084f4',
    'danger': '#f44236',
    'success': '#31a24c',
    'warning': '#ffa500',
}

app.config.suppress_callback_exceptions = True

# Layout
app.layout = html.Div(
    [
        # En-tête
        html.Div(
            [
                html.Div(
                    [
                        html.H1("🌍 GLOBAL DISASTERS ANALYTICS", 
                                style={'margin': 0, 'fontSize': 28, 'fontWeight': 700}),
                        html.P("Analyse interactive des catastrophes naturelles",
                               style={'color': colors['text'], 'margin': '8px 0 0 0', 'opacity': 0.7}),
                    ]
                ),
                dcc.Interval(id='interval', interval=10000, n_intervals=0)
            ],
            style={
                'padding': '24px 32px',
                'background': colors['card'],
                'borderBottom': f'1px solid {colors["accent"]}',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            }
        ),
        
        # Filtres
        html.Div(
            [
                html.Div([
                    html.Label("Type d'événement:", style={'fontWeight': 600}),
                    dcc.Dropdown(
                        id='event-type-filter',
                        multi=True,
                        style={'backgroundColor': colors['card'], 'color': colors['text']},
                        clearable=True
                    )
                ], style={'flex': 1, 'marginRight': '16px'}),
                
                html.Div([
                    html.Label("Région:", style={'fontWeight': 600}),
                    dcc.Dropdown(
                        id='region-filter',
                        multi=True,
                        style={'backgroundColor': colors['card'], 'color': colors['text']},
                        clearable=True
                    )
                ], style={'flex': 1}),
            ],
            style={
                'display': 'flex',
                'padding': '20px 32px',
                'gap': '16px',
                'background': colors['card'],
                'borderBottom': f'1px solid {colors["accent"]}40'
            }
        ),
        
        # KPIs
        html.Div(
            id='kpi-container',
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '16px',
                'padding': '24px 32px',
                'background': colors['bg']
            }
        ),
        
        # Graphiques principaux
        html.Div(
            [
                # Ligne 1: Map + Distribution
                html.Div(
                    [
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='world-map'))],
                            style={'flex': '2', 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='severity-dist'))],
                            style={'flex': '1', 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                    ],
                    style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}
                ),
                
                # Ligne 2: Heatmap + Timeline
                html.Div(
                    [
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='heatmap-region-type'))],
                            style={'flex': 1, 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                    ],
                    style={'marginBottom': '16px'}
                ),
                
                # Ligne 3: Timeline par région
                html.Div(
                    [dcc.Loading(dcc.Graph(id='timeline-by-region'))],
                    style={'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40', 'marginBottom': '16px'}
                ),
                
                # Ligne 4: Scatter avancés
                html.Div(
                    [
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='scatter-magnitude'))],
                            style={'flex': 1, 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='box-severity'))],
                            style={'flex': 1, 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                    ],
                    style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}
                ),
                
                # Ligne 5: Sunburst + Bar horizontale
                html.Div(
                    [
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='sunburst-chart'))],
                            style={'flex': 1, 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                        html.Div(
                            [dcc.Loading(dcc.Graph(id='top-regions-bar'))],
                            style={'flex': 1, 'background': colors['card'], 'borderRadius': 8, 'padding': 16, 'border': f'1px solid {colors["accent"]}40'}
                        ),
                    ],
                    style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}
                ),
            ],
            style={'padding': '0 32px 32px'}
        ),
    ],
    style={'backgroundColor': colors['bg'], 'minHeight': '100vh'}
)

# Callbacks pour charger et filtrer les données
@callback(
    [
        Output('event-type-filter', 'options'),
        Output('event-type-filter', 'value'),
        Output('region-filter', 'options'),
        Output('region-filter', 'value'),
        Output('kpi-container', 'children'),
    ],
    Input('interval', 'n_intervals')
)
def update_filters(n):
    df = load_data()
    if df.empty:
        return [], [], [], [], []
    
    event_types = sorted(df['event_type'].unique())
    regions = sorted(df['region'].unique())
    
    # KPIs
    total_events = len(df)
    avg_severity = df['severity_score'].mean()
    regions_count = df['region'].nunique()
    types_count = df['event_type'].nunique()
    
    kpi_items = [
        create_kpi_card(f"📊 {total_events:,}", "Total Events", colors['accent']),
        create_kpi_card(f"⚠️ {avg_severity:.2f}", "Avg Severity", colors['warning']),
        create_kpi_card(f"🌍 {regions_count}", "Regions", colors['success']),
        create_kpi_card(f"🎯 {types_count}", "Types", colors['danger']),
    ]
    
    return event_types, event_types, regions, regions, kpi_items

def create_kpi_card(value, label, color):
    return html.Div(
        [
            html.Div(value, style={'fontSize': 28, 'fontWeight': 700, 'color': color}),
            html.Div(label, style={'fontSize': 12, 'color': colors['text'], 'opacity': 0.7, 'marginTop': 8}),
        ],
        style={
            'background': colors['card'],
            'padding': '20px',
            'borderRadius': 8,
            'border': f'2px solid {color}40',
            'borderLeft': f'4px solid {color}',
        }
    )

# Graphiques
@callback(
    [
        Output('world-map', 'figure'),
        Output('severity-dist', 'figure'),
        Output('heatmap-region-type', 'figure'),
        Output('timeline-by-region', 'figure'),
        Output('scatter-magnitude', 'figure'),
        Output('box-severity', 'figure'),
        Output('sunburst-chart', 'figure'),
        Output('top-regions-bar', 'figure'),
    ],
    [
        Input('event-type-filter', 'value'),
        Input('region-filter', 'value'),
        Input('interval', 'n_intervals'),
    ]
)
def update_graphs(selected_types, selected_regions, n):
    df = load_data()
    if df.empty:
        return [{}, {}, {}, {}, {}, {}, {}, {}]
    
    # Filtrer
    if selected_types:
        df = df[df['event_type'].isin(selected_types)]
    if selected_regions:
        df = df[df['region'].isin(selected_regions)]
    
    # 1. World Map
    fig_map = go.Figure(data=go.Scattergeo(
        lon=df['longitude'],
        lat=df['latitude'],
        mode='markers',
        marker=dict(
            size=df['severity_score']*15,
            color=df['severity_score'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Severity", thickness=15, len=0.5),
            line=dict(width=0.5, color='white')
        ),
        text=df['title'],
        hovertemplate='<b>%{text}</b><br>Lat: %{lat:.2f}<br>Lon: %{lon:.2f}<extra></extra>',
    ))
    fig_map.update_layout(
        title='🗺️ Global Disaster Distribution',
        geo=dict(projection_type='natural earth', bgcolor=colors['bg']),
        template=plotly_template,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    # 2. Severity Distribution Pie
    severity_counts = df['severity_category'].value_counts()
    fig_severity = go.Figure(data=[go.Pie(
        labels=severity_counts.index,
        values=severity_counts.values,
        marker=dict(colors=[colors['danger'], colors['warning'], colors['accent']])
    )])
    fig_severity.update_layout(
        title='🎚️ Severity Levels',
        template=plotly_template,
        height=400,
    )
    
    # 3. Heatmap Region x Type
    heatmap_data = df.groupby(['region', 'event_type']).size().unstack(fill_value=0)
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd',
    ))
    fig_heatmap.update_layout(
        title='🔥 Heatmap: Regions vs Event Types',
        template=plotly_template,
        height=400,
    )
    
    # 4. Timeline par région
    timeline_data = df.groupby([pd.Grouper(key='start_date', freq='D'), 'region']).size().reset_index(name='count')
    fig_timeline = px.line(
        timeline_data,
        x='start_date',
        y='count',
        color='region',
        title='📈 Events Timeline by Region',
        template=plotly_template,
        height=300,
    )
    fig_timeline.update_layout(hovermode='x unified')
    
    # 5. Scatter Lat/Lon colored by Severity
    fig_scatter = px.scatter(
        df,
        x='latitude',
        y='longitude',
        color='severity_score',
        size='geometry_count',
        hover_name='title',
        hover_data={'event_type': True, 'region': True},
        color_continuous_scale='Reds',
        title='🎯 Lat/Lon Distribution colored by Severity',
        template=plotly_template,
        height=300,
    )
    
    # 6. Box plot Severity par Type
    fig_box = px.box(
        df,
        x='event_type',
        y='severity_score',
        color='event_type',
        title='📊 Severity Distribution by Event Type',
        template=plotly_template,
        height=300,
    )
    
    # 7. Sunburst Chart - Hierarchical view
    try:
        fig_sunburst = px.sunburst(
            df,
            path=['region', 'event_type', 'severity_category'],
            title='☀️ Hierarchical: Region → Type → Severity',
            template=plotly_template,
            height=400,
        )
    except:
        # Fallback if sunburst fails
        fig_sunburst = go.Figure()
        fig_sunburst.add_trace(go.Pie(
            labels=['Error'],
            values=[1],
        ))
        fig_sunburst.update_layout(title='Sunburst Error')
    
    # 8. Top Regions Bar (horizontal)
    top_regions = df['region'].value_counts().head(10)
    fig_bar = go.Figure(data=[go.Bar(
        y=top_regions.index,
        x=top_regions.values,
        orientation='h',
        marker=dict(color=top_regions.values, colorscale='Blues'),
    )])
    fig_bar.update_layout(
        title='🏆 Top 10 Regions by Events',
        template=plotly_template,
        height=300,
        xaxis_title='Count',
        yaxis_title='',
    )
    
    return fig_map, fig_severity, fig_heatmap, fig_timeline, fig_scatter, fig_box, fig_sunburst, fig_bar

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)
