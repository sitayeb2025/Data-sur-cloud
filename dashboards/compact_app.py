"""
=============================================================================
DASHBOARD COMPACT - 5 GRAPHIQUES ESSENTIELS SEULEMENT
=============================================================================
Dashboard minimaliste et ultra-rapide
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
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
    return df

app = dash.Dash(__name__)

colors = {
    'bg': '#0f1419',
    'card': '#1a1f26',
    'text': '#e4e6eb',
}

app.layout = html.Div([
    html.Div([
        html.H1("⚡ ESSENTIAL DISASTERS VIEW - 5 KEY METRICS", style={'margin': 0, 'fontSize': 24, 'fontWeight': 700}),
    ], style={
        'padding': '16px 24px',
        'background': colors['card'],
        'borderBottom': '2px solid #0084f4'
    }),
    
    html.Div([
        # Top 3 KPIs
        html.Div(id='kpis-row', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(3, 1fr)',
            'gap': '12px',
            'marginBottom': '12px'
        }),
        
        # 2 Main Graphs (50/50)
        html.Div([
            html.Div([dcc.Loading(dcc.Graph(id='g1', config={'responsive': True}))],
                    style={'flex': 1, 'background': colors['card'], 'borderRadius': 6, 'overflow': 'hidden'}),
            html.Div([dcc.Loading(dcc.Graph(id='g2', config={'responsive': True}))],
                    style={'flex': 1, 'background': colors['card'], 'borderRadius': 6, 'overflow': 'hidden'}),
        ], style={'display': 'flex', 'gap': '12px', 'marginBottom': '12px'}),
        
        # 3 Bottom Graphs (33/33/33)
        html.Div([
            html.Div([dcc.Loading(dcc.Graph(id='g3', config={'responsive': True}))],
                    style={'flex': 1, 'background': colors['card'], 'borderRadius': 6, 'overflow': 'hidden'}),
            html.Div([dcc.Loading(dcc.Graph(id='g4', config={'responsive': True}))],
                    style={'flex': 1, 'background': colors['card'], 'borderRadius': 6, 'overflow': 'hidden'}),
            html.Div([dcc.Loading(dcc.Graph(id='g5', config={'responsive': True}))],
                    style={'flex': 1, 'background': colors['card'], 'borderRadius': 6, 'overflow': 'hidden'}),
        ], style={'display': 'flex', 'gap': '12px'}),
    ],
    style={'padding': '12px 24px'}),
    
    dcc.Interval(id='interval', interval=15000, n_intervals=0),
], style={'backgroundColor': colors['bg'], 'minHeight': '100vh'})

@callback(
    [Output('kpis-row', 'children')] + 
    [Output(f'g{i}', 'figure') for i in range(1, 6)],
    Input('interval', 'n_intervals')
)
def update_all(n):
    df = load_data()
    if df.empty:
        return [[], {}, {}, {}, {}, {}]
    
    # KPIs
    kpi_items = [
        create_kpi(f"{len(df):,}", "Total Events", "#0084f4"),
        create_kpi(f"{df['region'].nunique()}", "Regions", "#31a24c"),
        create_kpi(f"{df['event_type'].nunique()}", "Event Types", "#ffa500"),
    ]
    
    # Graph 1: World Map (Large)
    fig1 = go.Figure(data=go.Scattergeo(
        lon=df['longitude'], lat=df['latitude'],
        mode='markers',
        marker=dict(size=4, color=df['severity_score'], colorscale='Reds', showscale=False),
        hovertemplate='<b>%{text}</b><extra></extra>',
        text=df['title'],
    ))
    fig1.update_layout(title='🗺️ Global Map', geo=dict(projection_type='natural earth'),
                       template=plotly_template, height=300, margin=dict(l=0, r=0, t=30, b=0))
    
    # Graph 2: Severity Pie
    fig2 = px.pie(df, names='severity_category', hole=0.4, title='🎚️ Severity Level')
    fig2.update_layout(template=plotly_template, height=300)
    
    # Graph 3: Events by Type (Top 8)
    top_types = df['event_type'].value_counts().head(8)
    fig3 = px.bar(x=top_types.values, y=top_types.index, orientation='h', title='🎯 Events by Type (Top 8)',
                  labels={'x': 'Count', 'y': 'Type'})
    fig3.update_layout(template=plotly_template, height=200, showlegend=False)
    
    # Graph 4: Top Regions
    top_regions = df['region'].value_counts().head(8)
    fig4 = px.bar(x=top_regions.values, y=top_regions.index, orientation='h', title='🌍 Top Regions (Top 8)',
                  labels={'x': 'Count', 'y': 'Region'})
    fig4.update_layout(template=plotly_template, height=200, showlegend=False)
    
    # Graph 5: Timeline (simplified)
    timeline = df.groupby(pd.Grouper(key='start_date', freq='D')).size().reset_index(name='count')
    fig5 = px.area(timeline, x='start_date', y='count', title='📈 Events Timeline',
                   labels={'start_date': 'Date', 'count': 'Count'})
    fig5.update_layout(template=plotly_template, height=200, hovermode='x unified')
    
    return kpi_items, fig1, fig2, fig3, fig4, fig5

def create_kpi(value, label, color):
    return html.Div(
        [
            html.Div(value, style={'fontSize': '20px', 'fontWeight': '700', 'color': color}),
            html.Div(label, style={'fontSize': '11px', 'color': colors['text'], 'opacity': 0.6, 'marginTop': 4}),
        ],
        style={
            'background': colors['card'],
            'padding': '12px 16px',
            'borderRadius': 6,
            'borderLeft': f'3px solid {color}',
        }
    )

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8053)
