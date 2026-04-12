"""
Dashboard Professionnel - Visualisation des Événements NASA EONET
Entreprise: École Multimédia
Date: 2026-04-12
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'app Dash
app = dash.Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
])

app.title = "NASA EONET Events Dashboard - Professional"

# Palette professionnelle
COLORS = {
    'background': '#0f1419',
    'surface': '#1a1f26',
    'surface_light': '#252b34',
    'text': '#e4e6eb',
    'text_muted': '#a0a3a8',
    'primary': '#0084f4',
    'primary_light': '#e7f1ff',
    'success': '#31a24c',
    'warning': '#f57c00',
    'danger': '#f44236',
    'info': '#29b6f6'
}

# Supprimez l'ancienne ligne STYLE_SHEET si elle existe

STYLE_SHEET = [
    "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
]



# CSS personnalisé
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: ''' + COLORS['background'] + ''';
                color: ''' + COLORS['text'] + ''';
                line-height: 1.6;
            }
            .container { 
                max-width: 1600px; 
                margin: 0 auto; 
                padding: 0 16px; 
            }
            .gradient-text {
                background: linear-gradient(135deg, ''' + COLORS['primary'] + ''' 0%, ''' + COLORS['info'] + ''' 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .card {
                background: ''' + COLORS['surface'] + ''';
                border: 1px solid ''' + COLORS['surface_light'] + ''';
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            .card:hover {
                border-color: ''' + COLORS['primary'] + ''';
                box-shadow: 0 4px 20px rgba(0, 132, 244, 0.15);
                transform: translateY(-2px);
            }
            .kpi-card {
                padding: 24px;
                border-left: 4px solid ''' + COLORS['primary'] + ''';
            }
            .kpi-value {
                font-size: 32px;
                font-weight: 700;
                margin: 12px 0;
                color: ''' + COLORS['primary'] + ''';
            }
            .kpi-label {
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: ''' + COLORS['text_muted'] + ''';
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer></footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''


def load_data():
    """Charge les données processées les plus récentes"""
    data_dir = Path("data/processed")
    
    if not data_dir.exists():
        logger.warning("Dossier de données non trouvé")
        return pd.DataFrame()
    
    # Récupérer le fichier le plus récent
    parquet_files = list(data_dir.glob("events_processed_*.parquet"))
    
    if not parquet_files:
        logger.warning("Aucun fichier de données trouvé")
        return pd.DataFrame()
    
    latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Chargement: {latest_file}")
    
    try:
        df = pd.read_parquet(latest_file)
        # Conversion des dates
        for col in ['start_date', 'last_update', 'collection_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except Exception as e:
        logger.error(f"Erreur chargement: {e}")
        return pd.DataFrame()


# Chargement des données
df = load_data()



def create_metric_card(title: str, value, color: str, icon: str = "📊"):
    """Crée une carte de métrique"""
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize': '24px', 'marginRight': '10px'}),
            html.Div([
                html.H4(title, style={'margin': '0', 'fontSize': '14px', 'color': '#7f8c8d'}),
                html.H2(str(value), style={'margin': '0', 'color': color, 'fontSize': '28px'})
            ])
        ], style={
            'padding': '15px',
            'backgroundColor': '#fff',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'display': 'flex',
            'alignItems': 'center'
        })
    ], style={'flex': '1', 'marginRight': '15px'})


# Layout de l'application
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    
    # Auto-refresh interval (toutes les 5 secondes)
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # 5 secondes
        n_intervals=0
    ),
    
    # Header
    html.Div([
        html.Div([
            html.H1("🌍 NASA EONET Events Dashboard", style={
                'color': COLORS['text'],
                'marginBottom': '10px',
                'fontFamily': 'Roboto'
            }),
            html.P("Visualisation en temps réel des événements naturels", style={
                'color': '#7f8c8d',
                'fontSize': '16px',
                'margin': '0'
            })
        ], style={'maxWidth': '1400px', 'margin': '0 auto'})
    ], style={
        'backgroundColor': '#fff',
        'padding': '30px 20px',
        'borderBottom': '1px solid #ecf0f1',
        'marginBottom': '30px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
    }),
    
    # Contenu principal
    html.Div([
        html.Div(style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px'}, children=[
            
            # Métriques clés
            html.Div(id='metrics-container', style={'display': 'flex', 'marginBottom': '30px', 'flexWrap': 'wrap', 'gap': '10px'}),
            
            # Graphiques
            html.Div([
                # Première ligne
                html.Div([
                    # Carte géographique
                    html.Div([
                        dcc.Graph(id='map-graph', style={'height': '500px'})
                    ], style={
                        'flex': '1',
                        'marginRight': '15px',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px'
                    }),
                    
                    # Types d'événements
                    html.Div([
                        dcc.Graph(id='events-by-type', style={'height': '500px'})
                    ], style={
                        'flex': '1',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px'
                    })
                ], style={'display': 'flex', 'marginBottom': '15px'}),
                
                # Deuxième ligne
                html.Div([
                    # Timeline
                    html.Div([
                        dcc.Graph(id='timeline-graph', style={'height': '300px'})
                    ], style={
                        'flex': '1',
                        'marginRight': '15px',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px'
                    }),
                    
                    # Sévérité
                    html.Div([
                        dcc.Graph(id='severity-graph', style={'height': '300px'})
                    ], style={
                        'flex': '1',
                        'backgroundColor': '#fff',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px'
                    })
                ], style={'display': 'flex'})
            ])
        ])
    ], style={'paddingBottom': '30px'})
])


# Callbacks pour les graphiques
@app.callback(
    Output('metrics-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    """Mise à jour des métriques KPI"""
    df = load_data()
    
    if df.empty:
        return html.Div("Aucune donnée disponible",style={'padding': '20px'})
    
    total_events = len(df)
    active_events = len(df[df['status'] == 'open']) if 'status' in df.columns else 0
    avg_severity = df['severity_score'].mean() if 'severity_score' in df.columns and not df['severity_score'].isna().all() else 0
    regions = df['region'].nunique() if 'region' in df.columns else 0
    
    return [
        create_metric_card("Total Événements", total_events, COLORS['primary'], "📊"),
        create_metric_card("Événements Actifs", active_events, COLORS['warning'], "🔴"),
        create_metric_card("Sévérité Moyenne", f"{avg_severity:.2f}/1.00" if avg_severity > 0 else "N/A", COLORS['danger'], "⚠️"),
        create_metric_card("Couverture Géo.", f"{regions} régions", COLORS['success'], "🗺️")
    ]


@app.callback(
    Output('map-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_map(_):
    """Crée la carte géographique des événements"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure().add_annotation(text="Loading data...")
        return fig
    
    try:
        fig = px.scatter_geo(
            df,
            lat='latitude',
            lon='longitude',
            hover_name='title',
            hover_data={'event_type': True, 'severity_score': ':.2f'},
            color='severity_score',
            size='geometry_count',
            color_continuous_scale='Reds',
            title='📍 Événements Naturels - Localisation Mondiale'
        )
    except Exception as e:
        logger.error(f"Map error: {e}")
        fig = go.Figure().add_annotation(text="No data available")
    
    fig.update_layout(
        height=500,
        font=dict(family='Roboto'),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


@app.callback(
    Output('events-by-type', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_events_by_type(_):
    """Types d'événements"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure().add_annotation(text="Loading data...")
        return fig
    
    try:
        event_counts = df['event_type'].value_counts().head(10)
        
        fig = px.bar(
            x=event_counts.index,
            y=event_counts.values,
            title='📊 Top 10 Types d\'Événements',
            labels={'x': 'Type', 'y': 'Nombre'},
            color=event_counts.values,
            color_continuous_scale='Blues'
        )
    except Exception as e:
        logger.error(f"Events by type error: {e}")
        fig = go.Figure().add_annotation(text="No data available")
    
    fig.update_layout(
        height=500,
        font=dict(family='Roboto'),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    
    return fig


@app.callback(
    Output('timeline-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_timeline(_):
    """Timeline des événements"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure().add_annotation(text="Loading data...")
        return fig
    
    try:
        df_sorted = df.sort_values('collection_date', na_position='last')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted['collection_date'],
            y=df_sorted['severity_score'],
            mode='lines+markers',
            name='Severity',
            line=dict(color=COLORS['danger'], width=2),
            marker=dict(size=6)
        ))
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        fig = go.Figure().add_annotation(text="No data available")
    
    fig.update_layout(
        title='⏱️ Timeline de Sévérité',
        xaxis_title='Date',
        yaxis_title='Score de Sévérité',
        height=300,
        font=dict(family='Roboto'),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


@app.callback(
    Output('severity-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_severity(_):
    """Distribution de sévérité"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure().add_annotation(text="Loading data...")
        return fig
    
    try:
        if 'severity_category' in df.columns:
            severity_counts = df['severity_category'].value_counts()
        else:
            severity_counts = df['event_type'].value_counts().head(5)
        
        fig = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title='⚠️ Distribution',
            color_discrete_sequence=[COLORS['success'], COLORS['warning'], COLORS['danger']]
        )
    except Exception as e:
        logger.error(f"Severity error: {e}")
        fig = go.Figure().add_annotation(text="No data available")
    
    fig.update_layout(
        height=300,
        font=dict(family='Roboto'),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


if __name__ == '__main__':
    logger.info("🚀 Démarrage du dashboard...")
    app.run_server(debug=True, host='0.0.0.0', port=8050)


if __name__ == '__main__':
    logger.info("🚀 Démarrage du dashboard...")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
