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
import json
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
import time
import ast
import warnings
import joblib
from io import BytesIO

# Teradata libraries
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import ColumnExpression
from teradataml.dataframe.dataframe import DataFrame
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators
from teradataml import ROC, BLOB, VARCHAR
from teradataml.utils.dtypes import _Dtypes
from teradataml.common.utils import UtilFuncs
from teradataml import TeradataMlException
from teradataml.common.messages import Messages, MessageCodes
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml import TeradataConstants
from teradataml import XGBoost, DecisionForest, KNN, SVM, GLM, db_drop_table

# AutoML Internal libraries
from teradataml.automl.data_preparation import _DataPreparation
from teradataml.automl.feature_engineering import _FeatureEngineering
from teradataml.automl.feature_exploration import _FeatureExplore, _is_terminal
from teradataml.automl.model_evaluation import _ModelEvaluator
from teradataml.automl.model_training import _ModelTraining
from teradataml.automl.data_transformation import _DataTransformation
from teradataml.automl.custom_json_utils import _GenerateCustomJson


class AutoML:
    
    def __init__(self,
                 task_type = "Default",
                 include = None,
                 exclude = None,
                 verbose = 0,
                 max_runtime_secs = None,
                 stopping_metric = None, 
                 stopping_tolerance = None,
                 max_models = None,
                 custom_config_file = None,
                 **kwargs):
        """
        DESCRIPTION:
            AutoML (Automated Machine Learning) is an approach that automates the process 
            of building, training, and validating machine learning models. It involves 
            various algorithms to automate various aspects of the machine learning workflow, 
            such as data preparation, feature engineering, model selection, hyperparameter
            tuning, and model deployment. It aims to simplify the process of building 
            machine learning models, by automating some of the more time-consuming 
            and labor-intensive tasks involved in the process.
            
            AutoML is designed to handle both regression and classification (binary and 
            multiclass) tasks. User can specify the task type whether to apply
            regression OR classification algorithm on the provided dataset. By default, AutoML 
            decides the task type.
            
            AutoML by default, trains using all model algorithms applicable for the 
            task type problem. For example, "glm" and "svm" does not support multi-class 
            classification problem. Thus, only 3 models are available to train in case 
            of multi-class classification problem, by default. While for regression and 
            binary classification problem, all 5 models i.e., "glm", "svm", "knn", 
            "decision_forest", "xgboost" are available to train by default.
            
            AutoML provides functionality to use specific model algorithms for training.
            User can provide either include or exclude model. In case of include, 
            only specified models are trained while for exclude, all models except 
            specified model are trained.
            
            AutoML also provides an option to customize the processes within feature
            engineering, data preparation and model training phases. User can customize
            the processes by passing the JSON file path in case of custom run. It also 
            supports early stopping of model training based on stopping metrics,
            maximum running time and maximum models to be trained.
            Note:
                * configure.temp_object_type="VT" follows sequential execution.

         
        PARAMETERS:  
            task_type:
                Optional Argument.
                Specifies the task type for AutoML, whether to apply regression OR classification
                on the provided dataset. If user wants AutoML to decide the task type automatically, 
                then it should be set to "Default".
                Default Value: "Default"
                Permitted Values: "Regression", "Classification", "Default"
                Types: str
            
            include:
                Optional Argument.
                Specifies the model algorithms to be used for model training phase.
                By default, all 5 models are used for training for regression and binary
                classification problem, while only 3 models are used for multi-class.
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str
                    
            
            exclude:
                Optional Argument.
                Specifies the model algorithms to be excluded from model training phase.
                No model is excluded by default. 
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str
            
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
                
            max_runtime_secs:
                Optional Argument.
                Specifies the time limit in seconds for model training.
                Types: int
                
            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
                Specifies the stopping metrics for stopping tolerance in model training.
                Permitted Values: 
                    * For task_type "Regression": "R2", "MAE", "MSE", "MSLE",
                                                  "MAPE", "MPE", "RMSE", "RMSLE",
                                                  "ME", "EV", "MPD", "MGD"

                    * For task_type "Classification": 'MICRO-F1','MACRO-F1',
                                                      'MICRO-RECALL','MACRO-RECALL',
                                                      'MICRO-PRECISION', 'MACRO-PRECISION',
                                                      'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                                                      'WEIGHTED-F1', 'ACCURACY'
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
                Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
            
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int
                
            custom_config_file:
                Optional Argument.
                Specifies the path of JSON file in case of custom run.
                Types: str

            **kwargs:
                Specifies the additional arguments for AutoML. Below
                are the additional arguments:
                    volatile:
                        Optional Argument.
                        Specifies whether to put the interim results of the
                        functions in a volatile table or not. When set to
                        True, results are stored in a volatile table,
                        otherwise not.
                        Default Value: False
                        Types: bool

                    persist:
                        Optional Argument.
                        Specifies whether to persist the interim results of the
                        functions in a table or not. When set to True,
                        results are persisted in a table; otherwise,
                        results are garbage collected at the end of the
                        session.
                        Default Value: False
                        Types: bool
                    
                    seed:
                        Optional Argument.
                        Specifies the random seed for reproducibility.
                        Default Value: 42
                        Types: int
                
        RETURNS:
            Instance of AutoML.
    
        RAISES:
            TeradataMlException, TypeError, ValueError
        
        EXAMPLES:
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function raises error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("GLMPredict", ["admissions_test", "admissions_train"])
            >>> load_example_data("decisionforestpredict", ["housing_train", "housing_test"])
            >>> load_example_data("teradataml", "iris_input")
    
            # Create teradataml DataFrames.
            >>> admissions_train = DataFrame.from_table("admissions_train")
            >>> admissions_test = DataFrame.from_table("admissions_test")
            >>> housing_train = DataFrame.from_table("housing_train")
            >>> housing_test = DataFrame.from_table("housing_test")
            >>> iris_input = DataFrame.from_table("iris_input")
            
            # Example 1: Run AutoML for classification problem.
            # Scenario: Predict whether a student will be admitted to a university
            #           based on different factors. Run AutoML to get the best 
            #           performing model out of available models.
           
            # Create an instance of AutoML.
            >>> automl_obj = AutoML(task_type="Classification")

            # Fit the data.
            >>> automl_obj.fit(admissions_train, "admitted")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()

            # Display best performing model.
            >>> automl_obj.leader()
            
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(admissions_test)
            >>> prediction
            
            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(admissions_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(admissions_test)
            >>> performance_metrics
            
            # Run evaluate to get performance metrics using model rank 3.
            >>> performance_metrics = automl_obj.evaluate(admissions_test, rank=3)
            >>> performance_metrics

            # Example 2 : Run AutoML for regression problem.
            # Scenario : Predict the price of house based on different factors.
            #            Run AutoML to get the best performing model using custom
            #            configuration file to customize different processes of
            #            AutoML Run. Use include to specify "xgbooost" and
            #            "decision_forset" models to be used for training.  
            
            # Generate custom JSON file
            >>> AutoML.generate_custom_config("custom_housing")           

            # Create instance of AutoML.
            >>> automl_obj = AutoML(task_type="Regression",
            >>>                     verbose=1,
            >>>                     include=["decision_forest", "xgboost"], 
            >>>                     custom_config_file="custom_housing.json")
            # Fit the data.
            >>> automl_obj.fit(housing_train, "price")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
  
            # Display best performing model.
            >>> automl_obj.leader()
            
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(housing_test)
            >>> prediction
            
            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(housing_test, rank=2)
            >>> prediction

            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test)
            >>> performance_metrics
            
            # Run evaluate to get performance metrics using second best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test, rank=2)
            >>> performance_metrics

            # Example 3 : Run AutoML for multiclass classification problem.
            # Scenario : Predict the species of iris flower based on different
            #            factors. Use custom configuration file to customize 
            #            different processes of AutoML Run to get the best
            #            performing model out of available models.
            
            # Split the data into train and test.
            >>> iris_sample = iris_input.sample(frac = [0.8, 0.2])
            >>> iris_train= iris_sample[iris_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> iris_test = iris_sample[iris_sample['sampleid'] == 2].drop('sampleid', axis=1)
            
            # Generate custom JSON file
            >>> AutoML.generate_custom_config()

            # Create instance of AutoML.
            >>> automl_obj = AutoML(verbose=2, 
            >>>                     exclude="xgboost",
            >>>                     custom_config_file="custom.json")
            
            # Fit the data.
            >>> automl_obj.fit(iris_train, iris_train.species)

            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Display best performing model.
            >>> automl_obj.leader()

            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(iris_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(iris_test)
            >>> performance_metrics
 
            # Example 4 : Run AutoML for regression problem with early stopping metric and tolerance.
            # Scenario : Predict the price of house based on different factors. 
            #            Use custom configuration file to customize different 
            #            processes of AutoML Run. Define performance threshold
            #            to acquire for the available models, and terminate training 
            #            upon meeting the stipulated performance criteria.
            
            # Generate custom JSON file
            >>> AutoML.generate_custom_config("custom_housing")

            # Create instance of AutoML.
            >>> automl_obj = AutoML(verbose=2, 
            >>>                     exclude="xgboost",
            >>>                     stopping_metric="R2",
            >>>                     stopping_tolerance=0.7,
            >>>                     max_models=10,
            >>>                     custom_config_file="custom_housing.json")
            # Fit the data.
            >>> automl_obj.fit(housing_train, "price")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(housing_test)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test)
            >>> performance_metrics

            # Example 5 : Run AutoML for regression problem with maximum runtime.
            # Scenario : Predict the species of iris flower based on different factors.
            #            Run AutoML to get the best performing model in specified time.

            # Split the data into train and test.
            >>> iris_sample = iris_input.sample(frac = [0.8, 0.2])
            >>> iris_train= iris_sample[iris_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> iris_test = iris_sample[iris_sample['sampleid'] == 2].drop('sampleid', axis=1)
            
            # Create instance of AutoML.
            >>> automl_obj = AutoML(verbose=2, 
            >>>                     exclude="xgboost",
            >>>                     max_runtime_secs=500,
            >>>                     max_models=3)
            
            # Fit the data.
            >>> automl_obj.fit(iris_train, iris_train.species)
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Display best performing model.
            >>> automl_obj.leader()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(iris_test)
            >>> prediction

            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(iris_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(iris_test)
            >>> performance_metrics
            
            # Run evaluate to get performance metrics using model rank 4.
            >>> performance_metrics = automl_obj.evaluate(iris_test, 4)
            >>> performance_metrics  
        """
        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["task_type", task_type, True, (str), True, ["Regression", "Classification", "Default"]])
        arg_info_matrix.append(["include", include, True, (str, list), True, ["glm", "svm", "knn", 
                                                                              "decision_forest", "xgboost"]])
        arg_info_matrix.append(["exclude", exclude, True, (str, list), True, ["glm", "svm", "knn", 
                                                                              "decision_forest", "xgboost"]])
        arg_info_matrix.append(["verbose", verbose, True, (int), True, [0,1,2]])
        arg_info_matrix.append(["max_runtime_secs", max_runtime_secs, True, (int, float)])
        arg_info_matrix.append(["stopping_metric", stopping_metric, True, (str), True, ["R2", "MAE", "MSE", "MSLE",
                                                                                        "MAPE", "MPE", "RMSE", "RMSLE",
                                                                                        "ME", "EV", "MPD", "MGD",
                                                                                        'MICRO-F1','MACRO-F1',
                                                                                        'MICRO-RECALL','MACRO-RECALL',
                                                                                        'MICRO-PRECISION', 'MACRO-PRECISION',
                                                                                        'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                                                                                        'WEIGHTED-F1', 'ACCURACY']])
        arg_info_matrix.append(["stopping_tolerance", stopping_tolerance, True, (float, int)])
        arg_info_matrix.append(["max_models", max_models, True, (int)])
        arg_info_matrix.append(["custom_config_file", custom_config_file, True, (str), True])

        volatile = kwargs.get('volatile', False)
        persist = kwargs.get('persist', False)
        seed = kwargs.get('seed', 42)

        arg_info_matrix.append(["volatile", volatile, True, (bool)])
        arg_info_matrix.append(["persist", persist, True, (bool)])
        arg_info_matrix.append(["seed", seed, True, (int)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)
        # Either include or exclude can be used.
        if include is not None or exclude is not None:
            _Validators._validate_mutually_exclusive_arguments(include, "include", exclude, "exclude")
        # Either volatile or persist can be used.
        if volatile and persist:
            _Validators._validate_mutually_exclusive_arguments(volatile, "volatlie", persist, "persist")
        # Validate mutually inclusive arguments
        _Validators._validate_mutually_inclusive_arguments(stopping_metric, "stopping_metric", stopping_tolerance, "stopping_tolerance")
        # Validate lower range for max_models
        _Validators._validate_argument_range(max_models, "max_models", lbound=1, lbound_inclusive=True)
        
        custom_data = None
        self.auto = True
        # Validate custom file
        if custom_config_file:
            # Performing validation
            _Validators._validate_file_exists(custom_config_file)
            _Validators._validate_file_extension(custom_config_file, "json")
            _Validators._check_empty_file(custom_config_file)
            # Setting auto to False
            self.auto = False
            # Loading file
            with open(custom_config_file, 'r') as json_file:
                custom_data = json.load(json_file)

        # Initializing class variables
        self.data = None
        self.target_column = None
        self.custom_data = custom_data
        self.task_type = task_type
        self.include_model = include
        self.exclude_model = exclude
        self.verbose = verbose
        self.max_runtime_secs = max_runtime_secs
        self.stopping_metric = stopping_metric
        self.stopping_tolerance = stopping_tolerance
        self.max_models = max_models
        self.model_list = ['decision_forest', 'xgboost', 'knn', 'svm', 'glm']
        self.is_classification_type = lambda: self.task_type.upper() == 'CLASSIFICATION'
        self._is_fit_called = False 
        self._is_load_model_called = False
        self.kwargs = kwargs
        self.table_name_mapping={}
        
    @collect_queryband(queryband="AutoML_fit")    
    def fit(self,
            data,
            target_column):
        """
        DESCRIPTION:
            Function triggers the AutoML run. It is designed to handle both 
            regression and classification tasks depending on the specified "task_type".
            
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies target column of dataset.
                Types: str or ColumnExpression

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError
            
        EXAMPLES:
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".

            # Example 1: Passing column expression for target column.
            >>> automl_obj.fit(data = housing_train, target_col = housing_train.price)
                                    
            # Example 2: Passing name of target column.
            >>> automl_obj.fit(data = housing_train, target_col = "price") 
        """

        self._is_fit_called = True
        # Checking if target column is of type ColumnExpression
        if isinstance(target_column, ColumnExpression):
            target_column = target_column.name
        
        # Appending fit arguments to list for validation
        arg_info_fit_matrix = []
        arg_info_fit_matrix.append(["data", data, False, (DataFrame), True])
        arg_info_fit_matrix.append(["target_column", target_column, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_fit_matrix)

        # Initializing class variables
        self.data = data
        self.target_column = target_column
        
        # Checking if include model list is present
        if self.include_model:
            # Converting to list if passed as string
            self.include_model = UtilFuncs._as_list(self.include_model)
            # Updating model list based on include list
            self.model_list = list(set(self.include_model))
            self.model_list = [model.lower() for model in self.model_list]

        # Checking if exclude model list is present
        if self.exclude_model:
            # Converting to list if passed as string
            self.exclude_model = UtilFuncs._as_list(self.exclude_model)
            # Updating model list based on exclude list
            self.model_list = list(set(self.model_list) - set(self.exclude_model))
            self.model_list = [model.lower() for model in self.model_list]
        
        # Checking if target column is present in data
        _Validators._validate_dataframe_has_argument_columns(self.target_column, "target_column", self.data, "df")
            
        # Handling default task type        
        if self.task_type.casefold() == "default":
            # if target column is having distinct values less than or equal to 20, 
            # then it will be mapped to classification problem else regression problem
            if self.data.drop_duplicate(self.target_column).size <= 20:
                print("\nTask type is set to Classification as target column "
                    "is having distinct values less than or equal to 20.")
                self.task_type = "Classification"
            else:
                print("\nTask type is set to Regression as target column is "
                    "having distinct values greater than 20.")
                self.task_type = "Regression"
        
        if self.is_classification_type():
            if self.stopping_metric is not None:
                permitted_values = ["MICRO-F1", "MACRO-F1", 
                                    "MICRO-RECALL", "MACRO-RECALL",
                                    "MICRO-PRECISION", "MACRO-PRECISION", 
                                    "WEIGHTED-PRECISION", "WEIGHTED-RECALL", 
                                    "WEIGHTED-F1", "ACCURACY"]
                _Validators._validate_permitted_values(self.stopping_metric, permitted_values, "stopping_metric")
        else:
            if self.stopping_metric is not None:
                permitted_values = ["R2", "MAE", "MSE", "MSLE",
                                    "MAPE", "MPE", "RMSE", "RMSLE",
                                    "ME", "EV", "MPD", "MGD"]
                _Validators._validate_permitted_values(self.stopping_metric, permitted_values, "stopping_metric")

        if not self.is_classification_type():
            _Validators._validate_column_type(self.data, self.target_column, 'target_column', 
                                              expected_types=UtilFuncs()._get_numeric_datatypes())
        
        # Displaying received custom input
        if self.custom_data:
            print("\nReceived below input for customization : ")
            print(json.dumps(self.custom_data, indent=4))
        
        # Classification probelm
        task_cls = _Classification
        cls_method = "_classification"
        
        # Regression problem
        if self.task_type.casefold() == "regression":
            task_cls = _Regression
            cls_method = "_regression"

        # Running AutoML
        clf = task_cls(self.data, self.target_column, self.custom_data)
        
        self.model_info, self.leader_board, self.target_count, self.target_label, \
            self.data_transformation_params, self.table_name_mapping = getattr(clf, cls_method)(
                                                                       model_list = self.model_list,
                                                                       auto = self.auto,
                                                                       verbose = self.verbose,
                                                                       max_runtime_secs = self.max_runtime_secs, 
                                                                       stopping_metric = self.stopping_metric, 
                                                                       stopping_tolerance = self.stopping_tolerance,
                                                                       max_models = self.max_models,
                                                                       **self.kwargs)

        # Model Evaluation Phase
        self.m_evaluator = _ModelEvaluator(self.model_info, 
                                           self.target_column,
                                           self.task_type)
      
    @collect_queryband(queryband="AutoML_predict")
    def predict(self,
                data,
                rank = 1,
                use_loaded_models = False):
        """
        DESCRIPTION:
            Function generates prediction on data using model rank in 
            leaderboard.
            Note:
                * If both fit and load method are called before predict, then fit method model will be used
                  for prediction by default unless 'use_loaded_models' is set to True in predict.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the dataset on which prediction needs to be generated 
                using model rank in leaderboard.
                Types: teradataml DataFrame

            rank:
                Optional Argument.
                Specifies the rank of the model in the leaderboard to be used for prediction.
                Default Value: 1
                Types: int
            
            use_loaded_models:
                Optional Argument.
                Specifies whether to use loaded models from database for prediction or not.
                Default Value: False
                Types: bool
                
        RETURNS:
            Pandas DataFrame with predictions.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".
            # Perform predict() operation on the "automl_obj".
            
            # Example 1: Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(admissions_test)
            >>> prediction
            
            # Example 2: Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(admissions_test, rank=2)
            >>> prediction

            # Example 3: Run predict on test data using loaded model.
            >>> automl_obj.load("model_table")
            >>> prediction = automl_obj.predict(admissions_test, rank=3)
            >>> prediction

            # Example 4: Run predict on test data using loaded model when fit is also called.
            >>> automl_obj.fit(admissions_train, "admitted")
            >>> automl_obj.load("model_table")
            >>> prediction = automl_obj.predict(admissions_test, rank=3, use_loaded_models=True)
            >>> prediction
        """
        # Checking if fit or load model is called before predict, If not raise error
        if not self._is_fit_called and not self._is_load_model_called:
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'predict' method", \
                                       "'fit' or 'load' method must be called before" \
                                       " running predict.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)

        # Appending predict arguments to list for validation.
        arg_info_pred_matrix = []
        arg_info_pred_matrix.append(["data", data, False, (DataFrame), True])
        arg_info_pred_matrix.append(["rank", rank, True, (int), True])
        arg_info_pred_matrix.append(["use_loaded_models", use_loaded_models, True, (bool)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_pred_matrix)

        # Run predict using loaded model
        if self._is_load_model_called and (not self._is_fit_called or use_loaded_models):
            # Validate range for model rank
            _Validators._validate_argument_range(rank, "rank", lbound=1, 
                                                 ubound=self.loaded_models_info.RANK.max(),
                                                 lbound_inclusive=True, ubound_inclusive=True)
            return self._run_loaded_model(data, rank)
        
        # Validate range for model rank
        _Validators._validate_argument_range(rank, "rank", lbound=1, 
                                             ubound=self.leader_board.RANK.max(),
                                             lbound_inclusive=True, ubound_inclusive=True)
        
        # Setting target column indicator to default value, i.e., True.
        self.target_column_ind = True
        # Model Evaluation using rank-1 [rank starts from 0 in leaderboard]
        rank = rank-1

        # Setting indicator to False if target column doesn't exist
        if self.target_column not in data.columns:
            self.target_column_ind = False
        
        # Checking if data is already transformed before or not
        data_node_id = data._nodeid
        if not self.table_name_mapping.get(data_node_id):
            # At first data transformation will be performed on raw test data
            # then evaluation will happen.
            self.transform_data(data)
        else:
            print("\nSkipping data transformation as data is already transformed.")
    
        # Generating prediction
        pred = self.m_evaluator.model_evaluation(rank = rank, 
                                                 table_name_mapping = self.table_name_mapping,
                                                 data_node_id = data_node_id,
                                                 target_column_ind = self.target_column_ind)
            
        # Checking if problem type is classification and target label is present.
        if self.is_classification_type() and self.target_label is not None:
            # Displaying target column labels
            tar_dct = {}
            print('\nTarget Column Mapping:')
            # Iterating rows
            for row in self.target_label.result.itertuples():
                # Retrieving the category names of encoded target column
                # row[1] contains the orginal name of cateogry
                # row[2] contains the encoded value
                if row[1] != 'TD_CATEGORY_COUNT':
                    tar_dct[row[1]] = row[2]
                    
            for key, value in tar_dct.items():
                print(f"{key}: {value}")

        # Renaming probability column if any
        prob_lst = [item for item in pred.result.columns if item.startswith('Prob_')]
        if len(prob_lst) > 0:
            rename_dict ={}
            for col in pred.result.columns:
                if col not in prob_lst:
                    rename_dict[col] = getattr(pred.result, col)
                else:
                    indx = int(col.split('_')[1])
                    rename_dict[f'prob_{indx}'] = getattr(pred.result, f'Prob_{indx}')
            rename_dict['drop_columns'] = True
            pred.result = pred.result.assign(**rename_dict)              

        print("\nPrediction : ")
        print(pred.result)
        
        if self.target_column_ind:
            prediction_column = 'prediction' if 'prediction' in pred.result.columns else 'Prediction'
            probability_column = 'prob_1'
            pred_target_count = pred.result.drop_duplicate(self.target_column).size
            # Displaying confusion matrix and ROC-AUC for classification problem
            if self.is_classification_type():
                print_data = lambda data: print(data) if _is_terminal() else display(data)
                # Displaying ROC-AUC for binary classification
                if self.target_count == 2 and pred_target_count == 2:
                    fit_params = {
                        "probability_column" : probability_column,
                        "observation_column" : self.target_column,
                        "positive_class" : "1",
                        "data" : pred.result
                    }
                    # Fitting ROC
                    roc_out = ROC(**fit_params)
                    print("\nROC-AUC : ")
                    print_data(roc_out.result)
                    print_data(roc_out.output_data)
                
                # Displaying confusion matrix for binary and multiclass classification
                prediction_df=pred.result.to_pandas()
                target_col = self.target_column
                print("\nConfusion Matrix : ")
                print_data(confusion_matrix(prediction_df[target_col], prediction_df[prediction_column]))
                
        # Returning prediction
        return pred.result
    
    @collect_queryband(queryband="AutoML_evaluate")  
    def evaluate(self,
                 data,
                 rank = 1,
                 use_loaded_models = False
                 ):
        """
        DESCRIPTION:
            Function evaluates on data using model rank in leaderboard
            and generates performance metrics.
            Note:
                * If both fit and load method are called before predict, then fit method model will be used
                  for prediction by default unless 'use_loaded_models' is set to True in predict.
            
        PARAMETERS:
            data:
                Required Argument.
                Specifies the dataset on which performance metrics needs to be generated.
                Types: teradataml DataFrame
                
                Note:
                    * Target column used for generating model is mandatory in "data" for evaluation.

            rank:
                Optional Argument.
                Specifies the rank of the model available in the leaderboard to be used for evaluation.
                Default Value: 1
                Types: int

            use_loaded_models:
                Optional Argument.
                Specifies whether to use loaded models from database for prediction or not.
                Default Value: False
                Types: bool

        RETURNS:
            Pandas DataFrame with performance metrics.
        
        RAISES:
            TeradataMlException.
        
        EXAMPLES:
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".
            # Perform evaluate() operation on the "automl_obj".
            
            # Example 1: Run evaluate on test data using best performing model.
            >>> performance_metrics = automl_obj.evaluate(admissions_test)
            >>> performance_metrics
            
            # Example 2: Run evaluate on test data using second best performing model.
            >>> performance_metrics = automl_obj.evaluate(admissions_test, rank=2)
            >>> performance_metrics

            # Example 3: Run evaluate on test data using loaded model.
            >>> automl_obj.load("model_table")
            >>> evaluation = automl_obj.evaluate(admissions_test, rank=3)
            >>> evaluation

            # Example 4: Run predict on test data using loaded model when fit is also called.
            >>> automl_obj.fit(admissions_train, "admitted")
            >>> automl_obj.load("model_table")
            >>> evaluation = automl_obj.evaluate(admissions_test, rank=3, use_loaded_models=True)
            >>> evaluation
        """
        if not self._is_fit_called and not self._is_load_model_called:
            # raise ValueError("fit() method must be called before evaluating.")
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'evaluate' method", \
                                       "'fit' or 'load' method must be called before" \
                                       " running evaluate.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        # Appending evaluate arguments to list for validation.
        arg_info_pred_matrix = []
        arg_info_pred_matrix.append(["data", data, False, (DataFrame), True])
        arg_info_pred_matrix.append(["rank", rank, True, (int), True])
        arg_info_pred_matrix.append(["use_loaded_models", use_loaded_models, True, (bool)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_pred_matrix)

        # Run evaluate using loaded model
        if self._is_load_model_called and (not self._is_fit_called or use_loaded_models):
            # Validate range for model rank
            _Validators._validate_argument_range(rank, "rank", lbound=1, 
                                                 ubound=self.loaded_models_info.RANK.max(),
                                                 lbound_inclusive=True, ubound_inclusive=True)
            return self._run_loaded_model(data, rank, output_type="evaluate")

        # Validate range for model rank
        _Validators._validate_argument_range(rank, "rank", lbound=1, 
                                             ubound=self.leader_board.RANK.max(),
                                             lbound_inclusive=True, ubound_inclusive=True)

        # Model Evaluation using rank-1 [rank starts from 0 in leaderboard]
        rank = rank-1

        # Raising exception if target column is not present in data
        # as it is required for evaluation.
        if self.target_column not in data.columns:
             raise TeradataMlException(
                 Messages.get_message(MessageCodes.TARGET_COL_NOT_FOUND_FOR_EVALUATE).format(self.target_column),
                 MessageCodes.TARGET_COL_NOT_FOUND_FOR_EVALUATE)
        
        # Checking if data is already transformed before or not
        data_node_id = data._nodeid
        if not self.table_name_mapping.get(data_node_id):
            # At first data transformation will be performed on raw test data
            # then evaluation will happen.
            self.transform_data(data)
        else:
            print("\nSkipping data transformation as data is already transformed.")

        metrics = self.m_evaluator.model_evaluation(rank = rank,  
                                                    table_name_mapping=self.table_name_mapping,
                                                    data_node_id = data_node_id,
                                                    get_metrics = True)

        # Checking if problem type is classification and target label is present.
        if self.is_classification_type() and self.target_label is not None:
            # Displaying target column labels
            tar_dct = {}
            print('\nTarget Column Mapping:')
            # Iterating rows
            for row in self.target_label.result.itertuples():
                # Retrieving the category names of encoded target column
                # row[1] contains the orginal name of cateogry
                # row[2] contains the encoded value
                if row[1] != 'TD_CATEGORY_COUNT':
                    tar_dct[row[1]] = row[2]
                    
            for key, value in tar_dct.items():
                print(f"{key}: {value}")
        
        # Showing performance metrics
        print("\nPerformance Metrics : ")
        print(metrics.result)
        if self.is_classification_type():
            print("-"*80)
            print(metrics.output_data)
        
        # Returning performance metrics
        return metrics.result
    
    def transform_data(self,
                       data,
                       data_params = None,
                       auto = None,
                       verbose = None,
                       target_column_ind = None):
        """
        DESCRIPTION:
            Function transforms the data based on the data transformation parameters
            generated during the fit phase.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the dataset to be transformed.
                Types: teradataml DataFrame
            
            data_params:
                Optional Argument.
                Specifies the data transformation parameters.
                Default Value: None
                Types: dict
            
            auto:
                Optional Argument.
                Specifies whether to AutoML ran in auto or custom mode.
                Default Value: None
                Types: bool

            verbose:
                Optional Argument.
                Specifies the verbosity level.
                Default Value: None
                Types: int
        
            target_column_ind:
                Optional Argument.
                Specifies whether target column is present in data or not.
                Default Value: None
                Types: bool

        RETURNS:
            None
        """
        # Creating instance of DataTransformation
        data_transform_instance = _DataTransformation(data = data,
                                                      data_transformation_params=data_params if data_params is not None else \
                                                                                 self.data_transformation_params,
                                                      auto=auto if data_params is not None else self.auto,
                                                      verbose=verbose if verbose is not None else self.verbose,
                                                      target_column_ind=target_column_ind if target_column_ind is not None else \
                                                                        self.target_column_ind,
                                                      table_name_mapping=self.table_name_mapping)
        
        # Storing mapping of table names for transformed data
        self.table_name_mapping = data_transform_instance.data_transformation()
    
    @collect_queryband(queryband="AutoML_leaderboard")
    def leaderboard(self):
        """
        DESCRIPTION:
            Function displays leaderboard.

        RETURNS:
            Pandas DataFrame with Leaderboard information.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".
            # Generate leaderboard using leaderboard() method on "automl_obj".
            >>> automl_obj.leaderboard()
        """
        if not self._is_fit_called:
            # raise ValueError("fit() method must be called before generating leaderboard.")
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'leaderboard' method", \
                                       "'fit' method must be called before" \
                                       " generating leaderboard.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        return self.leader_board
        
    @collect_queryband(queryband="AutoML_leader")    
    def leader(self):
        """
        DESCRIPTION:
            Function displays best performing model.
            
        RETURNS:
            None

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".
            # Generate leaderboard using leaderboard() method on "automl_obj".
            # Display best performing model using leader() method on "automl_obj".
            >>> automl_obj.leader()   
        """
        if not self._is_fit_called:
            # raise ValueError("fit() method must be called before generating leader.")
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'leader' method", \
                                       "'fit' method must be called before" \
                                       " generating leader.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        record = self.leader_board
        if not _is_terminal():
            display(record[record['RANK'] == 1])
        else:
            print(record[record['RANK'] == 1])

    @collect_queryband(queryband="AutoML_hyperparameter")
    def model_hyperparameters(self,
                              rank=1, 
                              use_loaded_models=False):
        """
        DESCRIPTION:
            Get hyperparameters of the model based on rank in leaderboard.
            Note:
                * If both the fit() and load() methods are invoked before calling model_hyperparameters(), 
                  by default hyperparameters are retrieved from the fit leaderboard. 
                  To retrieve hyperparameters from the loaded models, set "use_loaded_models" to True in the model_hyperparameters call.

        PARAMETERS:
            rank:
                Required Argument.
                Specifies the rank of the model in the leaderboard.
                Default Value: 1
                Types: int

            use_loaded_models:
                Optional Argument.
                Specifies whether to use loaded models from database to get hyperparameters or not.
                Default Value: False
                Types: bool

        RETURNS:
            Dictionary, containing hyperparameters.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Get hyperparameters of the model using fit models.
            # Create an instance of the AutoML called "automl_obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Perform fit() operation on the "automl_obj".
            # Get hyperparameters of the model using model_hyperparameters() method on "automl_obj".
            >>> automl_obj = AutoML(task_type="Classification")
            >>> automl_obj.fit(admissions_train, "admitted")
            >>> automl_obj.model_hyperparameters(rank=1)

            # Example 2: Get hyperparameters of the model using loaded models.
            # Create an instance of the AutoML called "automl_obj"
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Load models from the specified table.
            # Get hyperparameters of the model using model_hyperparameters() method on "automl_obj".
            >>> automl_obj = AutoML()
            >>> automl_obj.load("model_table")
            >>> automl_obj.model_hyperparameters(rank=1)

            # Example 3: Get hyperparameters of the model when both fit and load method are called.
            # Create an instance of the AutoML called "automl_obj"
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            # Fit the data.
            # Load models from the specified table.
            # Get hyperparameters of the model using model_hyperparameters() method on "automl_obj".
            >>> automl_obj = AutoML(task_type="Classification")
            >>> automl_obj.fit(admissions_train, "admitted")
            >>> automl_obj.load("model_table")

            # Get hyperparameters of the model using loaded models.
            >>> automl_obj.model_hyperparameters(rank=1, use_loaded_models=True)
            # Get hyperparameters of the model using fit models.
            >>> automl_obj.model_hyperparameters(rank=1)
        """

        if not self._is_fit_called and not self._is_load_model_called:
            # raise ValueError("fit() or load() method must be called before getting hyperparameters.")
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'model_hyperparameters' method",
                                       "No models available to get hyperparameters. " \
                                       "Run 'fit()' or 'load()' methods to get models.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        
        arg_info_matrix = []
        arg_info_matrix.append(["rank", rank, True, (int), True])
        arg_info_matrix.append(["use_loaded_models", use_loaded_models, True, (bool)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        leaderboard = None
        if self._is_load_model_called and (not self._is_fit_called or use_loaded_models):
            leaderboard = self.loaded_models_info
        else:
            leaderboard = self.model_info

        # Validate range for model rank from loaded models
        _Validators._validate_argument_range(rank, "rank", lbound=1, 
                                             ubound=leaderboard.RANK.max(),
                                             lbound_inclusive=True, ubound_inclusive=True)
        hyperparams = leaderboard.loc[leaderboard['RANK'] == rank, 'PARAMETERS'].values[0]

        # Deserializing hyperparameters
        hyperparams = ast.literal_eval(hyperparams)

        # Removing 'data' from hyperparameters
        keys_to_remove = ['input_columns', 'data', 'train_data', 'test_data']
        for key in keys_to_remove:
            hyperparams.pop(key, None)

        return hyperparams
    
    @collect_queryband(queryband="AutoML_load")
    def load(self,
             table_name):
        """
        DESCRIPTION:
            Function loads models information from the specified table.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name from which models are to be loaded.
                Types: str

        RETURNS:
            Pandas DataFrame with loaded models information.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the AutoML called "obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            >>> obj = AutoML()
            # Load models from the specified table.
            >>> tab = obj.load("model_table")
        """
        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, True, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        # Loading models
        self.loaded_models_info = DataFrame(table_name).to_pandas()

        self._load_data_transform_params()

        self._is_load_model_called = True

        return self.loaded_models_info.drop(['RESULT_TABLE', 'PARAMETERS'], axis=1)
    
    def _load_data_transform_params(self):
        """
        DESCRIPTION:
            Internal Function loads data transformation parameters from the specified table.
        """
        from sklearn.decomposition import PCA

        # Getting data transformation row
        data_transform_row = self.loaded_models_info[self.loaded_models_info['RANK'] == -1].iloc[0]

        # Removing data transformation row and dropping 'DATA_PARAMS' column
        # from loaded models info
        self.loaded_models_info = self.loaded_models_info[self.loaded_models_info['RANK'] != -1]
        self.loaded_models_info.drop('DATA_PARAMS', axis=1, inplace=True)

        # Loading data transformation parameters by deserializing
        buffer = BytesIO(data_transform_row['DATA_PARAMS'])
        data_params = joblib.load(buffer)

        fit_obj_lst = json.loads(data_transform_row['PARAMETERS'])

        # Generating Dataframe from table_names in data params
        # fit_obj_lst contain : ['one_hot_encoding_fit_obj', 'lasso_scale_fit_obj', 'pca_scale_fit_obj', imputation_fit_object]
        # Iterating over fit_obj_lst and converting table names to DataFrame
        for fit_obj_name in fit_obj_lst:
            if isinstance(data_params[fit_obj_name], dict):
                for key, val in data_params[fit_obj_name].items():
                    # Key: automl transformation step name, val: table name
                    data_params[fit_obj_name][key] = DataFrame(f'{val}')
            else:
                data_params[fit_obj_name] = DataFrame(f'{data_params[fit_obj_name]}')
        
        # Manually deserializing and reconstructing PCA object
        load_pca_info = data_params['pca_fit_instance']
        pca = PCA(n_components=load_pca_info['n_components'], random_state=42)
        pca.components_ = np.array(load_pca_info['components'])
        pca.explained_variance_ = np.array(load_pca_info['explained_variance'])
        pca.explained_variance_ratio_ = np.array(load_pca_info['explained_variance_ratio'])
        pca.mean_ = np.array(load_pca_info['mean'])
        pca.n_components_ = load_pca_info['n_components']
        pca.noise_variance_ = load_pca_info['noise_variance']
        pca.singular_values_ = np.array(load_pca_info['singular_values'])
        pca.feature_names_in_ = data_params['pca_fit_columns']
        pca.n_features_in_ = len(data_params['pca_fit_columns'])

        data_params['pca_fit_instance'] = pca

        self.loaded_data_transformation_params = data_params
    
    def _validate_ranks(self, ranks):
        """
        DESCRIPTION:
            Function validates the ranks argument.

        PARAMETERS:
            ranks:
                Required Argument.
                Specifies the ranks for the models to be saved.
                Types: int or list of int

        RAISES:
            TeradataMlException.
        """
        start_rank, end_rank = ranks.start, ranks.stop

        # Check if both parts are non-negative integers
        if not (start_rank > 0 and end_rank > 0):
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'deploy' method", \
                                       "Provided start and end rank in 'ranks' "\
                                       "must be positive non-zero integers.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)

        # Check if start_rank is less than or equal to end_rank
        if start_rank > end_rank:
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'deploy' method", \
                                       "Provided start rank in 'ranks' must be less than"\
                                       " or equal to end rank in 'ranks'.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        
        # check end rank is less than or equal to total models
        if end_rank > self.leader_board.RANK.max():
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                       "'deploy' method", \
                                       "Provided end rank in 'ranks' must be less than"\
                                       " or equal to total models available.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        
        return start_rank, end_rank
    
    @collect_queryband(queryband="AutoML_deploy")
    def deploy(self,
               table_name,
               top_n = 3,
               ranks = None
               ):
        """
        DESCRIPTION:
            Function saves models to the specified table name.
            Note:
                * If 'ranks' is provided, specified models in 'ranks' will be saved
                  and ranks will be reassigned to specified models based
                  on the order of the leaderboard, non-specified models will be ignored.
            
        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name to which models information is to be saved.
                Types: str

            top_n:
                Optional Argument.
                Specifies the top n models to be saved.
                Note:
                    * If 'ranks' is not provided, the function saves the top 'top_n' models.

                Default Value: 3
                Types: int
            
            ranks:
                Optional Argument.
                Specifies the ranks for the models to be saved.
                Note:
                    * If 'ranks' is provided, then 'top_n' is ignored.
                Types: int or list of int or range object
        
        RETURNS:
            None

        RAISES:
            TeradataMlException.
        
        EXAMPLES:
            # Create an instance of the AutoML called "obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            >>> obj = AutoML(task_type="Classification")
            >>> obj.fit(data = data, target_column = target_column)

            # Save top 3 models to the specified table.
            >>> obj.deploy("model_table")

            # Save top n models to the specified table.
            >>> obj.deploy("model_table", top_n=5)

            # Save models based on specified ranks to the specified table.
            >>> obj.deploy("model_table", ranks=[1, 3, 5])

            # Save models based on specified rank range to the specified table.
            >>> obj.deploy("model_table", ranks=range(2,6))
        """ 
        # raise Error if fit is not called
        if not self._is_fit_called:
            err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                    "'deploy' method", \
                                    "'fit' method must be called before" \
                                    " 'deploy'.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)

        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, True, (str), True])
        arg_info_matrix.append(["top_n", top_n, True, (int)])
        if not isinstance(ranks, range):
            arg_info_matrix.append(["ranks", ranks, True, (int, list)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        if isinstance(ranks, int):
            ranks = [ranks]
        elif isinstance(ranks, range):
            start_rank, end_rank = self._validate_ranks(ranks)

        if ranks is None or len(ranks) == 0:
            # If total models are greater than available models or less than 1
            try:
                _Validators._validate_argument_range(top_n, "top_n", lbound=1, 
                                                     ubound=self.leader_board.RANK.max(),
                                                     lbound_inclusive=True, ubound_inclusive=True)
            except ValueError as e:
                msg = "\n'top_n' should be equal or less than the available models or greater than 0. " \
                      "Deploying all available models to the table."
                warnings.warn(message=msg, stacklevel=2)
                top_n = self.leader_board.shape[0]
        elif isinstance(ranks, list):
            # If ranks is provided, then validating the ranks elements
            for ele in ranks:
                _Validators._validate_argument_range(ele, "element in ranks", lbound=1, 
                                                     ubound=self.leader_board.RANK.max(),
                                                     lbound_inclusive=True, ubound_inclusive=True)

        feature_selections = self.model_info['FEATURE_SELECTION'].unique().tolist()

        # Mapping feature selection to training data, 
        # we are creating a dictionary with key as feature selection and
        # value as temporary training data table name, so that we can copy
        # temporary training data to permanent table.
        # Here's an example of mapping:
        # Example: {'lasso': 'ml__survived_lasso_1717475362789542',
        #           'rfe': 'ml__survived_rfe_1717474570567062',
        #           'pca': 'ml__survived_pca_1717475375119752'}
        fs_to_data_dict ={fs:self.model_info.loc[self.model_info['FEATURE_SELECTION'] == fs, \
                                                'DATA_TABLE'].iloc[0] for fs in feature_selections}

        # Saving temporary training data to permanent table
        # We are replacing DATA_TABLE with permanent table name in model_info
        for key, val in fs_to_data_dict.items():
            per_name = self._create_per_result_table(prefix='{}_{}'.format(self.target_column, key),
                                                     persist_result_table=val)
            fs_to_data_dict[key] = per_name

        # Persist flag
        persist = self.kwargs.get('persist', False)
        # If ranks is provided, then saving models based on specified rank
        # in list will be prioritized over 'top_n'.
        if ranks is None or len(ranks) == 0:
            # Saving only top 'top_n' models
            for index, row in self.model_info.iterrows():
                if index < top_n:
                    self.model_info.loc[index, 'DATA_TABLE'] = fs_to_data_dict[row['FEATURE_SELECTION']]
                    if not persist:
                        per_name = self._create_per_result_table(prefix='{}_{}'.format(self.target_column, row['MODEL_ID']),
                                                                 persist_result_table=row['RESULT_TABLE'])
                        self.model_info.loc[index, 'RESULT_TABLE'] = per_name
                else:
                    break
            sv_models = self.model_info.drop('model-obj', axis=1).head(top_n)
        else:
            if isinstance(ranks, range):
                # Saving models based on start and end rank.
                sv_models = self.model_info[start_rank-1:end_rank].copy()
            else:
                # Saving models based on specified rank in list
                sv_models = self.model_info[self.model_info['RANK'].isin(ranks)].copy()
            sv_models.drop('model-obj', axis=1, inplace=True)
            sv_models.reset_index(drop=True, inplace=True)

            for index, row in sv_models.iterrows():
                sv_models.loc[index, 'RANK'] = index + 1
                sv_models.loc[index, 'DATA_TABLE'] = fs_to_data_dict[row['FEATURE_SELECTION']]
                if not persist:
                    per_name = self._create_per_result_table(prefix='{}_{}'.format(self.target_column, row['MODEL_ID']),
                                                             persist_result_table=row['RESULT_TABLE'])
                    sv_models.loc[index, 'RESULT_TABLE'] = per_name  
        
        # Data Transformation Parameters
        df = self._deploy_data_transformation_params()

        # Saving data transformation parameters to the specified table
        sv_models = pd.concat([sv_models, df], ignore_index=True, sort=False)

        copy_to_sql(df = sv_models, table_name=table_name, if_exists='replace', types={'DATA_PARAMS':BLOB, 
                                                                                       'PARAMETERS':VARCHAR(length=32000, charset='UNICODE')})

        print('Model Deployment Completed Successfully.')

    def _create_per_result_table(self, prefix, persist_result_table):
        """
        DESCRIPTION:
            Internal Function creates permanent table for the specified result table.

        PARAMETERS:
            prefix:
                Required Argument.
                Specifies the prefix for the permanent table name.
                Types: str

            persist_result_table:
                Required Argument.
                Specifies the result table name.
                Types: str

        RETURNS:
            Permanent table name.
            
        RAISES:
            TeradataMlException.
        """

        table_name = UtilFuncs._generate_temp_table_name(prefix=prefix,
                                                       table_type=TeradataConstants.TERADATA_TABLE,
                                                       gc_on_quit=False)
        qry = f"SELECT * FROM {persist_result_table}"
        UtilFuncs._create_table(table_name=table_name, 
                                query=qry,
                                volatile=False)
        return table_name


    def _deploy_data_transformation_params(self):
        """
        DESCRIPTION:
            Internal Function converts data transformation parameters dictonary (information of each step of automl) 
            to DataFrame with rank as -1 and return the DataFrame that can be concatenated with model_info DataFrame
            and saved to the user specified table in database.
        
        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException.
        """
        # Create a new dictionary to store the deep copy
        data_params = {}

        # Define a recursive function to deep copy dictionaries
        def deep_copy_dict(d):
            if not isinstance(d, dict):
                return d  # Base case: if it's not a dictionary, return the value directly
            return {k: deep_copy_dict(v) for k, v in d.items()}  # Recursively copy each item
        
        # Deep copy is needed as the original dictionary contains nested dictionaries 
        # and we want to avoid modifying the original dictionary when changes are made.
        # The .copy() method creates a shallow copy, which does not suffice for nested dictionaries.
        # Iterate through the original dictionary to handle deep copying.
        for key, value in self.data_transformation_params.items():
            # Check if value is a dictionary
            if isinstance(value, dict):
                # If the value is a dictionary, create a deep copy of the dictionary
                # This ensures that nested dictionaries are also copied, not just referenced.
                data_params[key] = deep_copy_dict(value)
            else:
                # If the value is not a dictionary, perform a shallow copy (direct assignment)
                data_params[key] = value

        # Names of fit objects that contain the table names
        # pointing to tables in the database.
        fit_obj_names = []

        # Persist flag
        persist = self.kwargs.get('persist', False)

        data_params['auto_mode'] = False if self.custom_data is not None else True

        # Iterating over data transformation parameters
        # aml_step_name is the name of transformation step taken and val is the value
        for aml_step_name,val in data_params.items():
            # Checking if value is of type teradataml DataFrame
            # If yes, then creating permanent table for the same
            # and storing the table_name in data_params instead of dataframe.
            if isinstance(val, DataFrame):
                fit_obj_names.append(aml_step_name)
                if persist:
                    data_params[aml_step_name] = val._table_name
                else:
                    per_name = self._create_per_result_table(prefix='{}'.format(aml_step_name),
                                                             persist_result_table= val._table_name)
                    data_params[aml_step_name] = per_name
            elif isinstance(val, dict) and 'fit_obj' in aml_step_name:
                for key, val in val.items():
                    if isinstance(val, DataFrame):
                        fit_obj_names.append(aml_step_name)
                        if persist:
                            data_params[aml_step_name][key] = val._table_name
                        else:
                            per_name = self._create_per_result_table(prefix='{}'.format(key),
                                                                     persist_result_table= val._table_name)
                            data_params[aml_step_name][key] = per_name
            elif aml_step_name == 'pca_fit_instance':
                # Serializing PCA object
                pca = data_params[aml_step_name]
                # Extract pca parameters
                pca_params = {
                    'n_components': pca.n_components_,
                    'components': pca.components_.tolist(),
                    'explained_variance': pca.explained_variance_.tolist(),
                    'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                    'mean': pca.mean_.tolist(),
                    'singular_values': pca.singular_values_.tolist(),
                    'noise_variance': pca.noise_variance_
                }
                data_params[aml_step_name] = pca_params
        
        # Serializing data transformation parameters
        buffer = BytesIO()
        joblib.dump(data_params, buffer)
        buffer.seek(0)
        serialized_data = buffer.getvalue()

        # Creating a string representation of fit object names
        param = json.dumps(fit_obj_names)

        # Creating a DataFrame of data transformation information
        row = {
            'RANK':-1,
            'PARAMETERS':param,
            'DATA_PARAMS':serialized_data,
        }
        df = pd.DataFrame([row])

        return df
        
    def _run_loaded_model(self,
                          test_data,
                          rank=1,
                          output_type='prediction'):
        """
        DESCRIPTION:
            Internal Function generates prediction and performance metrics using the specified model rank
            in the loaded models leaderboard.

        PARAMETERS:
            test_data:
                Required Argument.
                Specifies the test data on which prediction and performance metrics needs to be generated.
                Types: teradataml DataFrame

            rank:
                Optional Argument.
                Specifies the rank of the model in the leaderboard to be used for prediction.
                Default Value: 1
                Types: int
            
            output_type:
                Optional Argument.
                Specifies the type of output to be generated.
                Default Value: 'prediction'
                Types: str
                Permitted Values: 'prediction', 'metrics'

        RETURNS:
            Tuple containing prediction and performance metrics.

        RAISES:
            TeradataMlException.

        """
        # Indexing starts from 0
        rank = rank - 1
        # Extracting parameters
        parameters = ast.literal_eval(self.loaded_models_info.loc[rank, 'PARAMETERS'])
        # Model name
        model_name = self.loaded_models_info.loc[rank, 'MODEL_ID'].split('_')[0]
        # Feature selection
        fs = self.loaded_models_info.loc[rank, 'FEATURE_SELECTION']
        
        # Checking task type
        if 'R2' in self.loaded_models_info.columns:
            task_type='Regression'
        else:
            task_type='Classification'

        # Model names mapping to Analytic Functions
        func_map = {
            'XGBOOST': lambda params: XGBoost(**params),
            'GLM': lambda params: GLM(**params),
            'SVM': lambda params: SVM(**params),
            'DECISIONFOREST': lambda params: DecisionForest(**params),
            'KNN': lambda params: KNN(**params)
        }

        if output_type == 'prediction':
            print('Generating prediction using:')
        else:
            print('Generating performance metrics using:')
        print(f"Model Name: {model_name}")
        print(f"Feature Selection: {fs}")

        # Generating evaluation parameters
        eval_params = _ModelTraining._eval_params_generation(model_name,
                                                             parameters['response_column'],
                                                             task_type)
        if task_type == 'Classification':
            eval_params['output_responses'] = parameters['output_responses']
        
        # Checking if response column is present in test data
        if parameters['response_column'] not in test_data.columns:
            # Checking if output type is evaluation
            if output_type == 'evaluation':
                # Response column is rqeuired for evaluation, raise error if not present
                raise ValueError(f"Response column '{parameters['response_column']}' is not present in test data for evaluation.")
            eval_params.pop('accumulate', None)
            reponse_col_present = False
        else:
            reponse_col_present = True

        # Checking if data is already transformed before or not
        data_node_id = test_data._nodeid
        if not self.table_name_mapping.get(data_node_id):
            # Data transformation will be performed on raw test data
            self.transform_data(data=test_data, 
                                data_params=self.loaded_data_transformation_params,
                                auto=self.loaded_data_transformation_params['auto_mode'],
                                verbose=0, 
                                target_column_ind=reponse_col_present)

        # Extracting test data
        for feature_selection, table_name in self.table_name_mapping[data_node_id].items():
            if fs in feature_selection:
                test_data = DataFrame(table_name)
                break
        
        if model_name == 'KNN':
            train_data = DataFrame(self.loaded_models_info.loc[rank, 'DATA_TABLE'])
            
            parameters['train_data'] = train_data
            parameters['test_data'] = test_data
            
            if parameters['response_column'] in test_data.columns:
                parameters['accumulate'] = parameters['response_column']

            knn = func_map[model_name](parameters)
  
            # Checking if response column is present in test data
            if reponse_col_present and output_type != 'prediction':
                metrics = knn.evaluate(test_data=test_data, **eval_params)
            else:
                predictions = knn.result
        else:
            # Extracting result table name
            result_table_name = self.loaded_models_info.loc[rank, 'RESULT_TABLE']
            result_table = DataFrame(result_table_name)
            params = {
                "skip_input_arg_processing":True,
                "skip_output_arg_processing":True,
                "skip_other_arg_processing":True,
                "skip_func_output_processing":True,
                "_result_data":result_table,
                "response_column": parameters['response_column']
            }
            model = func_map[model_name](params)
            # Checking if response column is present in test data
            if reponse_col_present and output_type != 'prediction':
                metrics = model.evaluate(newdata=test_data, **eval_params)
            else:
                predictions = model.predict(newdata=test_data, **eval_params)
        
        # Return prediction and metrics, when output type is metrics
        if reponse_col_present and output_type != 'prediction':
            return metrics
        
        # Return prediction, when output type is prediction
        return predictions if model_name == 'KNN' else predictions.result

    @collect_queryband(queryband="AutoML_remove_saved_models")
    def remove_saved_models(self,
                            table_name):
        """
        DESCRIPTION:
            Function removes the specified table containing saved models.
            Note:
                * If any data table result table is not present inside the database, 
                  then it will be skipped.
        
        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name containing saved models.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the AutoML called "obj" 
            # by referring "AutoML() or AutoRegressor() or AutoClassifier()" method.
            >>> obj = AutoML()
            # Remove saved models from the specified table.
            >>> obj.remove_saved_models("model_table")
        """
        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, True, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        df = DataFrame(table_name).to_pandas()

        drop_list = df['DATA_TABLE'].dropna().unique().tolist()
        drop_list.extend(df['RESULT_TABLE'].dropna().unique().tolist())

        # Removing data transformation parameters tables
        data=df[df['RANK'] == -1].iloc[0]
        buffer = BytesIO(data['DATA_PARAMS'])
        data_params = joblib.load(buffer)
        fit_obj_lst = json.loads(data['PARAMETERS'])
        for i in fit_obj_lst:
            if isinstance(data_params[i], dict):
                drop_list.extend(data_params[i].values())
            else:
                drop_list.append(data_params[i])
            
        non_existent_tables = []
        for table in drop_list:
            try:
                execute_sql(f"DROP TABLE {table};")
            except Exception as e:
                non_existent_tables.append(table)
                continue
        
        if len(non_existent_tables) > 0:
            warnings.warn(message=f"\nThe following tables '{non_existent_tables}' do not exist in the database and have been skipped.",
                          stacklevel=2)

        db_drop_table(table_name)
    
    @staticmethod
    def generate_custom_config(file_name = "custom"):
        """
        DESCRIPTION:
            Function generates custom JSON file containing user customized input under current 
            working directory which can be used for AutoML execution.
        
        PARAMETERS:
            file_name:
                Optional Argument.
                Specifies the name of the file to be generated. Do not pass the file name
                with extension. Extension '.json' is automatically added to specified file name.
                Default Value: "custom"
                Types: str
        
        RETURNS:
            None 
        
        EXAMPLES:
            # Import either of AutoML or AutoClassifier or AutoRegressor from teradataml.
            # As per requirement, generate json file using generate_custom_config() method.
            
            # Generate a default file named "custom.json" file using either of below options.
            >>> AutoML.generate_custom_config()
            or
            >>> AutoClassifier.generate_custom_config()
            or 
            >>> AutoRegressor.generate_custom_config()
            # The above code will generate "custom.json" file under the current working directory.
            
            # Generate different file name using "file_name" argument.
            >>> AutoML.generate_custom_config("titanic_custom")
            or
            >>> AutoClassifier.generate_custom_config("titanic_custom")
            or
            >>> AutoRegressor.generate_custom_config("housing_custom")
            # The above code will generate "titanic_custom.json" file under the current working directory.
                
        """
        # Intializing class
        generator = _GenerateCustomJson()
        # Generating custom JSON data
        data = generator._generate_custom_json()
        # Converting to JSON
        custom_json = json.dumps(data, indent=4)
        # Save JSON data to the specified file
        json_file = f"{file_name}.json"
        with open(json_file, 'w') as file:
            file.write(custom_json)
        print(f"\n'{json_file}' file is generated successfully under the current working directory.")


class _Regression(_FeatureExplore, _FeatureEngineering, _DataPreparation, _ModelTraining):
  
    def __init__(self, 
                 data, 
                 target_column,
                 custom_data = None):
        """
        DESCRIPTION:
            Function initializes the data, target column for Regression.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml Dataframe.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str
            
            custom_data:
                Optional Argument.
                Specifies json object containing user customized input.
                Types: json object
        """
        self.data = data
        self.target_column = target_column
        self.custom_data = custom_data
        
        
    def _regression(self,
                    model_list = None, 
                    auto = False,
                    verbose = 0,
                    max_runtime_secs = None,
                    stopping_metric = None, 
                    stopping_tolerance = None,
                    max_models = None,
                    **kwargs):
        """
        DESCRIPTION:
            Interal Function runs Regression.
         
        PARAMETERS:  
            auto:
                Optional Argument.
                Specifies whether to run AutoML in custom mode or auto mode.
                When set to False, runs in custom mode. Otherwise, by default runs in auto mode.
                Types: bool
                
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
                
            max_runtime_secs:
                Optional Argument.
                Specifies the time limit in seconds for model training.
                Types: int
                
            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
                Specifies the stopping mertics for stopping tolerance in model training.
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
                Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
            
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int
        
            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool    
            
            seed:
                Optional Argument.
                Specifies the random seed for reproducibility.
                Default Value: 42
                Types: int
            
        RETURNS:
            a tuple containing, model information and leaderboard.   
        """
        # Feature Exploration Phase
        _FeatureExplore.__init__(self, 
                                 data = self.data, 
                                 target_column = self.target_column,
                                 verbose=verbose)
        if verbose > 0:
            self._exploration()
        # Feature Engineering Phase
        _FeatureEngineering.__init__(self, 
                                     data = self.data, 
                                     target_column = self.target_column,
                                     model_list = model_list,
                                     verbose = verbose,
                                     custom_data = self.custom_data,
                                     **kwargs)
        # Start time
        start_time = time.time()
        data, excluded_columns, target_label, data_transformation_params = self.feature_engineering(auto)
        
        # Data preparation Phase
        _DataPreparation.__init__(self, 
                                  data = self.data, 
                                  target_column = self.target_column, 
                                  verbose = verbose,
                                  excluded_columns = excluded_columns,
                                  custom_data = self.custom_data,
                                  data_transform_dict = data_transformation_params,
                                  **kwargs)
        features, data_transformation_params = self.data_preparation(auto)

        # Calculating max_runtime_secs for model training by,
        # subtracting the time taken for feature engineering and data preparation
        max_runtime_secs = max_runtime_secs - (time.time() - start_time) \
                                if max_runtime_secs is not None else None
        
        # Setting max_runtime_secs to 60 seconds if it is less than 0
        max_runtime_secs = 60 if max_runtime_secs is not None and \
                                            max_runtime_secs < 0 else max_runtime_secs
        
        # Model Training
        _ModelTraining.__init__(self, 
                                data = self.data, 
                                target_column = self.target_column,
                                model_list = model_list, 
                                verbose = verbose,
                                features = features,
                                task_type = "Regression",
                                custom_data = self.custom_data,
                                **kwargs)
        models_info, leaderboard, target_count = self.model_training(auto = auto,
                                                        max_runtime_secs = max_runtime_secs, 
                                                        stopping_metric = stopping_metric, 
                                                        stopping_tolerance = stopping_tolerance,
                                                        max_models = max_models)

        return (models_info, leaderboard, target_count, target_label, data_transformation_params, self.table_name_mapping)
            
class _Classification(_FeatureExplore, _FeatureEngineering, _DataPreparation, _ModelTraining):

    def __init__(self, 
                 data, 
                 target_column,
                 custom_data = None):
        """
        DESCRIPTION:
            Function initializes the data, target column for Classification.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml Dataframe.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str
            
            custom_data:
                Optional Argument.
                Specifies json object containing user customized input.
                Types: json object
        """
        self.data = data
        self.target_column = target_column
        self.custom_data = custom_data

    def _classification(self,
                        model_list = None,
                        auto = False,
                        verbose = 0,
                        max_runtime_secs = None,
                        stopping_metric = None, 
                        stopping_tolerance = None,
                        max_models = None,
                        **kwargs):
        """
        DESCRIPTION:
            Interal Function runs Classification.
         
        PARAMETERS:  
            auto:
                Optional Argument.
                Specifies whether to run AutoML in custom mode or auto mode.
                When set to False, runs in custom mode. Otherwise, by default runs in auto mode.
                Types: bool
                
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
                
            max_runtime_secs:
                Optional Argument.
                Specifies the time limit in seconds for model training.
                Types: int
                
            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
	            Specifies the stopping mertics for stopping tolerance in model training.
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
	            Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
            
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool
            
            seed:
                Optional Argument.
                Specifies the random seed for reproducibility.
                Default Value: 42
                Types: int

        RETURNS:
            a tuple containing, model information and leaderboard.
        """

        # Feature Exploration Phase
        _FeatureExplore.__init__(self, 
                                     data = self.data, 
                                     target_column = self.target_column,
                                     verbose=verbose)
        if verbose > 0:
            self._exploration()
        # Feature Engineeting Phase
        _FeatureEngineering.__init__(self, 
                                     data = self.data, 
                                     target_column = self.target_column,
                                     model_list = model_list,
                                     verbose = verbose,
                                     task_type = "Classification",
                                     custom_data = self.custom_data,
                                     **kwargs)
        # Start time
        start_time = time.time()
        data, excluded_columns, target_label, data_transformation_params = self.feature_engineering(auto)
        # Data Preparation Phase
        _DataPreparation.__init__(self, 
                                  data = self.data, 
                                  target_column = self.target_column, 
                                  verbose = verbose,
                                  excluded_columns = excluded_columns, 
                                  custom_data = self.custom_data,
                                  data_transform_dict = data_transformation_params,
                                  task_type = "Classification",
                                  **kwargs)
        features, data_transformation_params = self.data_preparation(auto)

        # Calculating max_runtime_secs for model training by,
        # subtracting the time taken for feature engineering and data preparation
        max_runtime_secs = max_runtime_secs - (time.time() - start_time) \
                                if max_runtime_secs is not None else None
        
        # Setting max_runtime_secs to 60 seconds if it is less than 0
        max_runtime_secs = 60 if max_runtime_secs is not None and \
                                            max_runtime_secs < 0 else max_runtime_secs

        # Model training
        _ModelTraining.__init__(self, 
                                data = self.data, 
                                target_column = self.target_column,
                                model_list = model_list, 
                                verbose = verbose,
                                features = features, 
                                task_type = "Classification",
                                custom_data = self.custom_data,
                                **kwargs)
        models_info, leaderboard, target_count = self.model_training(auto = auto,
                                                        max_runtime_secs = max_runtime_secs, 
                                                        stopping_metric = stopping_metric, 
                                                        stopping_tolerance = stopping_tolerance,
                                                        max_models = max_models)

        return (models_info, leaderboard, target_count, target_label, data_transformation_params, self.table_name_mapping)
  
    def _target_column_details(self): 
        """
        DESCRIPTION:
            Internal function displays the target column distribution of Target column/ Response column.
        """       
        # If data visualization libraries are available
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns
            self._display_msg(msg='\nTarget Column Distribution:',
                              show_data=True)
            plt.figure(figsize=(6, 6))
            # Ploting a histogram for target column
            sns.countplot(data=self.data.select([self.target_column]).to_pandas(), x=self.target_column)
            plt.show()

    def _check_data_imbalance(self, 
                              data=None):
        """
        DESCRIPTION:
            Internal function calculate and checks the imbalance in dataset.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: teradataml Dataframe
        
        RETURNS:
            bool, True if imbalance dataset detected, Otherwise False.
        """
        self._display_msg(msg="\nChecking imbalance data ...",
                          progress_bar=self.progress_bar)
        # Calculate the distribution of classes in the target column
        class_dist = data[self.target_column].value_counts().values

        # Find the minimum count of data points among the classes
        min_ct = np.min(class_dist)

        # Find the maximum count of data points among the classes
        max_ct = np.max(class_dist)

        # Calculate the imbalance ratio(minimum count to maximum count)
        imb_ratio = min_ct / max_ct

        # Check if the imbalance ratio less than the threshold of 0.4
        if imb_ratio < 0.4:
            self._display_msg(msg="Imbalance Found.",
                              progress_bar=self.progress_bar)
            return True

        self._display_msg(msg="Imbalance Not Found.",
                          progress_bar=self.progress_bar)
        return False
    
    def _set_custom_sampling(self):
        """
        DESCRIPTION:
            Function to handle customized data sampling for imbalance dataset.
        """
        # Fetching user input for data sampling
        data_imbalance_input = self.custom_data.get("DataImbalanceIndicator", False) 
        if data_imbalance_input:
            # Extracting method for performing data sampling
            handling_method = self.custom_data.get("DataImbalanceMethod", None)
            if handling_method == 'SMOTE':
                self._data_sampling_method = "SMOTE"
            elif handling_method == 'NearMiss':
                self._data_sampling_method = "NearMiss"
            else:
                self._display_msg(inline_msg="Provided method for data imbalance is not supported. AutoML will Proceed with default option.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="No information provided for performing customized imbalanced dataset sampling. AutoML will Proceed with default option.",
                              progress_bar=self.progress_bar)
    
    def _data_sampling(self, 
                       data):
        """
        DESCRIPTION:
            Function to handle data imbalance in dataset using sampling techniques 
            in case of classification.
            
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: pandas Dataframe.

        RETURNS:
            Teradataml dataframe after handling data imbalance.
        """
        self._display_msg(msg="\nStarting data imbalance handling ...",
                          progress_bar=self.progress_bar,
                          show_data=True)

        # Importing required libraries
        from imblearn.over_sampling import SMOTE
        from imblearn.under_sampling import NearMiss
        
        st = time.time()
        self._display_msg(msg=f"\nBalancing the data using {self._data_sampling_method}...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        # Performing data sampling
        try:
            # Fetching the minimum target column label count and 
            # accordingly setting the number of neighbors for the sampler
            min_label_count = min(data[self.target_column].value_counts())
            if self._data_sampling_method == 'SMOTE':
                n_neighbors = min(5, min_label_count - 1)
                sampling_method = SMOTE(k_neighbors=n_neighbors, random_state=42)
            else:
                n_neighbors = min(3, min_label_count)
                sampling_method = NearMiss(version=1, n_neighbors=n_neighbors)
            
            # Fitting on dataset
            xt, yt = sampling_method.fit_resample(data.drop(columns=[self.target_column], axis=1), 
                                                    data[self.target_column])
            
            # Merging the balanced dataset with target column
            balanced_df = (xt.reset_index().merge(yt.reset_index(), on="index")) 
            balanced_df.drop(columns=['index', 'id'], axis=1, inplace=True)
            balanced_df = balanced_df.reset_index().rename(columns={'index': 'id'})
            
            et = time.time()
            self._display_msg(msg=f"Handled imbalanced dataset using {self._data_sampling_method}: {et - st:.2f} sec",
                                progress_bar=self.progress_bar,
                                show_data=True)
        except:
            self._display_msg(msg=f"Balancing using {self._data_sampling_method} Failed!!",
                              progress_bar=self.progress_bar,
                              show_data=True)
            # Returning original data if the data sampler fails
            return data
        
        self._display_msg(msg="Completed data imbalance handling.",
                          progress_bar=self.progress_bar,
                          show_data=True)
        # Returning balanced dataframe
        return balanced_df

class AutoRegressor(AutoML):
    
    def __init__(self,
                 include = None,
                 exclude = None,
                 verbose=0,
                 max_runtime_secs=None,
                 stopping_metric=None, 
                 stopping_tolerance=None,
                 max_models=None,
                 custom_config_file=None,
                 **kwargs
                ):
        """
        DESCRIPTION:
            AutoRegressor is a special purpose AutoML feature to run regression specific tasks.
            Note:
                * configure.temp_object_type="VT" follows sequential execution.

         
        PARAMETERS:
            include:
                Optional Argument.
                Specifies the model algorithms to be used for model training phase.
                By default, all 5 models are used for training for regression and binary
                classification problem, while only 3 models are used for multi-class.
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str
            
            exclude:
                Optional Argument.
                Specifies the model algorithms to be excluded from model training phase.
                No model is excluded by default.
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str
                    
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
                
            max_runtime_secs:
                Optional Argument.
                Specifies the time limit in seconds for model training.
                Types: int
                
            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
                Specifies the stopping mertics for stopping tolerance in model training.
                Permitted Values: 
                    * For task_type "Regression": "R2", "MAE", "MSE", "MSLE",
                                                  "MAPE", "MPE", "RMSE", "RMSLE",
                                                  "ME", "EV", "MPD", "MGD"

                    * For task_type "Classification": 'MICRO-F1','MACRO-F1',
                                                      'MICRO-RECALL','MACRO-RECALL',
                                                      'MICRO-PRECISION', 'MACRO-PRECISION',
                                                      'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                                                      'WEIGHTED-F1', 'ACCURACY'
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
                Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
            
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int
                
            custom_config_file:
                Optional Argument.
                Specifies the path of JSON file in case of custom run.
                Types: str

            **kwargs:
                Specifies the additional arguments for AutoRegressor. Below
                are the additional arguments:
                    volatile:
                            Optional Argument.
                            Specifies whether to put the interim results of the
                            functions in a volatile table or not. When set to
                            True, results are stored in a volatile table,
                            otherwise not.
                            Default Value: False
                            Types: bool

                    persist:
                        Optional Argument.
                        Specifies whether to persist the interim results of the
                        functions in a table or not. When set to True,
                        results are persisted in a table; otherwise,
                        results are garbage collected at the end of the
                        session.
                        Default Value: False
                        Types: bool
                    
                    seed:
                        Optional Argument.
                        Specifies the random seed for reproducibility.
                        Default Value: 42
                        Types: int
            
        RETURNS:
            Instance of AutoRegressor.
    
        RAISES:
            TeradataMlException, TypeError, ValueError
            
        EXAMPLES:
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function will raise error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("decisionforestpredict", ["housing_train", "housing_test"])
    
            # Create teradataml DataFrame object.
            >>> housing_train = DataFrame.from_table("housing_train")
            
            # Example 1 : Run AutoRegressor using default options.
            # Scenario : Predict the price of house based on different factors.
           
            # Create instance of AutoRegressor.
            >>> automl_obj = AutoRegressor()

            # Fit the data.
            >>> automl_obj.fit(housing_train, "price")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()

            # Display best performing model.
            >>> automl_obj.leader()
            
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(housing_test)
            >>> prediction
            
            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(housing_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test)
            >>> performance_metrics
            
            # Run evaluate to get performance metrics using second best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test, 2)
            >>> performance_metrics

            # Example 2 : Run AutoRegressor for regression problem with early stopping metric and tolerance.
            # Scenario : Predict the price of house based on different factors.
            #            Use custom configuration file to customize different 
            #            processes of AutoML Run. Define performance threshold
            #            to acquire for the available models, and terminate training 
            #            upon meeting the stipulated performance criteria.
            
            # Generate custom configuration file.
            >>> AutoRegressor.generate_custom_config("custom_housing")

            # Create instance of AutoRegressor.
            >>> automl_obj = AutoRegressor(verbose=2,
            >>>                            exclude="xgboost",
            >>>                            stopping_metric="R2",
            >>>                            stopping_tolerance=0.7,
            >>>                            max_models=10,
            >>>                            custom_config_file="custom_housing.json")
            # Fit the data.
            >>> automl_obj.fit(housing_train, "price")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(housing_test)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test)
            >>> performance_metrics

            # Example 3 : Run AutoRegressor for regression problem with maximum runtime.
            # Scenario : Predict the price of house based on different factors.
            #            Run AutoML to get the best performing model in specified time.

            # Create instance of AutoRegressor.
            >>> automl_obj = AutoRegressor(verbose=2, 
            >>>                            exclude="xgboost",
            >>>                            max_runtime_secs=500)
            # Fit the data.
            >>> automl_obj.fit(housing_train, "price")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Display best performing model.
            >>> automl_obj.leader()  
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(housing_test)
            >>> prediction

            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(housing_test, 2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(housing_test)
            >>> performance_metrics
        """
        self.verbose = verbose
        self.max_runtime_secs = max_runtime_secs
        self.stopping_metric = stopping_metric
        self.stopping_tolerance = stopping_tolerance
        self.max_models = max_models
        self.custom_config_file = custom_config_file
        self.task_type = "Regression"
        self.include = include
        self.exclude = exclude
        
        super(AutoRegressor, self).__init__(task_type=self.task_type,
                                            include = self.include,
                                            exclude = self.exclude,
                                            verbose=self.verbose,
                                            max_runtime_secs=self.max_runtime_secs,
                                            stopping_metric=self.stopping_metric, 
                                            stopping_tolerance=self.stopping_tolerance,
                                            max_models=self.max_models,
                                            custom_config_file=self.custom_config_file,
                                            **kwargs)        
class AutoClassifier(AutoML):
        
    def __init__(self,
                include = None,
                exclude = None,
                verbose=0,
                max_runtime_secs=None,
                stopping_metric=None, 
                stopping_tolerance=None,
                max_models=None,
                custom_config_file=None,
                **kwargs
                ):
        """
        DESCRIPTION:
            AutoClassifier is a special purpose AutoML feature to run classification specific tasks.
            Note:
                * configure.temp_object_type="VT" follows sequential execution.

            
        PARAMETERS:  
            include:
                Optional Argument.
                Specifies the model algorithms to be used for model training phase.
                By default, all 5 models are used for training for regression and binary
                classification problem, while only 3 models are used for multi-class.
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str  
            
            exclude:
                Optional Argument.
                Specifies the model algorithms to be excluded from model training phase.
                No model is excluded by default. 
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str
                    
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
                
            max_runtime_secs:
                Optional Argument.
                Specifies the time limit in seconds for model training.
                Types: int
                
            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
                Specifies the stopping mertics for stopping tolerance in model training.
                Permitted Values: 
                    * For task_type "Regression": "R2", "MAE", "MSE", "MSLE",
                                                  "MAPE", "MPE", "RMSE", "RMSLE",
                                                  "ME", "EV", "MPD", "MGD"
                                                  
                    * For task_type "Classification": 'MICRO-F1','MACRO-F1',
                                                      'MICRO-RECALL','MACRO-RECALL',
                                                      'MICRO-PRECISION', 'MACRO-PRECISION',
                                                      'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                                                      'WEIGHTED-F1', 'ACCURACY'
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
                Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
            
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int
                
            custom_config_file:
                Optional Argument.
                Specifies the path of json file in case of custom run.
                Types: str

            **kwargs:
                Specifies the additional arguments for AutoClassifier. Below
                are the additional arguments:
                    volatile:
                        Optional Argument.
                        Specifies whether to put the interim results of the
                        functions in a volatile table or not. When set to
                        True, results are stored in a volatile table,
                        otherwise not.
                        Default Value: False
                        Types: bool

                    persist:
                        Optional Argument.
                        Specifies whether to persist the interim results of the
                        functions in a table or not. When set to True,
                        results are persisted in a table; otherwise,
                        results are garbage collected at the end of the
                        session.
                        Default Value: False
                        Types: bool
                    
                    seed:
                        Optional Argument.
                        Specifies the random seed for reproducibility.
                        Default Value: 42
                        Types: int
                
        RETURNS:
            Instance of AutoClassifier.
    
        RAISES:
            TeradataMlException, TypeError, ValueError
            
        EXAMPLES:    
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function will raise error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("teradataml", ["titanic", "iris_input"])
            >>> load_example_data("GLMPredict", ["admissions_test", "admissions_train"])
            
            # Create teradataml DataFrame object.
            >>> admissions_train = DataFrame.from_table("admissions_train")
            >>> titanic = DataFrame.from_table("titanic")
            >>> iris_input = DataFrame.from_table("iris_input")
            >>> admissions_test = DataFrame.from_table("admissions_test")
            
            # Example 1 : Run AutoClassifier for binary classification problem
            # Scenario : Predict whether a student will be admitted to a university
            #            based on different factors. Run AutoML to get the best performing model
            #            out of available models.
            
            # Create instance of AutoClassifier..
            >>> automl_obj = AutoClassifier()

            # Fit the data.
            >>> automl_obj.fit(admissions_train, "admitted")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()

            # Display best performing model.
            >>> automl_obj.leader()
            
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(admissions_test)
            >>> prediction
            
            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(admissions_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(admissions_test)
            >>> performance_metrics
            
            # Run evaluate to get performance metrics using model rank 4.
            >>> performance_metrics = automl_obj.evaluate(admissions_test, 4)
            >>> performance_metrics

            # Example 2 : Run AutoClassifier for binary classification.
            # Scenario : Predict whether passenger aboard the RMS Titanic survived
            #            or not based on differect factors. Run AutoML to get the 
            #            best performing model out of available models. Use custom
            #            configuration file to customize different processes of
            #            AutoML Run. 
            
            # Split the data into train and test.
            >>> titanic_sample = titanic.sample(frac = [0.8, 0.2])
            >>> titanic_train= titanic_sample[titanic_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> titanic_test = titanic_sample[titanic_sample['sampleid'] == 2].drop('sampleid', axis=1)
            
            # Generate custom configuration file.
            >>> AutoClassifier.generate_custom_config("custom_titanic")
            
            # Create instance of AutoClassifier.
            >>> automl_obj = AutoClassifier(verbose=2, 
            >>>                             custom_config_file="custom_titanic.json")
            # Fit the data.
            >>> automl_obj.fit(titanic_train, titanic_train.survived)

            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Display best performing model.
            >>> automl_obj.leader()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(titanic_test)
            >>> prediction

            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(titanic_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(titanic_test)
            >>> performance_metrics

            # Example 3 : Run AutoClassifier for multiclass classification problem.
            # Scenario : Predict the species of iris flower based on different factors.
            #            Run AutoML to get the best performing model out of available 
            #            models. Use custom configuration file to customize different 
            #            processes of AutoML Run.
            
            # Split the data into train and test.
            >>> iris_sample = iris_input.sample(frac = [0.8, 0.2])
            >>> iris_train= iris_sample[iris_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> iris_test = iris_sample[iris_sample['sampleid'] == 2].drop('sampleid', axis=1)
            
            # Generate custom configuration file.
            >>> AutoClassifier.generate_custom_config("custom_iris")
            
            # Create instance of AutoClassifier.
            >>> automl_obj = AutoClassifier(verbose=1, 
            >>>                             custom_config_file="custom_iris.json")
            # Fit the data.
            >>> automl_obj.fit(iris_train, "species")
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
  
            # Display best performing model.
            >>> automl_obj.leader()

            # Predict on test data using best performing model.
            >>> prediction = automl_obj.predict(iris_test)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(iris_test)
            >>> performance_metrics

            # Example 4 : Run AutoClassifier for classification problem with stopping metric and tolerance.
            # Scenario : Predict whether passenger aboard the RMS Titanic survived
            #            or not based on differect factors. Use custom configuration 
            #            file to customize different processes of AutoML Run. Define
            #            performance threshold to acquire for the available models, and 
            #            terminate training upon meeting the stipulated performance criteria.
            
            # Split the data into train and test.
            >>> titanic_sample = titanic.sample(frac = [0.8, 0.2])
            >>> titanic_train= titanic_sample[titanic_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> titanic_test = titanic_sample[titanic_sample['sampleid'] == 2].drop('sampleid', axis=1)
            
            # Generate custom configuration file.
            >>> AutoClassifier.generate_custom_config("custom_titanic")

            # Create instance of AutoClassifier.
            >>> automl_obj = AutoClassifier(verbose=2, 
            >>>                             exclude="xgboost",
            >>>                             stopping_metric="MICRO-F1",
            >>>                             stopping_tolerance=0.7,
            >>>                             max_models=8
            >>>                             custom_config_file="custom_titanic.json")
            # Fit the data.
            >>> automl_obj.fit(titanic_train, titanic_train.survived)
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(titanic_test)
            >>> prediction
            
            # Run evaluate to get performance metrics using best performing model.
            >>> performance_metrics = automl_obj.evaluate(titanic_test)
            >>> performance_metrics

            # Example 5 : Run AutoClassifier for classification problem with maximum runtime.
            # Scenario : Predict the species of iris flower based on different factors.
            #            Run AutoML to get the best performing model in specified time.
            
            # Split the data into train and test.
            >>> iris_sample = iris_input.sample(frac = [0.8, 0.2])
            >>> iris_train= iris_sample[iris_sample['sampleid'] == 1].drop('sampleid', axis=1)
            >>> iris_test = iris_sample[iris_sample['sampleid'] == 2].drop('sampleid', axis=1)

            # Create instance of AutoClassifier.
            >>> automl_obj = AutoClassifier(verbose=2, 
            >>>                             exclude="xgboost",
            >>>                             max_runtime_secs=500)
            >>>                             max_models=3)
            # Fit the data.
            >>> automl_obj.fit(iris_train, iris_train.species)
            
            # Display leaderboard.
            >>> automl_obj.leaderboard()
 
            # Display best performing model.
            >>> automl_obj.leader()
 
            # Run predict on test data using best performing model.
            >>> prediction = automl_obj.predict(iris_test)
            >>> prediction

            # Run predict on test data using second best performing model.
            >>> prediction = automl_obj.predict(iris_test, rank=2)
            >>> prediction
            
            # Run evaluate to get performance metrics using model rank 3.
            >>> performance_metrics = automl_obj.evaluate(iris_test, 3)
            >>> performance_metrics  
        """
        self.verbose = verbose
        self.max_runtime_secs = max_runtime_secs
        self.stopping_metric = stopping_metric
        self.stopping_tolerance = stopping_tolerance
        self.max_models = max_models
        self.custom_config_file = custom_config_file
        self.task_type = "Classification"
        self.include = include
        self.exclude = exclude
        
        super(AutoClassifier, self).__init__(task_type=self.task_type,
                                             include = self.include,
                                             exclude = self.exclude,
                                             verbose=self.verbose,
                                             max_runtime_secs=self.max_runtime_secs,
                                             stopping_metric=self.stopping_metric, 
                                             stopping_tolerance=self.stopping_tolerance,
                                             max_models=self.max_models,
                                             custom_config_file=self.custom_config_file,
                                             **kwargs)