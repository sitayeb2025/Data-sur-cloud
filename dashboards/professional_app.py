"""
=============================================================================
DASHBOARD PROFESSIONNEL - NASA EONET EVENTS MONITOR
Entreprise: École Multimédia | Version: 2.0 | Date: 2026-04-12
=============================================================================
Dashboard interactif for visualisation et monitoring des événements naturels
"""

import dash
from dash import dcc, html, Input, Output, callback, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION ET THEMES
# ============================================================================

# Palette professionnelle moderne
THEME = {
    'bg_primary': '#0f1419',      # Fond principal sombre
    'bg_secondary': '#1a1f26',    # Fond secondaire
    'bg_tertiary': '#252b34',     # Fond tertiaire
    'text_primary': '#e4e6eb',    # Texte principal clair
    'text_secondary': '#a0a3a8',  # Texte secondaire
    'text_muted': '#7a7d82',      # Texte affaibli
    
    # Couleurs d'accent
    'accent_primary': '#0084f4',   # Bleu
    'accent_success': '#31a24c',   # Vert
    'accent_warning': '#ffa500',   # Orange
    'accent_danger': '#f44236',    # Rouge
    'accent_info': '#29b6f6',      # Cyan
    
    # Dégradés
    'gradient_primary': 'linear-gradient(135deg, #0084f4 0%, #29b6f6 100%)',
}

# Initialisation Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ]
)

app.title = "NASA EONET Monitor - Professional Dashboard"

# CSS personnalisé global
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            html, body {
                height: 100%;
                width: 100%;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background-color: ''' + THEME['bg_primary'] + ''';
                color: ''' + THEME['text_primary'] + ''';
                line-height: 1.6;
                overflow-x: hidden;
            }
            
            #react-entry-point {
                min-height: 100vh;
            }
            
            /* Navigation et Header */
            .navbar {
                background: ''' + THEME['bg_secondary'] + ''';
                border-bottom: 1px solid ''' + THEME['bg_tertiary'] + ''';
                padding: 16px 32px;
                position: sticky;
                top: 0;
                z-index: 100;
                backdrop-filter: blur(10px);
            }
            
            .navbar-brand {
                font-size: 24px;
                font-weight: 700;
                background: ''' + THEME['gradient_primary'] + ''';
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .navbar-subtitle {
                font-size: 12px;
                color: ''' + THEME['text_muted'] + ''';
                margin-top: 4px;
                font-weight: 500;
            }
            
            /* Container */
            .dashboard-container {
                max-width: 1800px;
                margin: 0 auto;
                padding: 32px 16px;
            }
            
            /* Grid Layout */
            .grid {
                display: grid;
                gap: 16px;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            }
            
            .grid-2col {
                grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            }
            
            .grid-full {
                grid-column: 1 / -1;
            }
            
            /* Card Styles */
            .card {
                background: ''' + THEME['bg_secondary'] + ''';
                border: 1px solid ''' + THEME['bg_tertiary'] + ''';
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(0, 132, 244, 0.1),
                    transparent
                );
                transition: left 0.5s;
            }
            
            .card:hover {
                border-color: ''' + THEME['accent_primary'] + ''';
                box-shadow: 0 8px 32px rgba(0, 132, 244, 0.15);
                transform: translateY(-4px);
            }
            
            .card:hover::before {
                left: 100%;
            }
            
            /* KPI Card */
            .kpi-card {
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                min-height: 160px;
                padding: 24px;
                border-left: 4px solid ''' + THEME['accent_primary'] + ''';
            }
            
            .kpi-icon {
                font-size: 28px;
                margin-bottom: 8px;
                opacity: 0.9;
            }
            
            .kpi-label {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: ''' + THEME['text_muted'] + ''';
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .kpi-value {
                font-size: 36px;
                font-weight: 700;
                color: ''' + THEME['accent_primary'] + ''';
                line-height: 1;
                margin-bottom: 4px;
            }
            
            .kpi-unit {
                font-size: 11px;
                color: ''' + THEME['text_secondary'] + ''';
                font-weight: 500;
            }
            
            .kpi-card.success {
                border-left-color: ''' + THEME['accent_success'] + ''';
            }
            
            .kpi-card.success .kpi-value {
                color: ''' + THEME['accent_success'] + ''';
            }
            
            .kpi-card.warning {
                border-left-color: ''' + THEME['accent_warning'] + ''';
            }
            
            .kpi-card.warning .kpi-value {
                color: ''' + THEME['accent_warning'] + ''';
            }
            
            .kpi-card.danger {
                border-left-color: ''' + THEME['accent_danger'] + ''';
            }
            
            .kpi-card.danger .kpi-value {
                color: ''' + THEME['accent_danger'] + ''';
            }
            
            /* Chart Container */
            .chart-container {
                min-height: 400px;
            }
            
            /* Table Styles */
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }
            
            th {
                background-color: ''' + THEME['bg_tertiary'] + ''';
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: ''' + THEME['text_secondary'] + ''';
                border-bottom: 2px solid ''' + THEME['bg_tertiary'] + ''';
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 11px;
            }
            
            td {
                padding: 12px;
                border-bottom: 1px solid ''' + THEME['bg_tertiary'] + ''';
            }
            
            tr:hover {
                background-color: rgba(0, 132, 244, 0.05);
            }
            
            /* Status Badge */
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.4px;
            }
            
            .badge-success {
                background-color: rgba(49, 162, 76, 0.2);
                color: ''' + THEME['accent_success'] + ''';
            }
            
            .badge-warning {
                background-color: rgba(255, 165, 0, 0.2);
                color: ''' + THEME['accent_warning'] + ''';
            }
            
            .badge-danger {
                background-color: rgba(244, 66, 54, 0.2);
                color: ''' + THEME['accent_danger'] + ''';
            }
            
            /* Filter Section */
            .filter-section {
                background: ''' + THEME['bg_secondary'] + ''';
                border: 1px solid ''' + THEME['bg_tertiary'] + ''';
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .filter-section-title {
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.6px;
                color: ''' + THEME['text_secondary'] + ''';
                margin-bottom: 16px;
            }
            
            /* Responsive */
            @media (max-width: 1024px) {
                .grid-2col {
                    grid-template-columns: 1fr;
                }
            }
            
            @media (max-width: 768px) {
                .dashboard-container {
                    padding: 16px;
                }
                
                .card {
                    padding: 16px;
                }
                
                .kpi-value {
                    font-size: 28px;
                }
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

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def load_data():
    """Charge les données les plus récentes depuis le dossier processed"""
    try:
        data_dir = Path("data/processed")
        if not data_dir.exists():
            logger.warning("Dossier data/processed non trouvé")
            return pd.DataFrame()
        
        parquet_files = list(data_dir.glob("events_processed_*.parquet"))
        if not parquet_files:
            logger.warning("Aucun fichier Parquet trouvé")
            return pd.DataFrame()
        
        latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"✓ Chargement: {latest_file.name}")
        
        df = pd.read_parquet(latest_file)
        
        # Conversion des dates
        for col in ['start_date', 'last_update', 'collection_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        logger.error(f"✗ Erreur lors du chargement des données: {e}")
        return pd.DataFrame()


def get_event_type_color(event_type):
    """Retourne une couleur en fonction du type d'événement"""
    colors = {
        'Wildfires': THEME['accent_danger'],
        'Earthquakes': THEME['accent_warning'],
        'Volcanic Activity': THEME['accent_warning'],
        'Severe Storms': THEME['accent_primary'],
        'Floods': THEME['accent_info'],
        'Other': THEME['text_muted']
    }
    return colors.get(event_type, THEME['accent_primary'])


def create_kpi_card(label, value, unit="", icon="📊", color_class=""):
    """Crée une carte KPI professionnelle"""
    return html.Div([
        html.Div(icon, style={'fontSize': '32px', 'marginBottom': '8px'}),
        html.Div(label, className='kpi-label'),
        html.Div(str(value), className='kpi-value'),
        html.Div(unit, className='kpi-unit')
    ], className=f"card kpi-card {color_class}")


# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Auto-refresh toutes les 5 secondes
    dcc.Interval(id='refresh-interval', interval=5*1000, n_intervals=0),
    
    # === NAVBAR ===
    html.Div([
        html.Div([
            html.Div([
                html.Div("🌍", style={'fontSize': '28px'}),
                html.Div([
                    html.Div("NASA EONET Monitor", style={'fontWeight': '700', 'fontSize': '20px'}),
                    html.Div("Real-time Natural Disasters Tracking", className='navbar-subtitle')
                ])
            ], className='navbar-brand'),
            html.Div([
                html.Div("Last Update: ", style={'display': 'inline', 'fontSize': '12px', 'color': THEME['text_muted']}),
                html.Div(id='last-update-display', style={'display': 'inline', 'color': THEME['accent_primary'], 'fontWeight': '600'})
            ], style={'marginLeft': 'auto', 'display': 'flex', 'alignItems': 'center', 'gap': '8px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'maxWidth': '1800px', 'margin': '0 auto'})
    ], className='navbar'),
    
    # === MAIN CONTENT ===
    html.Div([
        # === FILTERS ===
        html.Div([
            html.Div("🔍 FILTERS & SETTINGS", className='filter-section-title'),
            html.Div([
                html.Div([
                    html.Label("Event Type:", style={'fontWeight': '600', 'marginBottom': '4px'}),
                    dcc.Dropdown(
                        id='event-type-filter',
                        options=[{'label': 'All Events', 'value': 'all'}],
                        value='all',
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'marginRight': '16px'}),
                html.Div([
                    html.Label("Severity:", style={'fontWeight': '600', 'marginBottom': '4px'}),
                    dcc.Dropdown(
                        id='severity-filter',
                        options=[
                            {'label': 'All Levels', 'value': 'all'},
                            {'label': 'High', 'value': 'high'},
                            {'label': 'Medium', 'value': 'medium'},
                            {'label': 'Low', 'value': 'low'}
                        ],
                        value='all',
                        style={'width': '100%'}
                    )
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'gap': '16px'})
        ], className='filter-section'),
        
        # === KPI CARDS ===
        html.Div(id='kpi-container', className='grid', style={'marginBottom': '32px'}),
        
        # === CHARTS SECTION ===
        html.Div([
            # Row 1: Map et Distribution
            html.Div([
                html.Div([
                    dcc.Graph(id='map-chart', style={'height': '500px'})
                ], className='card grid-item'),
                html.Div([
                    dcc.Graph(id='events-type-chart', style={'height': '500px'})
                ], className='card grid-item')
            ], className='grid grid-2col', style={'marginBottom': '16px'}),
            
            # Row 2: Timeline et Sévérité
            html.Div([
                html.Div([
                    dcc.Graph(id='timeline-chart', style={'height': '400px'})
                ], className='card'),
                html.Div([
                    dcc.Graph(id='severity-chart', style={'height': '400px'})
                ], className='card')
            ], className='grid grid-2col', style={'marginBottom': '16px'}),
            
            # Row 3: Top Events Table
            html.Div([
                html.Div([
                    html.H3("📋 Recent Events", style={'marginBottom': '16px', 'fontSize': '16px', 'fontWeight': '600'}),
                    html.Div(id='events-table-container', style={'overflowX': 'auto'})
                ], className='card grid-full')
            ], className='grid')
        ], style={'marginBottom': '32px'})
    ], className='dashboard-container')
], style={
    'backgroundColor': THEME['bg_primary'],
    'minHeight': '100vh',
    'fontFamily': "'Inter', sans-serif"
})


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    [Output('kpi-container', 'children'),
     Output('last-update-display', 'children')],
    Input('refresh-interval', 'n_intervals')
)
def update_kpis(n):
    """Met à jour les KPI cards"""
    df = load_data()
    
    if df.empty:
        empty_kpis = [create_kpi_card(f"Loading... {n}", "-", "", "⏳") for _ in range(4)]
        return empty_kpis, "No data"
    
    # Calculs
    total = len(df)
    active = len(df[df['status'] == 'open']) if 'status' in df.columns else 0
    avg_severity = df['severity_score'].mean() if 'severity_score' in df.columns else 0
    regions = df['region'].nunique() if 'region' in df.columns else 0
    last_update = df['collection_date'].max() if 'collection_date' in df.columns else datetime.now()
    
    if pd.isna(last_update):
        last_update = datetime.now()
    
    update_time = last_update.strftime('%H:%M:%S') if isinstance(last_update, pd.Timestamp) else 'N/A'
    
    kpis = [
        create_kpi_card("Total Events", total, "", "📊", ""),
        create_kpi_card("Active Now", active, "events", "🔴", "warning"),
        create_kpi_card("Avg Severity", f"{avg_severity:.2f}", "/1.00", "⚠️", "danger"),
        create_kpi_card("Regions", regions, "covered", "🗺️", "success")
    ]
    
    return kpis, update_time


@callback(
    Output('event-type-filter', 'options'),
    Input('refresh-interval', 'n_intervals')
)
def update_filters(n):
    """Met à jour les optionsdu filtre"""
    df = load_data()
    
    if df.empty:
        return [{'label': 'All Events', 'value': 'all'}]
    
    event_types = df['event_type'].unique()
    options = [{'label': 'All Events', 'value': 'all'}]
    options.extend([{'label': et, 'value': et} for et in sorted(event_types)])
    
    return options


@callback(
    Output('map-chart', 'figure'),
    [Input('refresh-interval', 'n_intervals'),
     Input('event-type-filter', 'value'),
     Input('severity-filter', 'value')]
)
def update_map(n, event_type, severity):
    """Carte géographique interactive"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Filtrage
    if event_type != 'all':
        df = df[df['event_type'] == event_type]
    
    try:
        fig = px.scatter_geo(
            df,
            lat='latitude',
            lon='longitude',
            hover_name='title',
            hover_data={
                'event_type': True,
                'severity_score': ':.2f'
            },
            color='severity_score',
            color_continuous_scale='Reds',
            title='🌎 Global Events Distribution'
        )
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor=THEME['bg_secondary'],
            plot_bgcolor=THEME['bg_tertiary'],
            font=dict(family='Inter', color=THEME['text_primary']),
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_colorbar=dict(
                title="Severity"
            )
        )
        
    except Exception as e:
        logger.error(f"Map error: {e}")
        fig = go.Figure().add_annotation(text=f"Error: {str(e)[:50]}")
    
    return fig


@callback(
    Output('events-type-chart', 'figure'),
    [Input('refresh-interval', 'n_intervals'),
     Input('severity-filter', 'value')]
)
def update_events_type(n, severity):
    """Distribution des types d'événements"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig
    
    event_counts = df['event_type'].value_counts().head(10)
    
    colors_list = [get_event_type_color(et) for et in event_counts.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=event_counts.index,
            y=event_counts.values,
            marker=dict(color=colors_list, line=dict(color=THEME['text_muted'], width=1)),
            hovertemplate='<b>%{x}</b><br>Events: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='🎯 Events by Type (Top 10)',
        xaxis_title='Event Type',
        yaxis_title='Count',
        template='plotly_dark',
        paper_bgcolor=THEME['bg_secondary'],
        plot_bgcolor=THEME['bg_tertiary'],
        font=dict(family='Inter', color=THEME['text_primary']),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig


@callback(
    Output('timeline-chart', 'figure'),
    Input('refresh-interval', 'n_intervals')
)
def update_timeline(n):
    """Timeline des événements"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig
    
    df_sorted = df.sort_values('collection_date', na_position='last').dropna(subset=['severity_score'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted['collection_date'],
        y=df_sorted['severity_score'],
        mode='lines+markers',
        name='Severity Score',
        line=dict(color=THEME['accent_danger'], width=3),
        marker=dict(size=8, color=THEME['accent_danger']),
        fill='tozeroy',
        fillcolor='rgba(244, 66, 54, 0.2)',
        hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Severity: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='📈 Severity Timeline',
        xaxis_title='Collection Date',
        yaxis_title='Severity Score',
        template='plotly_dark',
        paper_bgcolor=THEME['bg_secondary'],
        plot_bgcolor=THEME['bg_tertiary'],
        font=dict(family='Inter', color=THEME['text_primary']),
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode='x unified'
    )
    
    return fig


@callback(
    Output('severity-chart', 'figure'),
    Input('refresh-interval', 'n_intervals')
)
def update_severity(n):
    """Distribution de sévérité"""
    df = load_data()
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig
    
    # Créer des bins de sévérité
    severity_bins = pd.cut(df['severity_score'].dropna(), bins=[0, 0.33, 0.66, 1.0],
                           labels=['Low', 'Medium', 'High'], include_lowest=True)
    severity_counts = severity_bins.value_counts()
    
    colors_severity = {
        'Low': THEME['accent_success'],
        'Medium': THEME['accent_warning'],
        'High': THEME['accent_danger']
    }
    
    fig = go.Figure(data=[
        go.Pie(
            labels=severity_counts.index,
            values=severity_counts.values,
            marker=dict(
                colors=[colors_severity.get(s, THEME['accent_primary']) for s in severity_counts.index],
                line=dict(color=THEME['bg_secondary'], width=3)
            ),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='⚖️ Severity Distribution',
        template='plotly_dark',
        paper_bgcolor=THEME['bg_secondary'],
        font=dict(family='Inter', color=THEME['text_primary']),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True
    )
    
    return fig


@callback(
    Output('events-table-container', 'children'),
    Input('refresh-interval', 'n_intervals')
)
def update_events_table(n):
    """Tableau des événements récents"""
    df = load_data()
    
    if df.empty:
        return html.Div("No events available", style={'textAlign': 'center', 'padding': '20px', 'color': THEME['text_muted']})
    
    # Trier par date de collection décroissante
    df_sorted = df.sort_values('collection_date', na_position='last', ascending=False).head(10)
    
    # Créer les lignes du tableau
    rows = []
    for idx, row in df_sorted.iterrows():
        severity = row.get('severity_score', 0)
        if pd.isna(severity):
            severity_class = 'info'
            severity_text = 'Unknown'
        elif severity < 0.33:
            severity_class = 'success'
            severity_text = 'Low'
        elif severity < 0.66:
            severity_class = 'warning'
            severity_text = 'Medium'
        else:
            severity_class = 'danger'
            severity_text = 'High'
        
        rows.append(html.Tr([
            html.Td(row.get('title', 'N/A')[:30], style={'fontWeight': '500'}),
            html.Td(row.get('event_type', 'Unknown')),
            html.Td(html.Span(severity_text, className=f'badge badge-{severity_class}')),
            html.Td(f"{severity:.2f}" if not pd.isna(severity) else "N/A"),
            html.Td(row.get('collection_date').strftime('%Y-%m-%d %H:%M') if pd.notna(row.get('collection_date')) else 'N/A')
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Event Name'),
            html.Th('Type'),
            html.Th('Severity Level'),
            html.Th('Score'),
            html.Th('Date')
        ])),
        html.Tbody(rows)
    ])


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("🚀 LAUNCHING PROFESSIONAL NASA EONET DASHBOARD")
    logger.info(f"   URL: http://localhost:8050")
    logger.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        dev_tools_ui=False,
        dev_tools_props_check=False
    )
