import logging
import socketio
import logging
import asyncio
import polars as pl
from datetime import datetime
import toml
from db import DB

logger = logging.getLogger(__name__)

async def get_weather_station_data(config, db_conn, location_id:int, events:int) -> dict:
    config = config['ambient_weather']
    global event_received
    event_received = False

    url = config['uri']+config['app_key']
    sio =  socketio.AsyncClient()
    
    @sio.event
    async def connect():
        await sio.emit("subscribe", {"apiKeys": [config["api_key"]]})
        logger.info("Connected to Ambient Weather API")
    @sio.event
    async def connect_error(data):
        logger.info(f"Connection failed: {data}")
    @sio.event
    async def disconnect():
        logger.info("Disconnected from Ambient Weather API")

    @sio.event
    async def data(data):
        global event_received
        event_received = True
        # Set the data to be returned
        sio.data = data
        sio.data['source'] = "https://ambientweather.net"
        df = transform_data_facts(data ,location_id=location_id)
        print(df.head())
        df.write_database(config['db_table_name'],db_conn,if_table_exists='append')
        logger.info(f'Data written to database:{df.head()}')

    await sio.connect(url, transports=["websocket"])
    for i in range(events):
        event_received = False
        while not event_received:
            logger.info(f"Sleeping for 5 seconds, iteration {i+1}/{events}")
            await sio.sleep(5)
    logger.info("Disconnecting")
    await sio.disconnect()      

def transform_data_facts(ambient_data: dict, location_id: int) -> pl.DataFrame:
    '''
        Transform the data into a format that can be used to create the fact_weather table.
    '''
    if ambient_data is None:
        logger.info("No ambient data to insert")
        raise ValueError("Data is required")
    try:
        # Extract the relevant data from the JSON response
        df = pl.DataFrame({
            'date': datetime.fromisoformat(ambient_data['date']),
            'source': ambient_data['source'],
            'location_id': location_id,
            'temperature': ambient_data['tempf'],
            'pressure': ambient_data['baromrelin'],
            'humidity': ambient_data['humidity'],
            'wind_direction': ambient_data['winddir'],
            'wind_speed': ambient_data['windspdmph_avg10m'],
            'wind_gust': ambient_data['windgustmph'],
            'daily_precipitation': ambient_data['dailyrainin']
        })
        return df
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise ValueError(f'Error transforming data: {e}')

def run_weather_download(num_reads: int, location_id: int = 1):
    import toml, os
    config = toml.load('/weather_analysis/config/config.toml')
    db = DB(config)
    with db.engine.connect() as conn:
        asyncio.run(get_weather_station_data(config, conn, location_id, num_reads))
    print('complete')
    return "Complete"

# if __name__ == '__main__':
#     logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO,)
#     try:
#         config = toml.load('config/config.toml')
#         db = DB(config, url='url_test')
#         conn = db.engine.connect()
#         asyncio.run(get_weather_station_data(config, conn, 1, 1))
#         print('complete')
#     except Exception as e:
#         logger.error(f'Error writing to database or getting data from api: {e}')