# =========================================================
# 🌍 ULTRA PROFESSIONAL CIVIL PROTECTION DASHBOARD
# =========================================================
# VERSION COMPLETE CORRIGÉE
# =========================================================

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html
from dash.dependencies import Input, Output
from pathlib import Path

# =========================================================
# 🎨 COLORS
# =========================================================

C = {

    "bg": "#07101f",

    "panel": "rgba(15,23,42,0.92)",

    "text": "#e5e7eb",

    "red": "#ef4444",

    "orange": "#f59e0b",

    "green": "#10b981",

    "blue": "#3b82f6"
}

# =========================================================
# 🚀 APP
# =========================================================

app = dash.Dash(__name__)

server = app.server

# =========================================================
# 📂 LOAD DATA
# =========================================================

def load_data():

    path = Path("data/processed")

    files = list(path.glob("events_processed_*.parquet"))

    if not files:
        return pd.DataFrame()

    latest = max(files, key=lambda x: x.stat().st_mtime)

    df = pd.read_parquet(latest)

    # =====================================================
    # DETECT DATE COLUMN
    # =====================================================

    possible_dates = [

        "date",
        "event_date",
        "timestamp",
        "created_at",
        "time"
    ]

    for col in possible_dates:

        if col in df.columns:

            df["date"] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

            break

    # =====================================================
    # REMOVE INVALID DATES
    # =====================================================

    if "date" in df.columns:

        df = df.dropna(subset=["date"])

    return df

# =========================================================
# 🎨 PANEL STYLE
# =========================================================

PANEL_STYLE = {

    "background": C["panel"],

    "border": "1px solid rgba(239,68,68,0.2)",

    "borderRadius": "14px",

    "padding": "15px",

    "boxShadow": "0 0 20px rgba(239,68,68,0.08)"
}

# =========================================================
# 🧱 LAYOUT
# =========================================================

app.layout = html.Div(

    style={

        "backgroundColor": C["bg"],

        "backgroundImage": "url('/assets/control_room.jpg')",

        "backgroundSize": "cover",

        "backgroundPosition": "center",

        "backgroundAttachment": "fixed",

        "minHeight": "100vh",

        "padding": "15px",

        "fontFamily": "Arial"
    },

    children=[

        # =================================================
        # TITLE
        # =================================================

        html.Div(

            style={

                "textAlign": "center",

                "marginBottom": "20px"
            },

            children=[

                html.H1(

                    "🌍 SURVEILLANCE DES CATASTROPHES NATURELLES",

                    style={

                        "color": "white",

                        "fontSize": "42px",

                        "fontWeight": "bold",

                        "letterSpacing": "2px",

                        "textShadow": "0 0 20px rgba(255,255,255,0.4)"
                    }
                )
            ]
        ),

        # =================================================
        # FILTERS
        # =================================================

        html.Div(

            style={

                "display": "grid",

                "gridTemplateColumns": "1fr 1fr 1fr 1fr",

                "gap": "15px",

                "marginBottom": "20px"
            },

            children=[

                dcc.Dropdown(
                    id="filter_event",
                    placeholder="🌪️ Event Type",
                    multi=True
                ),

                dcc.Dropdown(
                    id="filter_region",
                    placeholder="🌍 Region",
                    multi=True
                ),

                dcc.RangeSlider(

                    id="filter_severity",

                    min=0,

                    max=1,

                    step=0.1,

                    value=[0,1],

                    marks={
                        0:"0",
                        0.5:"0.5",
                        1:"1"
                    }
                ),

                dcc.DatePickerRange(
                    id="filter_date"
                )
            ]
        ),

        # =================================================
        # MAIN GRID
        # =================================================

        html.Div(

            style={

                "display": "grid",

                "gridTemplateColumns": "320px 1fr 320px",

                "gap": "15px"
            },

            children=[

                # =============================================
                # LEFT PANEL
                # =============================================

                html.Div(

                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "15px"
                    },

                    children=[

                        # LIVE ALERTS

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                html.H2(

                                    "🚨 ALERTES EN COURS",

                                    style={
                                        "color": C["red"]
                                    }
                                ),

                                html.Div(id="live_alerts")
                            ]
                        ),

                        # GLOBAL STATS

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                html.H2(

                                    "📊 STATISTIQUES GLOBALES",

                                    style={
                                        "color": "white"
                                    }
                                ),

                                html.Div(id="global_stats")
                            ]
                        ),

                        # CRITICAL ZONES

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                html.H2(

                                    "🔥 ZONES CRITIQUES",

                                    style={
                                        "color": C["orange"]
                                    }
                                ),

                                html.Div(id="critical_regions")
                            ]
                        )
                    ]
                ),

                # =============================================
                # CENTER PANEL
                # =============================================

                html.Div(

                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "15px"
                    },

                    children=[

                        # WORLD MAP

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                dcc.Graph(
                                    id="world_map",
                                    style={"height": "760px"}
                                )
                            ]
                        ),

                        # BOTTOM GRAPHS
)html.Div(

    style={

        "display": "grid",

        "gridTemplateColumns": "1fr 1fr",

        "gap": "15px"
    },

    children=[

        dcc.Graph(id="regions_chart"),

        dcc.Graph(id="severity_gauge")
    ]
)
                    ]
                ),

                # =============================================
                # RIGHT PANEL
                # =============================================

                html.Div(

                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "15px"
                    },

                    children=[

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                dcc.Graph(id="event_types")
                            ]
                        ),

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                dcc.Graph(id="timeline")
                            ]
                        ),

                        html.Div(

                            style=PANEL_STYLE,

                            children=[

                                html.H3(

                                    "📡 DERNIÈRES ALERTES",

                                    style={
                                        "color": "white"
                                    }
                                ),

                                html.Div(id="latest_alerts")
                            ]
                        )
                    ]
                )
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
# 🔥 FILTER OPTIONS
# =========================================================

@app.callback(

    Output("filter_event", "options"),

    Output("filter_region", "options"),

    Input("interval", "n_intervals")
)
def update_filters(n):

    df = load_data()

    if df.empty:
        return [], []

    events = []

    regions = []

    if "event_type" in df.columns:

        events = [

            {"label": x, "value": x}

            for x in sorted(df["event_type"].dropna().unique())
        ]

    if "region" in df.columns:

        regions = [

            {"label": x, "value": x}

            for x in sorted(df["region"].dropna().unique())
        ]

    return events, regions

# =========================================================
# 🔍 FILTER FUNCTION
# =========================================================

def apply_filters(

    df,

    events,

    regions,

    severity,

    start_date,

    end_date
):

    if df.empty:
        return df

    if events and "event_type" in df.columns:

        df = df[df["event_type"].isin(events)]

    if regions and "region" in df.columns:

        df = df[df["region"].isin(regions)]

    if "severity_score" in df.columns:

        df = df[

            (df["severity_score"] >= severity[0]) &

            (df["severity_score"] <= severity[1])
        ]

    if "date" in df.columns:

        if start_date:

            df = df[df["date"] >= start_date]

        if end_date:

            df = df[df["date"] <= end_date]

    return df

# =========================================================
# 🚨 LIVE ALERTS
# =========================================================

@app.callback(
    Output("live_alerts", "children"),
    Input("interval", "n_intervals")
)
def live_alerts(n):

    df = load_data()

    if df.empty:
        return []

    if "severity_score" not in df.columns:
        return []

    top = df.sort_values(
        "severity_score",
        ascending=False
    ).head(5)

    cards = []

    for _, row in top.iterrows():

        cards.append(

            html.Div(

                style={

                    "background": "#111827",

                    "padding": "12px",

                    "marginBottom": "10px",

                    "borderRadius": "10px",

                    "borderLeft": "5px solid #ef4444"
                },

                children=[

                    html.Div(

                        str(row.get("event_type","UNKNOWN")).upper(),

                        style={

                            "color": "#ef4444",

                            "fontWeight": "bold",

                            "fontSize": "18px"
                        }
                    ),

                    html.Div(

                        f"Severity : {round(row['severity_score'],2)}",

                        style={
                            "color": "white"
                        }
                    ),

                    html.Div(

                        f"Region : {row.get('region','N/A')}",

                        style={
                            "color": "#9ca3af"
                        }
                    )
                ]
            )
        )

    return cards

# =========================================================
# 📊 GLOBAL STATS
# =========================================================

@app.callback(
    Output("global_stats", "children"),
    Input("interval", "n_intervals")
)
def global_stats(n):

    df = load_data()

    if df.empty:
        return []

    total = len(df)

    critical = len(df[df["severity_score"] >= 0.7])

    medium = len(
        df[
            (df["severity_score"] >= 0.4) &
            (df["severity_score"] < 0.7)
        ]
    )

    low = len(df[df["severity_score"] < 0.4])

    stats = [

        ("Total Events", total, C["red"]),

        ("Critical", critical, C["orange"]),

        ("Medium", medium, C["blue"]),

        ("Low", low, C["green"])
    ]

    result = []

    for title, value, color in stats:

        result.append(

            html.Div(

                style={
                    "marginBottom": "15px"
                },

                children=[

                    html.Div(

                        title,

                        style={
                            "color": "white"
                        }
                    ),

                    html.Div(

                        str(value),

                        style={

                            "color": color,

                            "fontSize": "32px",

                            "fontWeight": "bold"
                        }
                    )
                ]
            )
        )

    return result

# =========================================================
# 🔥 CRITICAL REGIONS
# =========================================================

@app.callback(
    Output("critical_regions", "children"),
    Input("interval", "n_intervals")
)
def critical_regions(n):

    df = load_data()

    if df.empty or "region" not in df.columns:
        return []

    critical = df[df["severity_score"] >= 0.7]

    grp = critical["region"].value_counts().head(5)

    result = []

    for region, count in grp.items():

        result.append(

            html.Div(

                style={
                    "marginBottom": "10px"
                },

                children=[

                    html.Div(

                        region,

                        style={
                            "color": "#f59e0b",
                            "fontWeight": "bold"
                        }
                    ),

                    html.Div(

                        f"{count} critical events",

                        style={
                            "color": "white"
                        }
                    )
                ]
            )
        )

    return result

# =========================================================
# 🌍 WORLD MAP
# =========================================================

@app.callback(

    Output("world_map", "figure"),

    Input("interval", "n_intervals"),

    Input("filter_event", "value"),

    Input("filter_region", "value"),

    Input("filter_severity", "value"),

    Input("filter_date", "start_date"),

    Input("filter_date", "end_date")
)
def world_map(

    n,

    events,

    regions,

    severity,

    start_date,

    end_date
):

    df = load_data()

    if df.empty:
        return go.Figure()

    df = apply_filters(

        df,

        events,

        regions,

        severity,

        start_date,

        end_date
    )

    required = {

        "latitude",
        "longitude",
        "severity_score"
    }

    if not required.issubset(df.columns):
        return go.Figure()

    fig = px.scatter_geo(

        df,

        lat="latitude",

        lon="longitude",

        color="event_type",

        size=df["severity_score"] * 0.3,

        hover_name="event_type",

        projection="natural earth",

        template="plotly_dark",

        size_max=8
    )

    fig.update_traces(

        marker=dict(

            opacity=0.75,

            line=dict(
                width=0.5,
                color="white"
            )
        )
    )

    fig.update_geos(

        bgcolor=C["bg"],

        showland=True,

        landcolor="#182235",

        showocean=True,

        oceancolor="#07101f",

        showcountries=True,

        countrycolor="#374151"
    )

    fig.update_layout(

        title="🌍 GLOBAL LIVE DISASTER MAP",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="white",

        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        )
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

        template="plotly_dark",

        title="📈 ÉVOLUTION TEMPORELLE"
    )

    fig.update_traces(

        line=dict(
            color="#ef4444",
            width=4
        )
    )

    fig.update_layout(

        height=320,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="white"
    )

    return fig

# =========================================================
# 🥧 EVENT TYPES
# =========================================================

@app.callback(
    Output("event_types", "figure"),
    Input("interval", "n_intervals")
)
def event_types(n):

    df = load_data()

    if df.empty or "event_type" not in df.columns:
        return go.Figure()

    grp = df["event_type"].value_counts().reset_index()

    grp.columns = ["event_type", "count"]

    fig = px.pie(

        grp,

        names="event_type",

        values="count",

        hole=0.55,

        template="plotly_dark",

        title="📊 TYPES D'ÉVÉNEMENTS"
    )

    fig.update_layout(

        height=320,

        paper_bgcolor="rgba(0,0,0,0)",

        font_color="white"
    )

    return fig

# =========================================================
# 📍 REGIONS CHART
# =========================================================

@app.callback(
    Output("regions_chart", "figure"),
    Input("interval", "n_intervals")
)
def regions_chart(n):

    df = load_data()

    if df.empty or "region" not in df.columns:
        return go.Figure()

    grp = (

        df["region"]

        .value_counts()

        .head(5)

        .reset_index()
    )

    grp.columns = [

        "region",
        "count"
    ]

    fig = px.bar(

        grp,

        x="count",

        y="region",

        orientation="h",

        template="plotly_dark",

        title="📍 RÉGIONS LES PLUS TOUCHÉES"
    )

    fig.update_traces(
        marker_color="#ef4444"
    )

    fig.update_layout(

        height=320,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="white",

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig

# =========================================================
# 🚨 SEVERITY GAUGE
# =========================================================

@app.callback(
    Output("severity_gauge", "figure"),
    Input("interval", "n_intervals")
)
def severity_gauge(n):

    df = load_data()

    if df.empty:
        return go.Figure()

    avg = df["severity_score"].mean() * 10

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=avg,

        title={"text": "🚨 NIVEAU DE SÉVÉRITÉ"},

        gauge={

            "axis": {"range": [0, 10]},

            "bar": {"color": "#ef4444"},

            "steps": [

                {"range": [0, 3], "color": "#10b981"},

                {"range": [3, 6], "color": "#f59e0b"},

                {"range": [6, 10], "color": "#dc2626"}
            ]
        }
    ))

    fig.update_layout(

        height=320,

        paper_bgcolor="rgba(0,0,0,0)",

        font_color="white"
    )

    return fig

# =========================================================
# 🔥 HEATMAP
# =========================================================

@app.callback(
    Output("heatmap", "figure"),
    Input("interval", "n_intervals")
)
def heatmap(n):

    df = load_data()

    if df.empty:
        return go.Figure()

    fig = px.density_mapbox(

        df,

        lat="latitude",

        lon="longitude",

        z="severity_score",

        radius=8,

        zoom=1,

        mapbox_style="carto-darkmatter"
    )

    fig.update_layout(

        height=320,

        paper_bgcolor="rgba(0,0,0,0)",

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

    return fig

# =========================================================
# 📡 LAST ALERTS
# =========================================================

@app.callback(
    Output("latest_alerts", "children"),
    Input("interval", "n_intervals")
)
def latest_alerts(n):

    df = load_data()

    if df.empty:
        return []

    latest = df.tail(5)

    result = []

    for _, row in latest.iterrows():

        result.append(

            html.Div(

                style={
                    "marginBottom": "10px"
                },

                children=[

                    html.Div(

                        str(row.get("event_type","UNKNOWN")),

                        style={
                            "color": "#ef4444",
                            "fontWeight": "bold"
                        }
                    ),

                    html.Div(

                        f"Severity : {round(row.get('severity_score',0),2)}",

                        style={
                            "color": "white"
                        }
                    )
                ]
            )
        )

    return result

# =========================================================
# ▶️ RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050
    )