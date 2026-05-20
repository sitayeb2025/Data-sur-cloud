import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, Input, Output
from pathlib import Path

# ================= DATA =================
def load_data():
    path = Path("data/processed")
    files = list(path.glob("events_processed_*.parquet"))
    if not files:
        return pd.DataFrame()
    df = pd.read_parquet(max(files, key=lambda x: x.stat().st_mtime))
    return df

df = load_data()

# ================= THEME =================
C = {
    "bg": "#0b1220",
    "card": "#111a2e",
    "blue": "#3b82f6",
    "green": "#10b981",
    "orange": "#f59e0b",
    "red": "#ef4444",
    "text": "#e5e7eb"
}

# ================= APP =================
app = dash.Dash(__name__)

app.layout = html.Div(
    style={"backgroundColor": C["bg"], "minHeight": "100vh", "padding": "20px"},
    children=[

        # TITLE
        html.H1("🌍 Global Catastrophe Cost Dashboard",
                style={"color": C["text"], "textAlign": "center"}),

        # KPI CARDS
        html.Div(id="kpis", style={
            "display": "grid",
            "gridTemplateColumns": "repeat(4, 1fr)",
            "gap": "15px",
            "marginTop": "20px"
        }),

        # GRAPHS ROW 1
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "15px"},
                 children=[

            dcc.Graph(id="cost_by_year"),
            dcc.Graph(id="cost_distribution")
        ]),

        # GRAPHS ROW 2
        html.Div(style={"marginTop": "15px"},
                 children=[dcc.Graph(id="world_map")]),

        dcc.Interval(id="interval", interval=5000, n_intervals=0)
    ]
)

# ================= CALLBACK KPIs =================
@app.callback(
    Output("kpis", "children"),
    Input("interval", "n_intervals")
)
def kpis(n):
    df = load_data()
    if df.empty:
        return [html.Div("No data")]

    total = len(df)
    types = df["event_type"].nunique() if "event_type" in df else 0
    regions = df["region"].nunique() if "region" in df else 0
    severity = df["severity_score"].mean() if "severity_score" in df else 0

    def card(title, value, color):
        return html.Div(style={
            "background": C["card"],
            "padding": "15px",
            "borderRadius": "10px",
            "color": C["text"],
            "border": f"1px solid {color}"
        }, children=[
            html.Div(title, style={"fontSize": "12px"}),
            html.Div(value, style={"fontSize": "26px", "fontWeight": "bold", "color": color})
        ])

    return [
        card("TOTAL EVENTS", total, C["blue"]),
        card("EVENT TYPES", types, C["green"]),
        card("SEVERITY AVG", round(severity, 2), C["orange"]),
        card("REGIONS", regions, C["red"]),
    ]

# ================= CHART 1: COST BY TYPE =================
@app.callback(Output("cost_by_year", "figure"),
              Input("interval", "n_intervals"))
def cost_by_year(n):
    df = load_data()
    if df.empty:
        return go.Figure()

    if "event_type" not in df:
        return go.Figure()

    fig = px.histogram(
        df,
        x="event_type",
        color="event_type",
        title="📊 Events Distribution (Insurance Style)",
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig

# ================= CHART 2: SEVERITY =================
@app.callback(Output("cost_distribution", "figure"),
              Input("interval", "n_intervals"))
def severity_dist(n):
    df = load_data()
    if df.empty or "severity_score" not in df:
        return go.Figure()

    fig = px.histogram(
        df,
        x="severity_score",
        nbins=20,
        title="⚠️ Severity Distribution (Damage Level)",
        template="plotly_dark",
        color_discrete_sequence=[C["orange"]]
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig

# ================= CHART 3: WORLD MAP =================
@app.callback(Output("world_map", "figure"),
              Input("interval", "n_intervals"))
def world_map(n):
    df = load_data()
    if df.empty:
        return go.Figure()

    if not {"latitude", "longitude"}.issubset(df.columns):
        return go.Figure()

    # ===== MAP DES TYPES → ICÔNES =====
    icon_map = {
        "fire": "🔥",
        "volcano": "🌋",
        "droplet": "💧"
    }

    color_map = {
        "fire": "#ef4444",
        "volcano": "#f59e0b",
        "droplet": "#3b82f6"
    }

    # fallback si type inconnu
    if "event_type" not in df.columns:
        df["event_type"] = "unknown"

    fig = go.Figure()

    for event_type, group in df.groupby("event_type"):
        icon = icon_map.get(event_type, "⚠️")
        color = color_map.get(event_type, "#9ca3af")

        fig.add_trace(go.Scattergeo(
            lat=group["latitude"],
            lon=group["longitude"],
            mode="markers+text",
            text=[icon] * len(group),
            textposition="middle center",
            marker=dict(
                size=12,
                color=color,
                line=dict(width=0.5, color="white")
            ),
            name=event_type,
            hovertemplate=
                "<b>%{text}</b><br>" +
                "Type: " + event_type + "<br>" +
                "Lat: %{lat}<br>" +
                "Lon: %{lon}<br>" +
                "<extra></extra>"
        ))

    fig.update_layout(
        title="🌍 Global Catastrophe Map",
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"],
        legend_title="Event Types",
        geo=dict(
            showland=True,
            landcolor="#1f2937",
            showcountries=True
        )
    )

    return fig

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)