import pandas as pd
from inspect import getsource
import re
from types import FunctionType
from teradataml.dbutils.filemgr import install_file, list_files, remove_file
from teradataml.options.configure import configure
import teradatasqlalchemy as tdsqlalchemy
from teradataml.utils.validators import _Validators
from teradataml.dataframe.sql import _SQLColumnExpression
from teradatasqlalchemy import VARCHAR, CLOB, CHAR
from teradataml.common.constants import TeradataTypes
from teradataml.common.utils import UtilFuncs
from teradataml.utils.dtypes import _Dtypes
from teradataml.dataframe.sql_interfaces import ColumnExpression
from teradataml.table_operators.table_operator_util import _TableOperatorUtils
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.scriptmgmt.lls_utils import get_env

def udf(user_function=None, returns=VARCHAR(1024), env_name = None, delimiter=',', quotechar=None):
    """
    DESCRIPTION:
        Creates a user defined function (UDF).
        
        Notes: 
            1. Date and time data types must be formatted to supported formats.
               (See Prerequisite Input and Output Structures in Open Analytics Framework for more details.)
            2. Packages required to run the user defined function must be installed in remote user 
               environment using install_lib method of UserEnv class. Import statements of these
               packages should be inside the user defined function itself.
            3. Do not call a regular function defined outside the udf() from the user defined function.
               The function definition and call must be inside the udf(). Look at Example 9 to understand more.

    PARAMETERS:
        user_function:
            Required Argument.
            Specifies the user defined function to create a column for
            teradataml DataFrame.
            Types: function
            Note:
                Lambda functions are not supported. Re-write the lambda function as regular Python function to use with UDF.

        returns:
            Optional Argument.
            Specifies the output column type.
            Types: teradatasqlalchemy types object
            Default: VARCHAR(1024)

        env_name:
            Optional Argument.
            Specifies the name of the remote user environment or an object of
            class UserEnv for VantageCloud Lake.
            Types: str or oject of class UserEnv.
            Note:
                * One can set up a user environment with required packages using teradataml
                  Open Analytics APIs. If no ``env_name`` is provided, udf use the default 
                  ``openml_env`` user environment. This default environment has latest Python
                  and scikit-learn versions that are supported by Open Analytics Framework
                  at the time of creating environment.

        delimiter:
            Optional Argument.
            Specifies a delimiter to use when reading columns from a row and
            writing result columns.
            Default value: ','
            Types: str with one character
            Notes:
                * This argument cannot be same as "quotechar" argument.
                * This argument cannot be a newline character.
                * Use a different delimiter if categorial columns in the data contains
                  a character same as the delimiter.

        quotechar:
            Optional Argument.
            Specifies a character that forces input of the user function
            to be quoted using this specified character.
            Using this argument enables the Advanced SQL Engine to
            distinguish between NULL fields and empty strings.
            A string with length zero is quoted, while NULL fields are not.
            Default value: None
            Types: str with one character
            Notes:
                * This argument cannot be same as "delimiter" argument.
                * This argument cannot be a newline character.

    RETURNS:
        ColumnExpression

    RAISES:
        TeradataMLException

    EXAMPLES:
        # Load the data to run the example.
        >>> load_example_data("dataframe", "sales")

        # Create a DataFrame on 'sales' table.
        >>> df = DataFrame("sales")
        >>> df
                    Feb    Jan    Mar    Apr    datetime
        accounts                                          
        Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
        Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
        Red Inc     200.0  150.0  140.0    NaN  04/01/2017
        Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
        Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
        Orange Inc  210.0    NaN    NaN  250.0  04/01/2017

        # Example 1: Create the user defined function to get the values in 'accounts'
        #            to upper case without passing returns argument.
        >>> from teradataml.dataframe.functions import udf
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(upper_stats = to_upper('accounts'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC
        >>>

        # Example 2: Create a user defined function to add length of string values in column  
        #           'accounts' with column 'Feb' and store the result in Integer type column.
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf(returns=INTEGER()) 
        ... def sum(x, y):
        ...     return len(x)+y
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(len_sum = sum('accounts', 'Feb'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime  len_sum
        accounts                                                 
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04      218
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04       98
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04      100
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04      209
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04      220
        Red Inc     200.0  150.0  140.0    NaN  17/01/04      207
        >>>

        # Example 3: Create a function to get the values in 'accounts' to upper case
        #            and pass it to udf as parameter to create a user defined function.
        >>> from teradataml.dataframe.functions import udf
        >>> def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>> upper_case = udf(to_upper)
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(upper_stats = upper_case('accounts'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC
        >>>
    
        # Example 4: Create a user defined function to add 4 to the 'datetime' column
        #            and store the result in DATE type column.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf(returns=DATE())
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%y/%m/%d")+datetime.timedelta(y)).strftime("%y/%m/%d")
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  new_date
        accounts                                                  
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  17/01/08
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  17/01/08
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  17/01/08
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  17/01/08
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  17/01/08
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  17/01/08

        # Example 5: Create a user defined function to add 4 to the 'datetime' column
        #            without passing returns argument.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%y/%m/%d")+datetime.timedelta(y))
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime             new_date
        accounts                                                             
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  2017-01-08 00:00:00
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  2017-01-08 00:00:00
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  2017-01-08 00:00:00
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  2017-01-08 00:00:00
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  2017-01-08 00:00:00
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  2017-01-08 00:00:00

        # Example 6: Create a two user defined function to 'to_upper' and 'sum',
        #            'to_upper' to get the values in 'accounts' to upper case and 
        #            'sum' to add length of string values in column 'accounts' 
        #            with column 'Feb' and store the result in Integer type column.
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf(returns=INTEGER()) 
        ... def sum(x, y):
        ...     return len(x)+y
        >>>
        # Assign the both Column Expression returned by user defined functions
        # to the DataFrame.
        >>> res = df.assign(upper_stats = to_upper('accounts'), len_sum = sum('accounts', 'Feb'))
        >>> res
                      Feb    Jan    Mar    Apr  datetime upper_stats  len_sum
        accounts                                                             
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC       98
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC      207
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC      100
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC      209
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC      220
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO      218
        >>>

        # Example 7: Convert the values is 'accounts' column to upper case using a user 
        #            defined function on Vantage Cloud Lake.
        # Create a Python 3.10.5 environment with given name and description in Vantage.
        >>> env = create_env('test_udf', 'python_3.10.5', 'Test environment for UDF')
        User environment 'test_udf' created.
        >>>
        # Create a user defined functions to 'to_upper' to get the values in upper case 
        # and pass the user env to run it on.
        >>> from teradataml.dataframe.functions import udf
        >>> @udf(env_name = env)
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> df.assign(upper_stats = to_upper('accounts'))
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC

        # Example 8: Create a user defined function to add 4 to the 'datetime' column
        #            and store the result in DATE type column on Vantage Cloud Lake.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf(returns=DATE())
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%Y-%m-%d")+datetime.timedelta(y)).strftime("%Y-%m-%d")
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  new_date
        accounts                                                  
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  17/01/08
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  17/01/08
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  17/01/08
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  17/01/08
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  17/01/08
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  17/01/08
        >>>

        # Example 9: Define a function 'inner_add_date' inside the udf to create a 
        #            date object by passing year, month, and day and add 1 to that date.
        #            Call this function inside the user defined function.
        >>> @udf
        ... def add_date(y,m,d):
        ... import datetime
        ... def inner_add_date(y,m,d):
        ...     return datetime.date(y,m,d) + datetime.timedelta(1)
        ... return inner_add_date(y,m,d)

        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date(2021, 10, 5))
        >>> res
                    Feb    Jan    Mar    Apr  datetime    new_date
        accounts                                                    
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  2021-10-06
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  2021-10-06
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  2021-10-06
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  2021-10-06
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  2021-10-06
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  2021-10-06
        >>>
    """

    allowed_datatypes = TeradataTypes.TD_ALL_TYPES.value
    # Validate datatypes in returns.
    _Validators._validate_function_arguments([["returns", returns, False, allowed_datatypes]])
    
    # Notation: @udf(returnType=INTEGER())
    if user_function is None:
        def wrapper(f):
            def func_(*args):
                return _SQLColumnExpression(expression=None, udf=f, udf_type=returns, udf_args=args,\
                                            env_name=env_name, delimiter=delimiter, quotechar=quotechar)
            return func_
        return wrapper
    # Notation: @udf
    else:
        def func_(*args):
            return _SQLColumnExpression(expression=None, udf=user_function, udf_type=returns, udf_args=args,\
                                        env_name=env_name, delimiter=delimiter, quotechar=quotechar)
    return func_


def register(name, user_function, returns=VARCHAR(1024)):
    """
    DESCRIPTION:
        Registers a user defined function (UDF).

        Notes: 
            1. Date and time data types must be formatted to supported formats.
               (See Requisite Input and Output Structures in Open Analytics Framework for more details.)
            2. On VantageCloud Lake, user defined function is registered by default in the 'openml_env' environment.
               User can register it in their own user environment, using the 'openml_user_env' configuration option.

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the user defined function to register.
            Types: str

        user_function:
            Required Argument.
            Specifies the user defined function to create a column for
            teradataml DataFrame.
            Types: function, udf
            Note:
                Lambda functions are not supported. Re-write the lambda function as regular Python function to use with UDF.

        returns:
            Optional Argument.
            Specifies the output column type used to register the user defined function.
            Note:
                * If 'user_function' is a udf, then return type of the udf is used as return type
                  of the registered user defined function.
            Default Value: VARCHAR(1024)
            Types: teradatasqlalchemy types object

    RETURNS:
        None

    RAISES:
        TeradataMLException, TypeError

    EXAMPLES:
        # Example 1: Register the user defined function to get the values upper case.
        >>> from teradataml.dataframe.functions import udf, register
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Register the created user defined function.
        >>> register("upper_val", to_upper)
        >>>

        # Example 2: Register a user defined function to get factorial of a number and
        #            store the result in Integer type column.
        >>> from teradataml.dataframe.functions import udf, register
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf
        ... def factorial(n):
        ...    import math
        ...    return math.factorial(n)
        >>>
        # Register the created user defined function.
        >>> register("fact", factorial, INTEGER())
        >>>

        # Example 3: Register a Python function to get the values upper case.
        >>> from teradataml.dataframe.functions import register
        >>> def to_upper(s):
        ...     return s.upper()
        >>>
        # Register the created Python function.
        >>> register("upper_val", to_upper)
        >>>
    """

    # Validate the arguments.
    arg_matrix = []
    allowed_datatypes = TeradataTypes.TD_ALL_TYPES.value
    arg_matrix.append(["returns", returns, True, allowed_datatypes])
    arg_matrix.append(["name", name, False, str])
    _Validators._validate_function_arguments(arg_matrix)

    function = []
    # Check if the user_function is Python function or
    # a user defined function(udf) or ColumnExpression returned by udf.
    if isinstance(user_function, ColumnExpression):
        function.append(user_function._udf)
        returns = user_function._type
    elif "udf.<locals>" not in user_function.__qualname__:
        function.append(user_function)
    else:
        user_function = user_function.__call__()
        function.append(user_function._udf)
        returns = user_function._type

    # Create a dictionary of user defined function name to return type.
    returns = {name: _create_return_type(returns)}

    exec_mode = 'REMOTE' if UtilFuncs._is_lake() else 'IN-DB'

    tbl_operators = _TableOperatorUtils([],
                                        None,
                                        "register",
                                        function,
                                        exec_mode,
                                        chunk_size=None,
                                        num_rows=1,
                                        delimiter=None,
                                        quotechar=None,
                                        data_partition_column=None,
                                        data_hash_column=None,
                                        style = "csv",
                                        returns = returns,
                                        )

    # Install the file on the lake/enterprise environment.
    if exec_mode == 'REMOTE':
        _Validators._check_auth_token("register")
        env_name = UtilFuncs._get_env_name()
        tbl_operators.__env = get_env(env_name)
        tbl_operators.__env.install_file(tbl_operators.script_path, suppress_output=True, replace=True)
    else:
        install_file(file_identifier=tbl_operators.script_base_name,
                        file_path=tbl_operators.script_path,
                        suppress_output=True, replace=True)


def call_udf(udf_name, func_args = () , **kwargs):
    """
    DESCRIPTION:
        Call a registered user defined function (UDF).

        Notes: 
            1. Packages required to run the registered user defined function must be installed in remote user 
               environment using install_lib method of UserEnv class. Import statements of these
               packages should be inside the user defined function itself.
            2. On VantageCloud Lake, user defined function runs by default in the 'openml_env' environment.
               User can use their own user environment, using the 'openml_user_env' configuration option.

    PARAMETERS:
        udf_name:
            Required Argument.
            Specifies the name of the registered user defined function.
            Types: str

        func_args:
            Optional Argument.
            Specifies the arguments to pass to the registered UDF.
            Default Value: ()
            Types: tuple

        delimiter:
            Optional Argument.
            Specifies a delimiter to use when reading columns from a row and
            writing result columns.
            Notes:
                * This argument cannot be same as "quotechar" argument.
                * This argument cannot be a newline character.
                * Use a different delimiter if categorial columns in the data contains
                  a character same as the delimiter.
            Default Value: ','
            Types: one character string

        quotechar:
            Optional Argument.
            Specifies a character that forces input of the user function
            to be quoted using this specified character.
            Using this argument enables the Analytics Database to
            distinguish between NULL fields and empty strings.
            A string with length zero is quoted, while NULL fields are not.
            Notes:
                * This argument cannot be same as "delimiter" argument.
                * This argument cannot be a newline character.
            Default Value: None
            Types: one character string

    RETURNS:
        ColumnExpression

    RAISES:
        TeradataMLException

    EXAMPLES:
        # Load the data to run the example.
        >>> load_example_data("dataframe", "sales")

        # Create a DataFrame on 'sales' table.
        >>> import random
        >>> dfsales = DataFrame("sales")
        >>> df = dfsales.assign(id = case([(df.accounts == 'Alpha Co', random.randrange(1, 9)),
        ...                           (df.accounts == 'Blue Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Jones LLC', random.randrange(1, 9)),
        ...                           (df.accounts == 'Orange Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Yellow Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Red Inc', random.randrange(1, 9))]))

        # Example 1: Register and Call the user defined function to get the values upper case.
        >>> from teradataml.dataframe.functions import udf, register, call_udf
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Register the created user defined function with name "upper".
        >>> register("upper", to_upper)
        >>>
        # Call the user defined function registered with name "upper" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(upper_col = call_udf("upper", ('accounts',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id   upper_col
        accounts
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4  YELLOW INC
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2    ALPHA CO
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5   JONES LLC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3     RED INC
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1    BLUE INC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4  ORANGE INC
        >>>

        # Example 2: Register and Call user defined function to get factorial of a number
        #            and store the result in Integer type column.
        >>> from teradataml.dataframe.functions import udf, register
        >>> @udf(returns = INTEGER())
        ... def factorial(n):
        ...    import math
        ...    return math.factorial(n)
        >>>
        # Register the created user defined function with name "fact".
        >>> from teradatasqlalchemy.types import INTEGER
        >>> register("fact", factorial)
        >>>
        # Call the user defined function registered with name "fact" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(fact_col = call_udf("fact", ('id',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id  fact_col
        accounts
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5       120
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4        24
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3         6
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1         1
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2         2
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4        24
        >>>

        # Example 3: Register and Call the Python function to get the values upper case.
        >>> from teradataml.dataframe.functions import register, call_udf
        >>> def to_upper(s):
        ...     return s.upper()
        >>>
        # Register the created Python function with name "upper".
        >>> register("upper", to_upper, returns = VARCHAR(1024))
        >>>
        # Call the Python function registered with name "upper" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(upper_col = call_udf("upper", ('accounts',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id   upper_col
        accounts
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4  YELLOW INC
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2    ALPHA CO
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5   JONES LLC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3     RED INC
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1    BLUE INC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4  ORANGE INC
        >>>
    """
    env = None
    delimiter = kwargs.pop('delimiter', ',')
    quotechar = kwargs.pop('quotechar', None)
    unknown_args = list(kwargs.keys())
    if len(unknown_args) > 0:
        raise TypeError(Messages.get_message(MessageCodes.UNKNOWN_ARGUMENT,
                                                "call_udf", unknown_args[0]))

    if UtilFuncs._is_lake():
        _Validators._check_auth_token("call_udf")
        env = get_env(UtilFuncs._get_env_name())
        file_list = env.files
        if file_list is None:
            raise TeradataMlException(Messages.get_message(
            MessageCodes.FUNC_EXECUTION_FAILED, "'call_udf'", "No UDF is registered with the name '{}'.".format(udf_name)),
                                MessageCodes.FUNC_EXECUTION_FAILED)
        file_column = 'File'
    else:
        file_list = list_files().to_pandas()
        file_column = 'Files'

    # Get the script name from the environment that starts with tdml_udf_name_<udf_name>_.
    script_file = [file for file in file_list[file_column] if file.startswith('tdml_udf_name_{}_udf_type_'.format(udf_name))]
    if len(script_file) != 1:
        raise TeradataMlException(Messages.get_message(
        MessageCodes.FUNC_EXECUTION_FAILED, "'call_udf'", "Multiple UDFs or no UDF is registered with the name '{}'.".format(udf_name)),
                                MessageCodes.FUNC_EXECUTION_FAILED)

    script_name = script_file[0]
    # Get the return type from the script name.
    x = re.search(r"tdml_udf_name_{}_udf_type_([A-Z_]+)(\d*)_register".format(udf_name), script_name)
    returns = getattr(tdsqlalchemy, x.group(1))
    # If the return type has length, get the length from the script name.
    returns = returns(x.group(2)) if x.group(2) else returns()

    return _SQLColumnExpression(expression=None, udf_args = func_args, udf_script = script_name, udf_type=returns,\
                                 delimiter=delimiter, quotechar=quotechar, env_name=env)


def list_udfs(show_files=False):
    """
    DESCRIPTION:
        List all the UDFs registered using 'register()' function.

    PARAMETERS:
        show_files:
            Optional Argument.
            Specifies whether to show file names or not.
            Default Value: False
            Types: bool

    RETURNS:
        Pandas DataFrame containing files and it's details or
        None if DataFrame is empty.

    RAISES:
        TeradataMLException.

    EXAMPLES:
        # Example 1: Register the user defined function to get the values in lower case,
                     then list all the UDFs registered.
        >>> @udf
        ... def to_lower(s):
        ...   if s is not None:
        ...        return s.lower()

        # Register the created user defined function.
        >>> register("lower", to_lower)

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     lower  VARCHAR1024  tdml_udf_name_lower_udf_type_VARCHAR1024_register.py
         1     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         2  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         3  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>
    """

    if UtilFuncs._is_lake():
        _Validators._check_auth_token("list_udfs")
        env_name = UtilFuncs._get_env_name()
        _df = get_env(env_name).files
        if _df is not None:
            # rename the existing DataFrame Column
            _df.rename(columns={'File': 'Files'}, inplace=True)
            _df = _df[_df['Files'].str.startswith('tdml_udf_') & _df['Files'].str.endswith('_register.py')][['Files']]
            if len(_df) == 0:
                print("No files found in remote user environment {}.".format(env_name))
            else:
                return _create_udf_dataframe(_df, show_files)

    else:
        _df = list_files()
        _df = _df[_df['Files'].startswith('tdml_udf_') & _df['Files'].endswith('_register.py')].to_pandas()
        if len(_df) == 0:
            print("No files found in Vantage")
        else:
            return _create_udf_dataframe(_df, show_files)

def _create_udf_dataframe(pandas_df, show_files=False):
    """
    DESCRIPTION:
        Internal function to return pandas DataFrame with
        column names "id", "name", "return_type", "filename".

    PARAMETERS:
        pandas_df:
            Required Argument.
            Specifies the pandas DataFrame containing one column 'Files'.
            Types: pandas DataFrame

        show_files:
            Optional Argument.
            Specifies whether to show file names or not.
            Types: bool

    RETURNS:
        pandas DataFrame.

    EXAMPLES:
        >>> _create_udf_dataframe(pandas_dataframe)

    """
    _lists = pandas_df.values.tolist()
    _data = {"id": [], "name": [], "return_type": []}
    if show_files:
        _data.update({"file_name": []})

    for _counter, _list in enumerate(_lists):
        # Extract udf name and type "tdml_udf_name_fact_udf_type_VARCHAR1024_register.py" -> ['fact', 'VARCHAR1024']
        value = _list[0][14:-12].split('_udf_type_')
        _data["id"].append(_counter)
        _data["name"].append(value[0])
        _data["return_type"].append(value[1])
        if show_files:
            _data["file_name"].append(_list[0])
    return pd.DataFrame(_data)


def deregister(name, returns=None):
    """
    DESCRIPTION:
        Deregisters a user defined function (UDF).

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the user defined function to deregister.
            Types: str

        returns:
            Optional Argument.
            Specifies the type used to deregister the user defined function.
            Types: teradatasqlalchemy types object

    RETURNS:
        None

    RAISES:
        TeradataMLException.

    EXAMPLES:
        # Example 1: Register the user defined function to get the values in lower case,
        #            then deregister it.
        >>> @udf
        ... def to_lower(s):
        ...   if s is not None:
        ...        return s.lower()

        # Register the created user defined function.
        >>> register("lower", to_lower)

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     lower  VARCHAR1024  tdml_udf_name_lower_udf_type_VARCHAR1024_register.py
         1     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         2  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         3  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>

        # Deregister the created user defined function.
        >>> deregister("lower")

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         1  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         2  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>

        # Example 2: Deregister only specified udf function with it return type.
        >>> @udf(returns=FLOAT())
        ... def sum(x, y):
        ...    return len(x) + y

        # Deregister the created user defined function.
        >>> register("sum", sum)

        # List all the UDFs registered
        >>> list_udfs(True)
        id name return_type                                       file_name
         0  sum       FLOAT    tdml_udf_name_sum_udf_type_FLOAT_register.py
         1  sum     INTEGER  tdml_udf_name_sum_udf_type_INTEGER_register.py
         >>>

        # Deregister the created user defined function.
        >>> from teradatasqlalchemy import FLOAT
        >>> deregister("sum", FLOAT())

        # List all the UDFs registered
        >>> list_udfs(True)
        id name return_type                                       file_name
         0  sum     INTEGER  tdml_udf_name_sum_udf_type_INTEGER_register.py
         >>>
    """
    _df = list_udfs(show_files=True)
    # raise Exception list_udfs  when DataFrame is empty
    if _df is None:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "'deregister'",
                                                       f"UDF '{name}' does not exist."),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    if returns is None:
        _df = _df[_df['file_name'].str.startswith(f'tdml_udf_name_{name}_udf_type_')]
    else:
        _df = _df[_df['file_name'].str.startswith(f'tdml_udf_name_{name}_udf_type_{_create_return_type(returns)}_register.py')]

    if len(_df) == 0:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "'deregister'",
                                                       f"UDF '{name}' does not exist."),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    _df = _df.values.tolist()

    # Remove the file on the lake/enterprise environment.
    if UtilFuncs._is_lake():
        env = get_env(UtilFuncs._get_env_name())
        for file_name in _df:
            env.remove_file(file_name[3], suppress_output=True)
    else:
        for file_name in _df:
            remove_file(file_name[3][:-3], force_remove = True, suppress_output = True)


def _create_return_type(returns):
    """
    DESCRIPTION:
        Internal function to return string representation of
        type "returns" in such a way it is included in file name.

    PARAMETERS:
        returns:
            Required Argument.
            Specifies the teradatasqlalchemy types object.
            Types: teradatasqlalchemy types object

    RETURNS:
        string

    EXAMPLES:
        >>> _create_udf_dataframe(VARCHAR(1024))
        'VARCHAR1024'
    """
    if isinstance(returns, (VARCHAR, CLOB, CHAR)):
        # If the length is not provided, set it to empty string.
        str_len = str(returns.length) if returns.length else ""
        return_str = str(returns) + str_len
    else:
        return_str = str(returns)
    # Replace the space with underscore in the return type.
    return_str = return_str.replace(" ", "_")
    return return_str