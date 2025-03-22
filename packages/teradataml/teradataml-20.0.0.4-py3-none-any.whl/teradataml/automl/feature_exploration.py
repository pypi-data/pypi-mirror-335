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


# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import ColumnSummary, CategoricalSummary, GetFutileColumns
from teradataml import OutlierFilterFit, OutlierFilterTransform
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.common.messages import Messages, MessageCodes
from teradataml import display as dp

def _is_terminal():
    """
    DESCRIPTION:
        Common Function detects whether code is running in
        terminal/console or IPython supported environment.

    RETURNS:
        bool.
    """
    if not hasattr(_is_terminal, 'ipython_imported'):
        try:
            # Check IPython environment
            __IPYTHON__
            # Check if IPython library is installed
            from IPython.display import display, HTML
            _is_terminal.ipython_imported = True
        except (NameError, ImportError):
            # If error, then terminal
            _is_terminal.ipython_imported = False

    return not _is_terminal.ipython_imported

# # conditional import
if not _is_terminal():
    from IPython.display import display, HTML

class _FeatureExplore:
    
    def __init__(self,
                data=None,
                target_column=None,
                verbose=0):
        """
        DESCRIPTION:
            Internal function initializes the data, target column for feature exploration.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml DataFrame for feature exploration.
                Types: teradataml Dataframe
            
            target_column:
                Required Arugment.
                Specifies the name of the target column in "data".
                Types: str
                
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
        """
        self.data = data
        self.target_column = target_column 
        self.verbose = verbose
        self.terminal_print = _is_terminal()
        self.style = self._common_style()

    def _exploration(self):
        """
        DESCRIPTION:
            Internal function performs following operations:
                1. Column summary of columns of the dataset
                2. Statistics of numeric columns of the dataset
                3. Categorical column summary
                4. Futile columns in the dataset
                5. Target column distribution
                6. Outlier Percentage in numeric columns of the dataset
        """
        numerical_columns = []
        categorical_columns= []
        date_column_list = []

        self._display_heading(phase=0)
        self._display_msg(msg='Feature Exploration started ...')
        
        # Detecting numerical and categorical column
        for col, d_type in self.data._column_names_and_types:
            if d_type in ['int','float']:
                numerical_columns.append(col)
            elif d_type in ['str']:
                categorical_columns.append(col)
            elif d_type in ['datetime.date','datetime.datetime']:
                date_column_list.append(col)

        # Display initial Count of data
        self._display_msg(msg = '\nData Overview:', show_data=True)
        print(f"Total Rows in the data: {self.data.shape[0]}\n"\
              f"Total Columns in the data: {self.data.shape[1]}")
        
        # Displaying date columns
        if len(date_column_list)!=0:
            self._display_msg(msg='Identified Date Columns:',
                             data=date_column_list)
        
        # Column Summary of each feature of data
        # such as null count, datatype, non null count
        self._column_summary()
        
        # Displays statistics such as mean/median/mode
        self._statistics()
        
        # Categorcial Summary and futile column detection
        if len(categorical_columns) != 0:
            categorical_obj = self._categorical_summary(categorical_columns)
            self._futile_column(categorical_obj)
        
        # Plot a graph of target column
        self._target_column_details()
        
        # Displays outlier percentage 
        outlier_method = "Tukey"
        df = self._outlier_detection(outlier_method,numerical_columns)    

    def _statistics(self):     
        """
        DESCRIPTION:
            Internal function displays the statistics of numeric columns such mean, mode, median.
        """
        # Statistics of numerical columns
        self._display_msg(msg='\nStatistics of Data:',
                          data=self.data.describe(),
                          show_data=True)

        
    def _column_summary(self):       
        """
        DESCRIPTION:
            Internal function displays the column summary of categorical column such as 
            datatype, null count, non null count, zero count.
        """
        dp.max_rows = self.data.shape[1]
        # Column Summary of all columns of dataset
        obj = ColumnSummary(data=self.data,
                            target_columns=self.data.columns)
        self._display_msg(msg='\nColumn Summary:',
                          data=obj.result,
                          show_data=True)
        dp.max_rows = 10
               
    def _categorical_summary(self, 
                             categorical_columns=None):
        """
        DESCRIPTION:
            Internal function display the categorical summary of categorical column such count, distinct values.

        PARAMETERS:
            categorical_columns:
                Required Argument.
                Specifies the categorical columns.
                Types: str or list of strings (str)
        
        RETURNS:
            Instance of ColumnSummary.
        """
        self._display_msg(msg='\nCategorical Columns with their Distinct values:',
                          show_data=True)
        
        # Categorical Summary of categorical columns
        obj = CategoricalSummary(data=self.data,
                                 target_columns=categorical_columns)
        
        catg_obj = obj.result[obj.result['DistinctValue'] != None]
        print("{:<25} {:<10}".format("ColumnName", "DistinctValueCount"))
        for col in categorical_columns:
            dst_val = catg_obj[catg_obj['ColumnName'] == col].size//3
            print("{:<25} {:<10}".format(col, dst_val))
        
        return obj
    
    def _futile_column(self, 
                       categorical_obj):
        """
        DESCRIPTION:
            Internal function detects the futile columns.

        PARAMETERS:
            categorical_obj:
                Required Argument.
                Specifies the instance of CategoricalSummary for futile column detection..
                Types: Instance of CategoricalSummary     
        """
        # Futile columns detection using categorical column object
        gfc_out = GetFutileColumns(data=self.data,
                                   object=categorical_obj,
                                   category_summary_column="ColumnName",
                                   threshold_value=0.7)
        
        # Extracts the futile column present in the first column
        f_cols = [i[0] for i in gfc_out.result.itertuples()]

        if len(f_cols) == 0:
            self._display_msg(inline_msg='\nNo Futile columns found.',
                              show_data=True)
        else:
            self._display_msg(msg='\nFutile columns in dataset:',
                              data=gfc_out.result,
                              show_data=True)

    def _target_column_details(self,
                               plot_data = None):
        """
        DESCRIPTION:
            Internal function displays the target column distribution of Target column/ Response column.
            
        PARAMETERS:
            plot_data:
                Required Argument.
                Specifies the input teradataml DataFrame for plotting distribution.
                Types: teradataml Dataframe
        """
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns
            if plot_data is None:
                target_data = self.data.select([self.target_column]).to_pandas()
            else:
                target_data = plot_data[[self.target_column]]
            self._display_msg(msg='\nTarget Column Distribution:',
                              show_data=True)
            plt.figure(figsize=(8, 6)) 
            # Ploting a histogram for target column
            plt.hist(target_data, bins=10, density=True, edgecolor='black')
            plt.xlabel(self.target_column)
            plt.ylabel('Density')
            plt.show()
    
    def _check_visualization_libraries(self):
        """
        DESCRIPTION:
            Internal function Checks the availability of data visualization libraries.
            
        RETURNS:
            Boolean, True if data visualization libraries are available. Otherwise return False.
        """
        
        # Conditional import
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            print("Install seaborn and matplotlib libraries to visualize the data.")
            return False
        
        return True
        
    def _outlier_detection(self, 
                           outlier_method,
                           column_list,
                           lower_percentile = None,
                           upper_percentile = None):
        """
        DESCRIPTION:
            Function detects the outlier in numerical column and display thier percentage.

        PARAMETERS:
            outlier_method:
                Required Argument.
                Specifies the outlier method required for outlier detection.
                Types: str

            column_list:
                Required Argument.
                Specifies the numeric columns for outlier percentage calculation.
                Types: str or list of strings (str)
                
            lower_percentile:
                Optional Argument.
                Specifies the lower percentile value for outlier detection in case of percentile method.
                Types: float
                   
            upper_percentile:
                Optional Argument.
                Specifies the upper percentile value for outlier detection in case of percentile method.
                Types: float
        
        RETURNS:
            Pandas DataFrame containing, column name with outlier percentage.

        """
        # Performing outlier fit on the data for replacing outliers with NULL value
        fit_params = {
            "data" : self.data,
            "target_columns" : column_list,
            "outlier_method" : outlier_method,
            "lower_percentile" : lower_percentile,
            "upper_percentile" : upper_percentile,
            "replacement_value" : 'NULL'
        }
        OutlierFilterFit_out = OutlierFilterFit(**fit_params)
        transform_params = {
            "data" : self.data,
            "object" : OutlierFilterFit_out.result
        }
        # Performing outlier transformation on each column
        OutlierTransform_obj = OutlierFilterTransform(**transform_params)
        
        # Column summary of each column of the data
        fit_params = {
            "data" : OutlierTransform_obj.result,
            "target_columns" : column_list
        }
        colSummary = ColumnSummary(**fit_params)

        null_count_expr = colSummary.result.NullCount
        non_null_count_expr = colSummary.result.NonNullCount
        
        # Calculating outlier percentage
        df = colSummary.result.assign(True, 
                                      ColumnName = colSummary.result.ColumnName, 
                                      OutlierPercentage = (null_count_expr/(non_null_count_expr+null_count_expr))*100)
    
        # Displaying non-zero containing outlier percentage for columns
        df = df[df['OutlierPercentage']>0]
        if self.verbose > 0:
            print(" "*500, end='\r')
            if df.shape[0] > 0:
                self._display_msg(msg='Columns with outlier percentage :-',
                                  show_data=True)
                print(df)
            else:
                print("\nNo outlier found!")
            
        return df
    
    def _common_style(self):
        """
        DESCRIPTION:
            Internal Function sets the style tag for HTML.
        
        RETURNS:
            string containing style tag.
        
        """
        style = '''
            <style>
                .custom-div {
                    background-color: lightgray;
                    color: #000000;
                    padding: 10px;
                    border-radius: 8px;
                    box-shadow: 0 3px 4px rgba(0, 0, 0, 0.2);
                    margin-bottom: 10px;
                    text-align: center;
                }
            </style>
        '''
        return style
    
    def _display_heading(self,
                         phase=0,
                         progress_bar=None):
        """
        DESCRIPTION:
            Internal function to print the phase of AutoML that
            completed in green color.
            
        PARAMETERS:
            phase:
                Optional Argument.
                Specifies the phase of automl that completed.
                Types: int
        
            progress_bar:
                Optional Argument.
                Specifies the _ProgressBar object.
                Types: object (_ProgressBar)
        
        RETURNS:
            None.
        """
        # Phases of automl
        steps = ["1. Feature Exploration ->", " 2. Feature Engineering ->",
                 " 3. Data Preparation ->", " 4. Model Training & Evaluation"]
        # Check verbose > 0
        if self.verbose > 0:
            
            # Check if code is running in IPython enviornment
            if not self.terminal_print:
                # Highlightedt phases of automl
                highlighted_steps = "".join(steps[:phase])
                
                # Unhighlighted phases of automl
                unhighlighted_steps = "".join(steps[phase:])
                
                # Combining highlighted and unhighlighted phases
                msg = self.style + f'<br><div class="custom-div"><h3><span style="color: green;">{highlighted_steps}</span>{unhighlighted_steps}<center></h3></center></div>'
                # Displaying the msg
                if progress_bar is not None:
                    progress_bar.update(msg=msg,
                                        progress=False,
                                        ipython=True)
                else:
                    display(HTML(msg))
            else:
                try:
                    # Try to import colorama if not already imported
                    from colorama import Fore, Style, init
                    # initalize the color package
                    init()
                    
                    # Highlight the phases of automl
                    highlighted_steps = "".join([Fore.GREEN + Style.BRIGHT + step + Style.RESET_ALL for step in steps[:phase]])
                    
                    # Unhighlighted the phases of automl
                    unhighlighted_steps = "".join(steps[phase:])
                    
                    # Combining highlighted and unhighlighted phases
                    msg = f'{highlighted_steps}{unhighlighted_steps}'
                    
                except ImportError:    
                    msg = "".join(step for step in steps)
                
                if progress_bar is not None:
                    progress_bar.update(msg=msg,
                                        progress=False)
                else:
                    print(msg)
                
    def _display_msg(self,
                     msg=None, 
                     progress_bar=None,
                     inline_msg=None,
                     data=None,
                     col_lst=None,
                     show_data=False):
        """
        DESCRIPTION:
            Internal Function to print statement according to
            environment.
        
        PARAMETERS:
            msg:
                Optional Argument.
                Specifies the message to print.
                Types: str
            
            progress_bar:
                Optional Argument.
                Specifies the _ProgressBar object.
                Types: object (_ProgressBar)
                
            inline_msg:
                Optional Argument.
                Specifies the additional information to print.
                Types: str
            
            data:
                Optional Argument.
                Specifies the teradataml dataframe to print.
                Types: teradataml DataFrame
            
            col_lst:
                Optional Argument.
                Specifies the list of columns.
                Types: list of str/int/data.time
            
            show_data:
                Optional Argument.
                Specifies whether to print msg/data when verbose<2.
                Default Value: False
                Types: bool
        
        RETURNS:
            None.
                
        """
        # If verbose level is set to 2
        if self.verbose == 2:
            # If a progress bar is provided
            if progress_bar:
                # If a message is provided
                if msg:
                    # Update the progress bar with the message and either the column list or data (if they are not None)
                    progress_bar.update(msg=msg, data=col_lst if col_lst else data if data is not None else None, 
                                        progress=False, 
                                        ipython=not self.terminal_print)
                    # Displaying shape of data
                    if data is not None:
                        progress_bar.update(msg=f'{data.shape[0]} rows X {data.shape[1]} columns',
                                            progress=False,
                                            ipython=not self.terminal_print)
                # If an inline message is provided instead
                elif inline_msg:
                    # Update the progress bar with the inline message
                    progress_bar.update(msg=inline_msg, progress=False)
            # If no progress bar is provided
            else:
                # If a message is provided
                if msg:
                    # Print the message
                    print(f"{msg}")
                    # If a column list is provided
                    if col_lst:
                        # Print the column list
                        print(col_lst)
                    # If data is provided instead
                    elif data is not None:
                        # Print the data if terminal_print is True, else display the data
                        print(data) if self.terminal_print else display(data)
                # If an inline message is provided instead
                elif inline_msg:
                    # Print the inline message
                    print(f'{inline_msg}')
            # Exit the function after handling verbose level 2
            return

        # If verbose level is more than 0 and show_data is True
        if self.verbose > 0 and show_data:
            # If a progress bar and a message are provided
            if progress_bar and msg:
                # Update the progress bar with the message and data (if data is not None)
                progress_bar.update(msg=msg, data=data if data is not None else None, 
                                    progress=False, ipython=not self.terminal_print)
            # If no progress bar is provided
            else:
                # If a message is provided
                if msg:
                    # Print the message if terminal_print is True, else display the message
                    print(f'{msg}') if self.terminal_print else display(HTML(f'<h4>{msg}</h4>'))
                # If data is provided
                if data is not None:
                    # Print the data if terminal_print is True, else display the data
                    print(data) if self.terminal_print else display(data)