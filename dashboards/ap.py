# =========================================================
# 🌍 CIVIL PROTECTION DASHBOARD
# =========================================================
# Dashboard temps réel pour :
# - surveillance des catastrophes
# - aide à la décision
# - suivi des zones critiques
# - monitoring opérationnel
#
# Technologies :
# - Dash
# - Plotly
# - Pandas
#
# =========================================================

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, Input, Output
from pathlib import Path

# =========================================================
# 🎨 THEME COLORS
# =========================================================

C = {
    "bg": "#0b1220",
    "card": "#111a2e",
    "text": "#e5e7eb",

    "blue": "#3b82f6",
    "green": "#10b981",
    "orange": "#f59e0b",
    "red": "#ef4444"
}

# =========================================================
# 📂 LOAD DATA
# =========================================================

def load_data():
    """
    Charge automatiquement le dernier fichier parquet.
    """

    path = Path("data/processed")

    files = list(path.glob("events_processed_*.parquet"))

    if not files:
        return pd.DataFrame()

    latest = max(files, key=lambda x: x.stat().st_mtime)

    df = pd.read_parquet(latest)

    # Conversion date si présente
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df


# =========================================================
# 🚀 INIT APP
# =========================================================

app = dash.Dash(__name__)

# =========================================================
# 🧱 LAYOUT
# =========================================================

app.layout = html.Div(

    style={
        "backgroundColor": C["bg"],
        "minHeight": "100vh",
        "padding": "20px",
        "fontFamily": "Arial"
    },

    children=[

        # =================================================
        # TITLE
        # =================================================

        html.H1(
            "🚨 CIVIL PROTECTION MONITORING SYSTEM",
            style={
                "color": C["text"],
                "textAlign": "center",
                "marginBottom": "20px"
            }
        ),

        # =================================================
        # KPI CARDS
        # =================================================

        html.Div(
            id="kpis",

            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "15px",
                "marginBottom": "20px"
            }
        ),

        # =================================================
        # ALERT LEVEL
        # =================================================

        dcc.Graph(id="alert_gauge"),

        # =================================================
        # ROW 1
        # =================================================

        html.Div(

            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "15px"
            },

            children=[

                dcc.Graph(id="timeline"),

                dcc.Graph(id="severity_distribution")
            ]
        ),

        # =================================================
        # ROW 2
        # =================================================

        html.Div(

            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "15px",
                "marginTop": "15px"
            },

            children=[

                dcc.Graph(id="danger_types"),

                dcc.Graph(id="priority_chart")
            ]
        ),

        # =================================================
        # MAP
        # =================================================

        html.Div(

            style={"marginTop": "15px"},

            children=[
                dcc.Graph(id="world_map")
            ]
        ),

        # =================================================
        # AUTO REFRESH
        # =================================================

        dcc.Interval(
            id="interval",
            interval=5000,
            n_intervals=0
        )
    ]
)

# =========================================================
# 📊 KPI CARDS
# =========================================================

@app.callback(
    Output("kpis", "children"),
    Input("interval", "n_intervals")
)
def update_kpis(n):

    df = load_data()

    if df.empty:
        return [html.Div("No data")]

    total_events = len(df)

    event_types = (
        df["event_type"].nunique()
        if "event_type" in df.columns else 0
    )

    regions = (
        df["region"].nunique()
        if "region" in df.columns else 0
    )

    avg_severity = (
        df["severity_score"].mean()
        if "severity_score" in df.columns else 0
    )

    def card(title, value, color):

        return html.Div(

            style={
                "background": C["card"],
                "padding": "20px",
                "borderRadius": "12px",
                "border": f"1px solid {color}",
                "textAlign": "center"
            },

            children=[

                html.Div(
                    title,
                    style={
                        "color": C["text"],
                        "fontSize": "14px"
                    }
                ),

                html.Div(
                    str(value),
                    style={
                        "fontSize": "30px",
                        "fontWeight": "bold",
                        "color": color
                    }
                )
            ]
        )

    return [

        card("TOTAL EVENTS", total_events, C["blue"]),

        card("EVENT TYPES", event_types, C["green"]),

        card("AVERAGE SEVERITY", round(avg_severity, 2), C["orange"]),

        card("REGIONS", regions, C["red"])
    ]


# =========================================================
# 🚨 GLOBAL ALERT LEVEL
# =========================================================

@app.callback(
    Output("alert_gauge", "figure"),
    Input("interval", "n_intervals")
)
def alert_gauge(n):

    df = load_data()

    if df.empty or "severity_score" not in df.columns:
        return go.Figure()

    avg = df["severity_score"].mean()

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=avg,

        title={'text': "🚨 GLOBAL ALERT LEVEL"},

        gauge={

            'axis': {'range': [0, 10]},

            'bar': {'color': "#ef4444"},

            'steps': [

                {'range': [0, 3], 'color': "#10b981"},

                {'range': [3, 6], 'color': "#f59e0b"},

                {'range': [6, 10], 'color': "#dc2626"}
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig


# =========================================================
# 📈 TIMELINE
# =========================================================

@app.callback(
    Output("timeline", "figure"),
    Input("interval", "n_intervals")
)
def timeline(n):

    df = load_data()

    if df.empty or "date" not in df.columns:
        return go.Figure()

    ts = (
        df.groupby(df["date"].dt.date)
        .size()
        .reset_index(name="events")
    )

    fig = px.line(
        ts,
        x="date",
        y="events",
        title="📈 Disaster Evolution Over Time",
        template="plotly_dark"
    )

    fig.update_traces(
        line=dict(
            color=C["blue"],
            width=4
        )
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig


# =========================================================
# ⚠️ SEVERITY DISTRIBUTION
# =========================================================

@app.callback(
    Output("severity_distribution", "figure"),
    Input("interval", "n_intervals")
)
def severity_distribution(n):

    df = load_data()

    if df.empty or "severity_score" not in df.columns:
        return go.Figure()

    fig = px.histogram(

        df,

        x="severity_score",

        nbins=20,

        title="⚠️ Severity Distribution",

        template="plotly_dark",

        color_discrete_sequence=[C["orange"]]
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig


# =========================================================
# 🌪️ MOST DANGEROUS TYPES
# =========================================================

@app.callback(
    Output("danger_types", "figure"),
    Input("interval", "n_intervals")
)
def danger_types(n):

    df = load_data()

    required = {"event_type", "severity_score"}

    if df.empty or not required.issubset(df.columns):
        return go.Figure()

    grp = (

        df.groupby("event_type")["severity_score"]

        .mean()

        .sort_values(ascending=False)

        .reset_index()
    )

    fig = px.bar(

        grp,

        x="event_type",

        y="severity_score",

        color="severity_score",

        title="🌪️ Most Dangerous Event Types",

        template="plotly_dark",

        color_continuous_scale="Reds"
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig


# =========================================================
# 🚑 PRIORITY CHART
# =========================================================

@app.callback(
    Output("priority_chart", "figure"),
    Input("interval", "n_intervals")
)
def priority_chart(n):

    df = load_data()

    if df.empty or "severity_score" not in df.columns:
        return go.Figure()

    bins = [0, 3, 6, 10]

    labels = ["LOW", "MEDIUM", "CRITICAL"]

    df["priority"] = pd.cut(
        df["severity_score"],
        bins=bins,
        labels=labels
    )

    counts = (
        df["priority"]
        .value_counts()
        .reset_index()
    )

    fig = px.pie(

        counts,

        names="priority",

        values="count",

        title="🚑 Intervention Priority",

        template="plotly_dark",

        color="priority",

        color_discrete_map={
            "LOW": "#10b981",
            "MEDIUM": "#f59e0b",
            "CRITICAL": "#ef4444"
        }
    )

    fig.update_layout(
        paper_bgcolor=C["bg"],
        font_color=C["text"]
    )

    return fig


# =========================================================
# 🌍 WORLD MAP
# =========================================================

@app.callback(
    Output("world_map", "figure"),
    Input("interval", "n_intervals")
)
def world_map(n):

    df = load_data()

    required = {
        "latitude",
        "longitude",
        "severity_score",
        "event_type"
    }

    if df.empty or not required.issubset(df.columns):
        return go.Figure()

    color_map = {

        "fire": "#ef4444",

        "volcano": "#f59e0b",

        "droplet": "#3b82f6"
    }

    fig = px.scatter_geo(

        df,

        lat="latitude",

        lon="longitude",

        color="event_type",

        size="severity_score",

        projection="natural earth",

        hover_name="event_type",

        title="🌍 Global Catastrophe Live Map",

        template="plotly_dark",

        color_discrete_map=color_map,

        size_max=5
    )

    fig.update_traces(

        marker=dict(

            opacity=0.85,

            line=dict(
                width=1,
                color="white"
            )
        )
    )

    fig.update_layout(

        paper_bgcolor=C["bg"],

        plot_bgcolor=C["bg"],

        font_color=C["text"],

        geo=dict(

            bgcolor=C["bg"],

            landcolor="#1f2937",

            oceancolor="#0f172a",

            showocean=True,

            showcountries=True,

            countrycolor="#374151"
        )
    )

    return fig


# =========================================================
# ▶️ RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )