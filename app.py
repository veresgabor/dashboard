from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "gapminder.csv"

df = pd.read_csv(DATA_PATH)
years = [int(year) for year in sorted(df["year"].unique())]
continents = sorted(df["continent"].unique())
colors = px.colors.qualitative.Safe

app = Dash(__name__)
app.title = "gapminder dashboard"


def get_selected_countries(selected_data):
    if not selected_data or "points" not in selected_data:
        return []

    countries = []
    for point in selected_data["points"]:
        country = point["customdata"][0]
        if country not in countries:
            countries.append(country)
    return countries


def make_scatter(current_df):
    fig = px.scatter(
        current_df,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        custom_data=["country"],
        color_discrete_sequence=colors,
        log_x=True,
        size_max=45,
        title="life expectancy and gdp per capita",
        labels={
            "gdpPercap": "GDP per capita (log scale)",
            "lifeExp": "Life expectancy",
            "pop": "Population",
        },
    )
    fig.update_traces(marker_line_color="white", marker_line_width=1, opacity=0.8)
    fig.update_layout(
        template="plotly_white",
        dragmode="select",
        legend_title_text="continent",
        margin=dict(l=50, r=20, t=60, b=50),
    )
    return fig


def make_bar(current_df, selected_countries):
    if selected_countries:
        bar_df = current_df[current_df["country"].isin(selected_countries)].copy()
        title = "population of selected countries"
    else:
        bar_df = current_df.nlargest(10, "pop").copy()
        title = "top 10 countries by population"

    bar_df = bar_df.sort_values("pop", ascending=True)
    fig = px.bar(
        bar_df,
        x="pop",
        y="country",
        orientation="h",
        color="continent",
        color_discrete_sequence=colors,
        title=title,
        labels={"pop": "Population", "country": ""},
    )
    fig.update_layout(template="plotly_white", margin=dict(l=50, r=20, t=60, b=50))
    fig.update_xaxes(rangemode="tozero")
    return fig


def make_line(history_df, selected_countries):
    if selected_countries:
        line_df = history_df[history_df["country"].isin(selected_countries)].copy()
        fig = px.line(
            line_df,
            x="year",
            y="lifeExp",
            color="country",
            markers=True,
            title="life expectancy over time for selected countries",
            labels={"year": "Year", "lifeExp": "Life expectancy", "country": "Country"},
        )
    else:
        line_df = (
            history_df.groupby(["year", "continent"], as_index=False)["lifeExp"]
            .mean()
        )
        fig = px.line(
            line_df,
            x="year",
            y="lifeExp",
            color="continent",
            markers=True,
            color_discrete_sequence=colors,
            title="average life expectancy over time",
            labels={
                "year": "Year",
                "lifeExp": "Average life expectancy",
                "continent": "Continent",
            },
        )

    fig.update_layout(template="plotly_white", margin=dict(l=50, r=20, t=60, b=50))
    return fig


def make_map(current_df, selected_countries, full_df):
    if selected_countries:
        map_df = current_df[current_df["country"].isin(selected_countries)].copy()
        title = "life expectancy map for selected countries"
    else:
        map_df = current_df.copy()
        title = "life expectancy map"

    fig = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="lifeExp",
        hover_name="country",
        hover_data={
            "continent": True,
            "lifeExp": ":.1f",
            "gdpPercap": ":.0f",
            "pop": ":,.0f",
        },
        color_continuous_scale="Blues",
        range_color=(full_df["lifeExp"].min(), full_df["lifeExp"].max()),
        title=title,
        labels={"lifeExp": "Life expectancy"},
    )
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=60, b=0))
    fig.update_geos(showcoastlines=False, showframe=False)
    return fig


app.layout = html.Div(
    [
        html.H1("gapminder dashboard"),
        html.P(
            "for sociology students who want to compare countries over time. "
            "select countries in the scatter plot to update the other charts."
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("year"),
                        dcc.Slider(
                            id="year-slider",
                            min=min(years),
                            max=max(years),
                            step=None,
                            value=max(years),
                            marks={year: str(year) for year in years},
                        ),
                    ],
                    style={"marginBottom": "20px"},
                ),
                html.Div(
                    [
                        html.Label("continents"),
                        dcc.Checklist(
                            id="continent-checklist",
                            options=[{"label": continent, "value": continent} for continent in continents],
                            value=continents,
                            inline=True,
                        ),
                    ]
                ),
            ],
            style={
                "backgroundColor": "#f5f7fa",
                "padding": "16px",
                "borderRadius": "10px",
                "marginBottom": "20px",
            },
        ),
        html.P(id="selection-text"),
        html.Div(
            [
                dcc.Graph(id="scatter-chart", style={"height": "420px"}),
                dcc.Graph(id="bar-chart", style={"height": "420px"}),
                dcc.Graph(id="line-chart", style={"height": "420px"}),
                dcc.Graph(id="map-chart", style={"height": "420px"}),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                "gap": "16px",
            },
        ),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
    },
)


@app.callback(
    Output("selection-text", "children"),
    Output("scatter-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("line-chart", "figure"),
    Output("map-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-checklist", "value"),
    Input("scatter-chart", "selectedData"),
)
def update_dashboard(selected_year, selected_continents, selected_data):
    if not selected_continents:
        selected_continents = continents

    current_df = df[
        (df["year"] == selected_year) & (df["continent"].isin(selected_continents))
    ].copy()
    history_df = df[df["continent"].isin(selected_continents)].copy()

    selected_countries = get_selected_countries(selected_data)

    if selected_countries:
        selection_text = f"selected countries: {', '.join(selected_countries)}"
    else:
        selection_text = "selected countries: none"

    scatter_fig = make_scatter(current_df)
    bar_fig = make_bar(current_df, selected_countries)
    line_fig = make_line(history_df, selected_countries)
    map_fig = make_map(current_df, selected_countries, current_df)

    return selection_text, scatter_fig, bar_fig, line_fig, map_fig


if __name__ == "__main__":
    app.run(debug=True)
