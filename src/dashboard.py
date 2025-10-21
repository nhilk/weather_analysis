from dash import Dash, html, dcc, callback, Input, Output, CeleryManager
from sqlalchemy import text
import plotly.express as px
import polars as ps
from db import DB
from celery_app import celery_app
import toml

config = toml.load('config/config.toml')
db = DB(config = config)
conn = db.engine.connect()
queries = toml.load('src/queries.toml')
query_keys = list(queries.keys())
manager = CeleryManager(celery_app)


app = Dash(__name__,background_callback_manager=manager)

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
    app.run(host='0.0.0.0', port=8050,debug=True)