import psycopg2
import os
import sys
import pandas as pd
from src.exception.custom_exception import CustomException
from src.logginig.logger import get_logger
from sklearn.model_selection import train_test_split
from config.data_config import DB_CONFIG
from config.path_config import *

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, db_params, output_dir):
        self.db_params = db_params
        self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        
    def connect_to_db(self):
        try:
            connect = psycopg2.connect(
                host = self.db_params['host'],
                port = self.db_params['port'],
                dbname = self.db_params['dbname'],
                user = self.db_params['user'],
                password = self.db_params['password']
            )

            logger.info("Database connection established...")
            return connect
        except Exception as e:
            logger.error(f"Error while establishing connection {e}")
            raise CustomException(str(e),sys)
        
    def extract_data(self):
        try:
            connect = self.connect_to_db()
            query = "SELECT * FROM public.titanic"
            df = pd.read_sql_query(query, connect)
            logger.info("Data extracted from DB")
            return df

        except Exception as e:
            logger.error(f"Error while extracting data {e}")
            raise CustomException(str(e),sys)
             
        
    def save_data(self, df):
        try:
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
            train_df.to_csv(TRAIN_PATH,index=False)
            test_df.to_csv(TEST_PATH , index=False)
            
            logger.info("Data Splitting and saving done")
        except Exception as e:
            logger.error(f"Error while saving data {e}")
            raise CustomException(str(e),sys)
        
    def run(self):
        try:
            logger.info("Data Ingestion Pipleine Started..../")
            df = self.extract_data()
            self.save_data(df)
            logger.info("End of Data Ingestion Pipline..")
        except Exception as e:
            logger.error(f"Error while Data Ingestion Piplleine {e}")
            raise CustomException(str(e),sys)

if __name__ == '__main__':
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()