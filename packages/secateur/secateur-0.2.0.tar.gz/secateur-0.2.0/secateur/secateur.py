import json
import logging
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

from .config import Config
from .commands import Commands
from .analytics import Analytics
from .logger import Logger

class Secateur(Commands):
    """
    DOC-STRING
    """
    def __init__(self, sql_engine: str, mongo_connection: str,
                 mongo_database: str = 'database', config: dict = None):
        if isinstance(sql_engine, Engine):
            self.sql_engine = sql_engine
            self.sql_connection = self.sql_engine.connect()
            self.session_factory = sessionmaker(bind=self.sql_engine)
        elif isinstance(sql_engine, str):
            self.sql_engine = create_engine(sql_engine)
            self.sql_connection = self.sql_engine.connect()
            self.session_factory = sessionmaker(bind=self.sql_engine)
        else:
            raise ValueError("URL-string or SQL-engine must be provided")
        
        self.__validate_sql_connection()
        
        if isinstance(mongo_connection, MongoClient):
            self.mongo_connection = mongo_connection
            self.mongo_database = self.mongo_connection[mongo_database]
        elif isinstance(mongo_connection, str):
            self.mongo_connection = MongoClient(mongo_connection)
            self.mongo_database = self.mongo_connection[mongo_database]
        else:
            raise ValueError("URL-string or Mongo-connection must be provided")
        
        self.__validate_mongo_connection()
        self.dialect = self.sql_connection.engine.url.get_backend_name()
        self.closed = False
        
        self.__config_internal = Config(sql_connection=self.sql_connection,
                             sql_dialect=self.dialect,
                             mongo_connection=self.mongo_connection,
                             config=config)
        self.config = self.__config_internal.config
        self.logger = self.__refresh_logger()

        print("""\033[96m
   _____                 __                 
  / ___/___  _________ _/ /____  __  _______
  \__ \/ _ \/ ___/ __ `/ __/ _ \/ / / / ___/
 ___/ /  __/ /__/ /_/ / /_/  __/ /_/ / /    
/____/\___/\___/\__,_/\__/\___/\__,_/_/     
\033[0m""")
    
    def __setitem__(self, key: str, value: dict) -> None:
        if not isinstance(key, str):
            raise TypeError("Collection name must be string")
        if not isinstance(value, dict):
            raise TypeError("Migration object must be dict")
        if value["type"] in ("table", "query"):
            self.config["mapping"][key] = value
        else:
            rules = self.config["pruning"].get(key, [])
            rules.append(value.pop("type", value))
            self.config["pruning"][key] = rules

    def __validate_sql_connection(self) -> bool:
        try:
            self.sql_connection.execute(text("SELECT 1;")).fetchone()
        except:
            raise Exception("Connection to SQL database couldn't be established")

    def __validate_mongo_connection(self) -> bool:
        try:
            self.mongo_connection.server_info()["version"]
        except:
            raise Exception("Connection to MongoDB couldn't be established")

    def set_config(self, config: dict = None) -> None:
        self.__config_internal.set_config(config)
        self.config = self.__config_internal.config
        self.logger = self.__refresh_logger()

    def reset_config(self) -> None:
        self.__config_internal.reset_config()

    def validate_config(self, config: dict = {}) -> bool:
        return self.__config_internal.validate_config(config)
    
    def save_config(self, path: str = None) -> None:
        path = f"{self.config['id']}.json" if not(path) else path
        self.__config_internal.save_config(path)

    def auto_config(self, schemes: list = [], tables: list = [], excluded: list = []) -> None:
        try:
            self.__config_internal.auto_config(schemes=schemes, tables=tables, excluded=excluded)
            self.config = self.__config_internal.config
            self.logger = self.__refresh_logger()
            self.logger.logger.log(logging.INFO, "AUTO-CONFIG IS GENERATED WITH: schemes=%s, tables=%s, excluded=%s", schemes, tables, excluded)
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "AUTO-CONFIG IS GENERATED WITH AN ERROR: %s", err)

    def __refresh_logger(self):
        return Logger(self.config["id"], self.config["meta"]["log"])

    def close(self):
        self.sql_connection.close()
        self.session_factory.close_all()
        self.sql_engine.dispose()
        self.mongo_connection.close()
        self.closed = True

    def __del__(self):
        self.close()