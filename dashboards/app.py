# =========================================================
# 🌍 CIVIL PROTECTION DASHBOARD
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
    "bg":     "#0b1220",
    "card":   "#111a2e",
    "text":   "#e5e7eb",
    "blue":   "#3b82f6",
    "green":  "#10b981",
    "orange": "#f59e0b",
    "red":    "#ef4444"
}

# =========================================================
# 🗺️ EVENT TYPE → style (valeurs réelles du parquet)
# =========================================================

EVENT_STYLE = {
    "wildfires":       {"symbol": "🔥", "color": "#ff4500", "halo": "rgba(255,69,0,0.35)"},
    "severe storms":   {"symbol": "🌀", "color": "#a78bfa", "halo": "rgba(167,139,250,0.35)"},
    "volcanoes":       {"symbol": "🌋", "color": "#ff8c00", "halo": "rgba(255,140,0,0.35)"},
    "earthquakes":     {"symbol": "💥", "color": "#f59e0b", "halo": "rgba(245,158,11,0.35)"},
    "floods":          {"symbol": "🌊", "color": "#1e90ff", "halo": "rgba(30,144,255,0.35)"},
    "landslides":      {"symbol": "⛰️", "color": "#92400e", "halo": "rgba(146,64,14,0.35)"},
    "sea and lake ice":{"symbol": "🧊", "color": "#bfdbfe", "halo": "rgba(191,219,254,0.35)"},
    "default":         {"symbol": "⚠️", "color": "#e5e7eb", "halo": "rgba(229,231,235,0.25)"},
}

def get_style(event_type):
    et = str(event_type).lower().strip() if event_type else "default"
    for key in EVENT_STYLE:
        if key in et:
            return EVENT_STYLE[key]
    return EVENT_STYLE["default"]

# =========================================================
# 📂 LOAD DATA
# =========================================================

def load_data():
    path = Path("data/processed")
    files = list(path.glob("events_enriched_*.parquet"))
    if not files:
        return pd.DataFrame()
    latest = max(files, key=lambda x: x.stat().st_mtime)
    df = pd.read_parquet(latest)
    severity_map = {"high": 0.85, "medium": 0.5, "low": 0.2, "unknown": 0.3}
    if "severity" in df.columns:
        if df["severity"].dtype == object:
            df["severity"] = df["severity"].str.lower().map(severity_map).fillna(0.3)
        df["severity_category"] = pd.cut(
            df["severity"], bins=[0, 0.33, 0.66, 1.0],
            labels=["Low", "Medium", "High"]
        ).astype(str)
    for col in ("start_date", "date", "collection_date"):
        if col in df.columns:
            df["date"] = pd.to_datetime(df[col], utc=True, errors="coerce")
            break
    return df
# =========================================================
# 🚀 INIT APP
# =========================================================

app = dash.Dash(__name__)

# =========================================================
# 🧱 LAYOUT
# =========================================================

app.layout = html.Div(
    style={"backgroundColor": C["bg"], "minHeight": "100vh",
           "padding": "20px", "fontFamily": "Arial"},
    children=[

        # ── TITLE ────────────────────────────────────────
        html.H1(
            "🚨 CIVIL PROTECTION MONITORING SYSTEM",
            style={"color": C["text"], "textAlign": "center", "marginBottom": "20px"}
        ),

        # ── FILTER BAR ───────────────────────────────────
        html.Div(
            style={
                "background": C["card"], "borderRadius": "12px",
                "padding": "20px", "marginBottom": "20px",
                "border": f"1px solid {C['blue']}",
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr 1fr 1fr",
                "gap": "20px", "alignItems": "end"
            },
            children=[

                # Filtre 1 : Type d'événement
                html.Div([
                    html.Label("🌪️ Event Type", style={
                        "color": C["text"], "marginBottom": "8px",
                        "display": "block", "fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="filter_event_type", options=[], multi=True,
                        placeholder="All types...",
                        style={"backgroundColor": "#1e293b", "color": "#000"})
                ]),

                # Filtre 2 : Région
                html.Div([
                    html.Label("🌍 Region", style={
                        "color": C["text"], "marginBottom": "8px",
                        "display": "block", "fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="filter_region", options=[], multi=True,
                        placeholder="All regions...",
                        style={"backgroundColor": "#1e293b", "color": "#000"})
                ]),

                # Filtre 3 : Severity Category
                html.Div([
                    html.Label("🚨 Severity Level", style={
                        "color": C["text"], "marginBottom": "8px",
                        "display": "block", "fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="filter_severity_cat",
                        options=[
                            {"label": "🔴 High",   "value": "High"},
                            {"label": "🟠 Medium", "value": "Medium"},
                            {"label": "🟢 Low",    "value": "Low"},
                        ],
                        multi=True,
                        placeholder="All levels...",
                        style={"backgroundColor": "#1e293b", "color": "#000"})
                ]),

                # Filtre 4 : Score de sévérité (slider 0→1)
                html.Div([
                    html.Div([
                        html.Label("⚠️ Severity Score", style={
                            "color": C["text"],
                            "display": "inline-block", "fontWeight": "bold"}),
                        html.Button("↺ Reset filters", id="btn_reset",
                            n_clicks=0,
                            style={
                                "float": "right",
                                "background": "transparent",
                                "border": f"1px solid {C['blue']}",
                                "color": C["blue"],
                                "borderRadius": "6px",
                                "padding": "2px 10px",
                                "cursor": "pointer",
                                "fontSize": "12px"
                            })
                    ], style={"marginBottom": "8px"}),
                    dcc.RangeSlider(
                        id="filter_severity", min=0, max=1, step=0.05,
                        value=[0, 1],
                        marks={
                            0:    {"label": "0",    "style": {"color": C["text"]}},
                            0.25: {"label": "0.25", "style": {"color": C["text"]}},
                            0.5:  {"label": "0.5",  "style": {"color": C["text"]}},
                            0.75: {"label": "0.75", "style": {"color": C["text"]}},
                            1:    {"label": "1",    "style": {"color": C["text"]}},
                        },
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ]),
            ]
        ),

        # ── KPI CARDS ────────────────────────────────────
        html.Div(
            id="kpis",
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
                   "gap": "15px", "marginBottom": "20px"}
        ),

        # ── 🌍 WORLD MAP EN PREMIER ───────────────────────
        html.Div(
            style={"marginBottom": "20px"},
            children=[dcc.Graph(id="world_map", style={"height": "680px"})]
        ),

        # ── ROW 1 : alert gauge + severity distribution ──
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                   "gap": "15px", "marginTop": "15px"},
            children=[
                dcc.Graph(id="alert_gauge"),
                dcc.Graph(id="severity_distribution")
            ]
        ),

        # ── ROW 2 : danger types + priority ──────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                   "gap": "15px", "marginTop": "15px"},
            children=[
                dcc.Graph(id="danger_types"),
                dcc.Graph(id="priority_chart")
            ]
        ),

        # ── ROW 3 : top regions (remplace graphe vide) ───
        html.Div(
            style={"marginTop": "15px"},
            children=[dcc.Graph(id="top_regions")]
        ),

        # ── AUTO REFRESH ─────────────────────────────────
        dcc.Interval(id="interval", interval=5000, n_intervals=0)
    ]
)

# =========================================================
# 🔄 POPULATE FILTER OPTIONS
# =========================================================

@app.callback(
    Output("filter_event_type", "options"),
    Output("filter_region",     "options"),
    Input("interval", "n_intervals")
)
def populate_filters(n):
    df = load_data()
    if df.empty:
        return [], []
    event_opts = (
        [{"label": t, "value": t} for t in sorted(df["event_type"].dropna().unique())]
        if "event_type" in df.columns else []
    )
    region_opts = (
        [{"label": r, "value": r} for r in sorted(df["region"].dropna().unique())]
        if "region" in df.columns else []
    )
    return event_opts, region_opts

# =========================================================
# ↺ RESET FILTERS
# =========================================================

@app.callback(
    Output("filter_event_type",   "value"),
    Output("filter_region",       "value"),
    Output("filter_severity_cat", "value"),
    Output("filter_severity",     "value"),
    Input("btn_reset", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n):
    return None, None, None, [0, 1]

# =========================================================
# 🔧 HELPER : apply filters
# =========================================================

def apply_filters(df, event_types, regions, severity_cats, severity_range):
    if df.empty:
        return df
    if event_types and "event_type" in df.columns:
        df = df[df["event_type"].isin(event_types)]
    if regions and "region" in df.columns:
        df = df[df["region"].isin(regions)]
    if severity_cats and "severity_category" in df.columns:
        df = df[df["severity_category"].isin(severity_cats)]
    if severity_range and "severity" in df.columns:
        lo, hi = severity_range
        df = df[(df["severity"] >= lo) & (df["severity"] <= hi)]
    return df

# =========================================================
# 📊 KPI CARDS
# =========================================================

@app.callback(
    Output("kpis", "children"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def update_kpis(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)
    if df.empty:
        return [html.Div("No data", style={"color": C["text"]})]

    total        = len(df)
    ev_types_cnt = df["event_type"].nunique()   if "event_type"    in df.columns else 0
    regions_cnt  = df["region"].nunique()        if "region"        in df.columns else 0
    avg_sev      = df["severity"].mean()   if "severity" in df.columns else 0

    def card(title, value, color):
        return html.Div(
            style={"background": C["card"], "padding": "20px", "borderRadius": "12px",
                   "border": f"1px solid {color}", "textAlign": "center"},
            children=[
                html.Div(title, style={"color": C["text"], "fontSize": "14px"}),
                html.Div(str(value), style={"fontSize": "30px", "fontWeight": "bold", "color": color})
            ]
        )

    return [
        card("TOTAL EVENTS",     total,                  C["blue"]),
        card("EVENT TYPES",      ev_types_cnt,           C["green"]),
        card("AVG SEVERITY",     f"{avg_sev:.2f}",       C["orange"]),
        card("REGIONS",          regions_cnt,            C["red"]),
    ]

# =========================================================
# 🚨 GLOBAL ALERT LEVEL  (0→1)
# =========================================================

@app.callback(
    Output("alert_gauge", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def alert_gauge(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)
    if df.empty or "severity" not in df.columns:
        return go.Figure()
    avg = df["severity"].mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(avg, 3),
        number={"valueformat": ".2f"},
        title={"text": "🚨 GLOBAL ALERT LEVEL"},
        gauge={
            "axis":  {"range": [0, 1]},
            "bar":   {"color": "#ef4444"},
            "steps": [
                {"range": [0,    0.33], "color": "#10b981"},
                {"range": [0.33, 0.66], "color": "#f59e0b"},
                {"range": [0.66, 1],    "color": "#dc2626"},
            ]
        }
    ))
    fig.update_layout(paper_bgcolor=C["bg"], font_color=C["text"])
    return fig
# =========================================================
# 🗺️ HEATMAP : TYPE D'ÉVÉNEMENT × RÉGION  (avg severity)
# =========================================================

@app.callback(
    Output("severity_distribution", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def event_region_heatmap(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)

    if df.empty or not {"event_type", "region", "severity"}.issubset(df.columns):
        return go.Figure()

    # Top 10 régions les plus actives pour rester lisible
    top_regions = (
        df.groupby("region")["severity"]
        .count()
        .nlargest(10)
        .index.tolist()
    )
    df_heat = df[df["region"].isin(top_regions)]

    pivot = (
        df_heat.groupby(["event_type", "region"])["severity"]
        .mean()
        .unstack(fill_value=0)
    )

    # Annotations : valeur ou vide si 0
    annotations = []
    for i, etype in enumerate(pivot.index):
        for j, region in enumerate(pivot.columns):
            val = pivot.loc[etype, region]
            annotations.append(dict(
                x=region, y=etype,
                text=f"{val:.2f}" if val > 0 else "",
                showarrow=False,
                font=dict(size=10, color="white")
            ))

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0,  "#071e3d"],
            [0.33, "#1e6091"],
            [0.66, "#f59e0b"],
            [1.0,  "#ef4444"],
        ],
        zmin=0, zmax=1,
        colorbar=dict(
            title="Avg severity",
            tickvals=[0, 0.33, 0.66, 1],
            ticktext=["0", "Low", "Med", "High"],
            tickfont=dict(color=C["text"])
        ),
        hovertemplate=(
            "<b>%{y}</b> in <b>%{x}</b><br>"
            "Avg severity : %{z:.2f}<extra></extra>"
        )
    ))

    fig.update_layout(
        title="🗺️ Event Type × Region — Avg Severity",
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font_color=C["text"],
        annotations=annotations,
        xaxis=dict(tickangle=-35, title=""),
        yaxis=dict(title=""),
        margin=dict(l=120, r=20, t=50, b=100),
    )
    return fig

# =========================================================
# 🌪️ MOST DANGEROUS TYPES
# =========================================================

@app.callback(
    Output("danger_types", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def danger_types(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)
    if df.empty or not {"event_type","severity"}.issubset(df.columns):
        return go.Figure()
    grp = (df.groupby("event_type")["severity"]
             .mean().sort_values(ascending=False).reset_index())
    fig = px.bar(
        grp, x="event_type", y="severity",
        color="severity",
        title="🌪️ Most Dangerous Event Types (avg severity)",
        template="plotly_dark",
        color_continuous_scale="Reds",
        text=grp["severity"].map(lambda v: f"{v:.2f}")
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
                      font_color=C["text"], yaxis_title="Avg Severity Score")
    return fig

# =========================================================
# 🚑 PRIORITY CHART  (severity_category réelle)
# =========================================================

@app.callback(
    Output("priority_chart", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def priority_chart(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)
    if df.empty:
        return go.Figure()
    if "severity_category" in df.columns:
        counts = df["severity_category"].value_counts().reset_index()
        counts.columns = ["priority", "count"]
    else:
        df = df.copy()
        df["priority"] = pd.cut(df["severity"],
                                bins=[0, 0.33, 0.66, 1.0],
                                labels=["Low", "Medium", "High"])
        counts = df["priority"].value_counts().reset_index()
        counts.columns = ["priority", "count"]
    fig = px.pie(
        counts, names="priority", values="count",
        title="🚑 Intervention Priority",
        template="plotly_dark",
        color="priority",
        color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    )
    fig.update_layout(paper_bgcolor=C["bg"], font_color=C["text"])
    return fig

# =========================================================
# 🏆 TOP 15 REGIONS  (remplace le graphe vide timeline)
# =========================================================

@app.callback(
    Output("top_regions", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def top_regions(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)
    if df.empty or not {"region","severity"}.issubset(df.columns):
        return go.Figure()
    grp = (
        df.groupby("region")
        .agg(event_count=("severity","count"),
             avg_severity=("severity","mean"))
        .sort_values("event_count", ascending=False)
        .head(15).reset_index()
    )
    fig = px.bar(
        grp, x="event_count", y="region", orientation="h",
        color="avg_severity",
        title="🏆 Top 15 Regions by Number of Events",
        template="plotly_dark",
        color_continuous_scale="YlOrRd",
        labels={"event_count":"Events","avg_severity":"Avg Severity","region":"Region"},
        text="event_count"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        paper_bgcolor=C["bg"], plot_bgcolor=C["bg"], font_color=C["text"],
        yaxis={"categoryorder":"total ascending"}, height=520,
        coloraxis_colorbar=dict(title="Avg severity")
    )
    return fig

# =========================================================
# 🌍 WORLD MAP — vectorisé + halos + emojis
# =========================================================

@app.callback(
    Output("world_map", "figure"),
    Input("interval",            "n_intervals"),
    Input("filter_event_type",   "value"),
    Input("filter_region",       "value"),
    Input("filter_severity_cat", "value"),
    Input("filter_severity",     "value"),
)
def world_map(n, event_types, regions, severity_cats, severity_range):
    df = apply_filters(load_data(), event_types, regions, severity_cats, severity_range)

    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="#060d1a",
        font_color=C["text"],
        height=680,
        margin=dict(l=0, r=0, t=45, b=0),
        title=dict(text="🌍 SURVEILLANCE DES CATASTROPHES EN TEMPS RÉEL",
                   font=dict(size=16, color="#e5e7eb"), x=0.5),
        legend=dict(bgcolor="rgba(11,18,32,0.8)", bordercolor="#374151",
                    borderwidth=1, font=dict(size=12)),
        geo=dict(
            projection_type="natural earth",
            bgcolor="#071428",
            landcolor="#2d4a1e",
            oceancolor="#071e3d",
            showocean=True,
            showcountries=True,
            countrycolor="#1e3a5f",
            countrywidth=0.5,
            showcoastlines=True,
            coastlinecolor="#1e4976",
            coastlinewidth=0.8,
            showlakes=True,
            lakecolor="#071e3d",
            showrivers=True,
            rivercolor="#0d3460",
            showframe=False,
            showsubunits=True,
            subunitcolor="#162d4a",
        )
    )

    required = {"latitude","longitude","severity","event_type"}
    if df.empty or not required.issubset(df.columns):
        return fig

    df = df.copy()
    df["_style_key"] = df["event_type"].apply(
        lambda et: next((k for k in EVENT_STYLE if k in str(et).lower()), "default")
    )
    df["_color"]  = df["_style_key"].map(lambda k: EVENT_STYLE[k]["color"])
    df["_halo"]   = df["_style_key"].map(lambda k: EVENT_STYLE[k]["halo"])
    df["_symbol"] = df["_style_key"].map(lambda k: EVENT_STYLE[k]["symbol"])
    df["_size"]      = 3 + df["severity"] * 5
    df["_halo_size"] = df["_size"] * 1.6

    sev_label = df["severity"].apply(
        lambda s: "🔴 High" if s >= 0.66 else ("🟠 Medium" if s >= 0.33 else "🟢 Low")
    )
    df["_hover"] = (
        "<b>" + df["event_type"].str.upper() + "</b><br>"
        + "📍 " + df["region"].astype(str) + "<br>"
        + "⚠️ Score : " + df["severity"].map(lambda v: f"{v:.2f}")
        + " — " + sev_label
    )

    for etype, grp in df.groupby("event_type"):
        st = get_style(etype)
        # Halo
        fig.add_trace(go.Scattergeo(
            lat=grp["latitude"], lon=grp["longitude"],
            mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(size=grp["_halo_size"], color=st["halo"],
                        opacity=0.2, line=dict(width=0))
        ))
        # Point principal
        fig.add_trace(go.Scattergeo(
            lat=grp["latitude"], lon=grp["longitude"],
            mode="markers",
            name=f"{st['symbol']} {etype}",
            hovertemplate=grp["_hover"] + "<extra></extra>",
            marker=dict(size=grp["_size"], color=st["color"],
                        opacity=0.75, line=dict(width=0.5, color="white"))
        ))

    return fig

# =========================================================
# ▶️ RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)