from sqlalchemy import create_engine, URL
import datetime
import logging
import os

class DB:
    def __init__(self, config):
        try:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO)
            self.logger.info("Connecting to database")
            self.config = config
            self.engine = create_engine(config['database']['url'])
            self.logger.info("Engine created")
        except Exception as e:
            self.logger.error(f"Engine creation failed: {e}")