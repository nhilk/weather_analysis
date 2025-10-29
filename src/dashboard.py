from dash import Dash, html, dcc, dash_table
import sys
import toml
import logging
import os
import polars as ps
from sqlalchemy import text
import plotly.express as px
import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO,)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from db import DB
from call_backs import register_callbacks

def create_app():
    config = toml.load('config/config.toml')
    db = DB(config = config)
    queries = toml.load('src/queries.toml')
    query_keys = list(queries.keys())
    #manager = CeleryManager(celery_app)


    app = Dash(__name__)#background_callback_manager=manager)

    app.layout = html.Div(children=[
        html.H1(children='Temperature'),
        dbc.Row([dcc.Input(id='api_input'.format('number')),
                html.Button('Trigger API', id='trigger_api',n_clicks=0),
                html.Button('Refresh Latest Weather', id='get_latest_weather',n_clicks=0)]),
        dcc.Store(id='ambient_job_triggered'),
        
        dcc.Dropdown(query_keys,query_keys[0],id='graph_to_display'),
        dash_table.DataTable(id='latest_weather',style_header={'fontWeight':'bold'}),
        dcc.Graph(id='display_graph')
    ])
    register_callbacks(app, db)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8050)