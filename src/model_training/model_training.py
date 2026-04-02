import os
import sys
import pandas as pd
import joblib
import pickle
from src.feature_store.feature_store import FeatureStore
from src.exception.custom_exception import CustomException
from src.logginig.logger import get_logger
from config.path_config import *
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score


logger = get_logger(__name__)

class ModelTrainer:
    def __init__(self, feature_store : FeatureStore, model_dave_path=MODEL_DIR):
        self.feature_store = feature_store
        self.model_save_path = model_dave_path
        self.model = None
        
        os.makedirs(self.model_save_path, exist_ok=True)
        logger.info("Your Model Trainer is intialized...")
        
        
    def load_data_from_redis(self, entity_ids):
        try:
            logger.info("Extracting data from Redis")

            data = []
            for entity_id in entity_ids:
                features = self.feature_store.get_features(entity_id)
                if features:
                    data.append(features)
                else:
                    logger.warning("Feature not found")
            return data
        except Exception as e:
            logger.error(f"Error while loading data from Redis {e}")
            raise CustomException(str(e), sys)
        
    def prepare_data(self):
        try:
            entity_ids = self.feature_store.get_all_features()
            
            train_entity_ids, test_entity_ids = train_test_split(entity_ids, test_size=0.2, random_state=42)
            
            train_data = self.load_data_from_redis(train_entity_ids)
            test_data = self.load_data_from_redis(test_entity_ids)
            
            train_df = pd.DataFrame(train_data)
            test_df = pd.DataFrame(test_data)
            
            x_train = train_df.drop('Survived', axis=1)
            logger.info(x_train.shape)
            x_test = test_df.drop('Survived', axis=1)
            y_train = train_df['Survived']
            y_test = test_df['Survived']
            
            logger.info("Preparation for Model Training completed")
            return x_train , x_test , y_train, y_test
            
        except Exception as e:
            logger.error(f"Error while preparing data {e}")
            raise CustomException(str(e), sys)
        
        
    def hyperparamter_tuning(self, x_train, y_train):
        try:
            logger.info("Starting Hyperparameter Tuning")
            
            
            param_distributions = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, 30],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
            
            rf = RandomForestClassifier(random_state=42 )
            random_search = RandomizedSearchCV(rf, param_distributions, n_iter=10, cv=3, scoring='accuracy', random_state=42)
            random_search.fit(x_train, y_train)
            
            
            logger.info(f"Best paramters : {random_search.best_params_}")
            return random_search.best_estimator_
        
        except Exception as e:
            logger.error(f"Error while hyperparamter tuning {e}")
            raise CustomException(str(e), sys)
        
        
    def train_and_evaluate(self, x_train, x_test, y_train, y_test):
        try:
            logger.info("Starting Model Training and Evaluation")
            
            best_rf = self.hyperparamter_tuning(x_train, y_train)
            
            y_pred = best_rf.predict(x_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f'Accuracy: {accuracy}')
            logger.info(f'Recall: {recall}')
            logger.info(f'Precision: {precision}')
            logger.info(f'F1 Score: {f1}')
            
            self.save_model(best_rf)
            
            return accuracy, recall, precision, f1
        
        except Exception as e:
            logger.error(f"Error while model training {e}")
            raise CustomException(str(e), sys)
        
    def save_model(self, model):
        try:
            model_filename = f'{self.model_save_path}random_forest_model.pkl'
            
            with open(model_filename, 'wb') as f:  
                pickle.dump(model, f)
                
            
            logger.info(f"Model saved at {model_filename}")
        except Exception as e:
            logger.error(f"Error while model saving {e}")
            raise CustomException(str(e), sys)
        

    def run(self):
        try:
            logger.info("Starting Model Training Pipleine....")
             
            x_train, x_test, y_train, y_test = self.prepare_data()
             
            accuracy = self.train_and_evaluate(x_train, x_test, y_train, y_test)
             
             
            logger.info("End of Model Training pipeline...")

        except Exception as e:
            logger.error(f"Error while model training pipeline {e}")
            raise CustomException(str(e), sys)
        
    
if __name__ == "__main__":
    feature_store = FeatureStore()
    model_trainer = ModelTrainer(feature_store)
    model_trainer.run()
        