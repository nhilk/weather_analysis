from dash import Dash, html, dcc, CeleryManager
import sys
import toml
import logging
import os
import polars as ps
from sqlalchemy import text
import plotly.express as px

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO,)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from celery_app import celery_app
from db import DB
from call_backs import register_callbacks

def create_app():
    config = toml.load('config/config.toml')
    db = DB(config = config)
    queries = toml.load('src/queries.toml')
    query_keys = list(queries.keys())
    #manager = CeleryManager(celery_app)


    app = Dash(__name__)#background_callback_manager=manager)

    selectable = text(queries['all_weather']['query'])
    with db.engine.connect() as conn:
        df = ps.read_database(query=selectable,connection=conn)


    fig = px.line(df, x='date', y='temperature')

    app.layout = html.Div(children=[
        html.H1(children='Temperature'),
        html.Button('Trigger API', id='trigger_api',n_clicks=0),
        dcc.Store(id='ambient_job_triggered'),
        dcc.Dropdown(query_keys,query_keys[0],id='graph_to_display'),
        dcc.Graph(id='display_graph')
    ])
    register_callbacks(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8050)