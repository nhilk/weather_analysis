from dash import Dash, html, dcc, callback, Input, Output
from sqlalchemy import text
import plotly.express as px
import polars as ps
from db import DB
import toml

config = toml.load('config/config.toml')
db = DB(config = config)
conn = db.engine.connect()
queries = toml.load('src/queries.toml')
query_keys = list(queries.keys())


app = Dash()

selectable = text(queries['all_weather']['query'])
df = ps.read_database(query=selectable,connection=conn)

fig = px.line(df, x='date', y='temperature')

app.layout = html.Div(children=[
    html.H1(children='Temperature'),
    dcc.Dropdown(query_keys,query_keys[0],id='graph_to_display'),
    dcc.Graph(id='display_graph')
])

@callback(
    Output('display_graph','figure'),
    Input('graph_to_display', 'value')
)
def update_graph(graph_to_display):
    query = queries[graph_to_display]
    selectable = text(query['query'])
    df = ps.read_database(query=selectable,connection=conn)
    fig = px.line(df,x=query['columns']['x'], y=query['columns']['y'])
    return fig

if __name__ == '__main__':
    app.run(debug=True)