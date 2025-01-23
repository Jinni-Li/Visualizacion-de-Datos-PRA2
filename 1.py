import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Leer el dataset
df = pd.read_csv("spotify_tracks_filtered.csv")

# Preparar la aplicación Dash
app = Dash(__name__)
app.title = "Spotify Dashboard"

# Layout del dashboard
app.layout = html.Div([
    html.H1("Spotify Data Dashboard", style={"textAlign": "center"}),

    # Dropdown para seleccionar el año
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id="year-dropdown",
            options=[
                {"label": str(year), "value": year} for year in sorted(df["year"].unique()) if not pd.isnull(year)
            ],
            placeholder="All Years",
            multi=False
        ),
    ], style={"width": "50%", "margin": "auto"}),

    html.Hr(),

    # Gráfico de Barras para Keywords
    html.Div([
        dcc.Graph(id="top-keywords-bar"),
    ]),

    # Tablas para Canciones y Álbumes
    html.Div([
        html.H3("Top 3 Songs"),
        html.Table(id="top-songs-table", style={"width": "100%", "margin": "auto"}),

        html.H3("Top 3 Albums"),
        html.Table(id="top-albums-table", style={"width": "100%", "margin": "auto"})
    ]),

    html.Hr(),

    # Detalles de los artistas
    html.Div([
        html.H3("Top Artist Details"),
        html.Div(id="artist-details", style={"margin": "auto", "textAlign": "center"})
    ])
])

# Callback para actualizar los datos según el año seleccionado
@app.callback(
    [
        Output("top-keywords-bar", "figure"),
        Output("top-songs-table", "children"),
        Output("top-albums-table", "children"),
        Output("artist-details", "children"),
    ],
    [Input("year-dropdown", "value")]
)
def update_dashboard(selected_year):
    # Filtrar los datos según el año seleccionado
    if selected_year:
        filtered_df = df[df["year"] == selected_year]
    else:
        filtered_df = df

    # Top 3 Keywords por Popularidad
    keywords = filtered_df[["danceability", "energy", "valence"]].mean().sort_values(ascending=False).head(3)
    fig_keywords = px.bar(
        x=keywords.index, y=keywords.values, labels={"x": "Keywords", "y": "Average Value"},
        title="Top 3 Keywords by Popularity"
    )

    # Top 3 Songs
    top_songs = filtered_df.sort_values(by="popularity", ascending=False)[["track_name", "popularity"]].head(3)
    songs_table = [
        html.Tr([html.Th("Track Name", style={"textAlign": "center"}), html.Th("Popularity", style={"textAlign": "center"})])
        ] + [
            html.Tr([html.Td(song.track_name, style={"textAlign": "center"}), html.Td(song.popularity, style={"textAlign": "center"})])
            for song in top_songs.itertuples()
            ]

    # Top 3 Albums
    top_albums = filtered_df.groupby("album_name")["popularity"].mean().sort_values(ascending=False).head(3)
    albums_table = [
        html.Tr([html.Th("Album Name", style={"textAlign": "center"}), html.Th("Average Popularity", style={"textAlign": "center"})])
        ] + [
            html.Tr([html.Td(album, style={"textAlign": "center"}), html.Td(avg_popularity, style={"textAlign": "center"})])
            for album, avg_popularity in top_albums.items()
            ]

    # Top Artist Details
    top_artist = filtered_df.groupby("artist_name")["popularity"].mean().idxmax()
    artist_df = filtered_df[filtered_df["artist_name"] == top_artist]
    most_popular_album = artist_df.groupby("album_name")["popularity"].mean().idxmax()
    top_tracks = artist_df.sort_values(by="popularity", ascending=False)[["track_name", "popularity"]].head(3)
    artist_keywords = artist_df[["danceability", "energy", "valence"]].mean().sort_values(ascending=False).head(3).index.tolist()

    artist_details = html.Div([
        html.H4(f"Top Artist: {top_artist}"),
        html.P(f"Most Popular Album: {most_popular_album}"),
        html.H5("Top 3 Tracks:"),
        html.Ul([html.Li(f"{track.track_name} (Popularity: {track.popularity})") for track in top_tracks.itertuples()]),
        html.H5("Top Keywords:"),
        html.Ul([html.Li(keyword) for keyword in artist_keywords])
    ])

    return fig_keywords, songs_table, albums_table, artist_details


if __name__ == "__main__":
    app.run_server(debug=True)
