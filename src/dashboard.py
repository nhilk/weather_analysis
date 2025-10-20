from dash import Dash, html, dcc
import plotly.express as px
import polars as ps
from db import DB
import toml

config = toml.load('config/config.toml')
db = DB(config = config)
conn = db.engine.connect()

app = Dash()


query_str = 'SELECT date, temperature FROM fact_weather'
df = ps.read_database(query=query_str,connection=conn)

fig = px.line(df, x='date', y='temperature')

app.layout = html.Div(children=[
    html.H1(children='Temperature'),
    dcc.Graph(id='temperature-graph',
              figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)