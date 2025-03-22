# ################################################################## 
# 
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Sweta Shaw
# Email Id: Sweta.Shaw@Teradata.com
# 
# Secondary Owner: Akhil Bisht
# Email Id: AKHIL.BISHT@Teradata.com
# 
# Version: 1.1
# Function Version: 1.0
# ##################################################################

# Python libraries
import time
import ast

# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.automl.model_training import _ModelTraining


class _ModelEvaluator:
    
    def __init__(self, 
                 df=None, 
                 target_column=None, 
                 task_type=None):
        """
        DESCRIPTION:
            Function initializes the data, target column, features and models
            for model evaluation.
         
        PARAMETERS:  
            df:
                Required Argument.
                Specifies the model information.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies the target column present inside the dataset.
                Types: str
                
            task_type:
                Required Argument.
                Specifies the task type for AutoML, whether to apply regresion OR classification
                on the provived dataset.
                Default Value: "Regression"
                Permitted Values: "Regression", "Classification"
                Types: str

        """
        self.model_info = df
        self.target_column = target_column
        self.task_type = task_type
        
    def model_evaluation(self, 
                         rank, 
                         table_name_mapping,
                         data_node_id, 
                         target_column_ind = True,
                         get_metrics = False):
        """
        DESCRIPTION:
            Function performs the model evaluation on the specified rank in leaderborad.
         
        PARAMETERS:  
            rank:
                Required Argument.
                Specifies the position of ML model for evaluation.
                Types: int
                        
            table_name_mapping:
                Required Argument.
                Specifies the mapping of train,test table names.
                Types: dict
            
            data_node_id:
                Required Argument.
                Specifies the test data node id.
                Types: str
            
            target_column_ind:
                Optional Argument.
                Specifies whether target column is present in the dataset or not.
                Default Value: True
                Types: bool
      
            get_metrics:
                Optional Argument.
                Specifies whether to return metrics or not.
                Default Value: False
                Types: bool
                
        RETURNS:
            tuple containing, performance metrics and predicitions of specified rank ML model.
             
        """
        # Setting target column indicator
        self.target_column_ind = target_column_ind
        self.table_name_mapping = table_name_mapping
        self.data_node_id = data_node_id
        self.get_metrics = get_metrics
        
        # Return predictions only if test data is present and target column is not present
        return self._evaluator(rank)

    def _evaluator(self,
                   rank):
        """
        DESCRIPTION:
            Internal Function runs evaluator function for specified rank ML model
            based on regression/classification problem.
         
        PARAMETERS:  
            rank:
                Required Argument.
                Specifies the position(rank) of ML model for evaluation.
                Types: int
                
        RETURNS:
            tuple containing, performance metrics and predictions of ML model.
             
        """
        # Extracting model using rank
        model = self.model_info.loc[rank]

        ml_name = self.model_info.loc[rank]['MODEL_ID'].split('_')[0]
        
        # Defining eval_params 
        eval_params = _ModelTraining._eval_params_generation(ml_name,
                                                             self.target_column,
                                                             self.task_type)
        
        # Extracting test data for evaluation based on data node id
        test = DataFrame(self.table_name_mapping[self.data_node_id]['{}_new_test'.format(model['FEATURE_SELECTION'])])

        print("\nFollowing model is being picked for evaluation:")
        print("Model ID :", model['MODEL_ID'],
              "\nFeature Selection Method :",model['FEATURE_SELECTION'])
        
        if self.task_type.lower() == 'classification':
            params = ast.literal_eval(model['PARAMETERS'])
            eval_params['output_responses'] = params['output_responses']
        
        # Mapping data according to model type
        data_map = 'test_data' if ml_name == 'KNN' else 'newdata'
        # Performing evaluation if get_metrics is True else returning predictions
        if self.get_metrics:
            metrics = model['model-obj'].evaluate(**{data_map: test}, **eval_params)
            return metrics
        else:
            # Removing accumulate parameter if target column is not present
            if not self.target_column_ind:
                eval_params.pop("accumulate")
            pred = model['model-obj'].predict(**{data_map: test}, **eval_params)
            return pred