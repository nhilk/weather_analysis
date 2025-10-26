from dash import Input, Output
import toml
import sys, os
import polars as ps
from sqlalchemy import text
import plotly.express as px
import ambient_weather


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from db import DB
from celery_app import run_weather_download_task

# Top-level function to enqueue the Celery task wrapper and return immediately
def do_ambient_download(n_clicks):
    if not n_clicks:
        return None
    # Enqueue the periodic/task wrapper directly; worker will execute it
    run_weather_download_task.delay(1, 1)
    return {"status": "queued"}

def register_callbacks(app):
    @app.callback(
        Output('display_graph','figure'),
        Input('graph_to_display', 'value')
    )
    def update_graph(graph_to_display):
        config = toml.load('config/config.toml')
        queries = toml.load('src/queries.toml')
        query = queries[graph_to_display]
        db = DB(config = config)
        selectable = text(query['query'])
        with db.engine.connect() as conn:
            df = ps.read_database(query=selectable,connection=conn)
        match query['graph_type']:
            case 'line':
                fig = px.line(df,x=query['columns']['x'], y=query['columns']['y'])
            case 'scatter':
                fig = px.scatter(df, x=query['columns']['x'], y=query['columns']['y'])
            case _:
                fig = px.line(df,x=query['columns']['x'], y=query['columns']['y'])
        return fig

    # Register a quick enqueue callback (no background=True since it returns immediately)
    app.callback(
        Output('ambient_job_triggered', 'data'),
        Input('trigger_api', 'n_clicks'),
    )(do_ambient_download)
