from src.data_ingestion.data_ingestion import DataIngestion
from src.data_preprocessing.data_preprocessing import DataPreprocessor
from src.model_training.model_training import ModelTrainer
from src.feature_store.feature_store import FeatureStore
from config.path_config import *
from config.data_config import *

if __name__ == "__main__":
   
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()
    
    feature_store = FeatureStore()
    
    data_preprocessor = DataPreprocessor(TRAIN_PATH, TEST_PATH, feature_store)
    data_preprocessor.run()
    
    feature_store = FeatureStore()
    model_trainer = ModelTrainer(feature_store)
    model_trainer.run()