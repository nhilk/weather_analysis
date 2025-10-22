from dash import Dash, html, dcc, callback, Input, Output, CeleryManager, State
import sys
from sqlalchemy import text
import plotly.express as px
import polars as ps
import toml
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO,)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from db import DB
from celery_app import celery_app
import ambient_weather


config = toml.load('config/config.toml')
db = DB(config = config)
queries = toml.load('src/queries.toml')
query_keys = list(queries.keys())
manager = CeleryManager(celery_app)


app = Dash(__name__,background_callback_manager=manager)

selectable = text(queries['all_weather']['query'])
with db.engine.connect() as conn:
    df = ps.read_database(query=selectable,connection=conn)


fig = px.line(df, x='date', y='temperature')

app.layout = html.Div(children=[
    html.H1(children='Temperature'),
    html.Button('Tigger API', id='trigger_api',n_clicks=0),
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
    with db.engine.connect() as conn:
        df = ps.read_database(query=selectable,connection=conn)
    fig = px.line(df,x=query['columns']['x'], y=query['columns']['y'])
    return fig

@callback(
    Input('trigger_api', 'n_clicks'),
    background=True
)
def trigger_ambient_api(n_clicks):
    ambient_weather.run_weather_download(num_reads=1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050,debug=True)