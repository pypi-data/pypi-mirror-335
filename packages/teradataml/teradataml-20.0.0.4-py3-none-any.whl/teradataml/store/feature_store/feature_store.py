"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements the core framework that allows user to use Teradata Enterprise Feature Store.
"""

from sqlalchemy import literal_column
from teradataml.context.context import get_connection
from teradataml.common.constants import SQLConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.dataframe.sql import _SQLColumnExpression as Col
from teradataml.dbutils.dbutils import _create_database, _create_table, db_drop_table, execute_sql, Grant, Revoke, _update_data, _delete_data, db_transaction
from teradataml.store.feature_store.constants import *
from teradataml.store.feature_store.models import *
from teradataml.common.sqlbundle import SQLBundle
from teradataml.utils.validators import _Validators


class FeatureStore:
    """Class for FeatureStore."""

    def __init__(self, repo):
        """
        DESCRIPTION:
            Method to create FeatureStore in teradataml.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the repository name.
                Types: str.

        RETURNS:
            Object of FeatureStore.

        RAISES:
            None

        EXAMPLES:
            >>> # Create FeatureStore for repository 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            >>> fs
            FeatureStore(vfs_v1)-v1.0
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["repo", repo, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        # Do not validate the existance of repo as it consumes a network call.
        self.__repo = repo
        self.__version = ""

        # Declare SQLBundle to use it further.
        self.__sql_bundle = SQLBundle()

        # Store all the DF's here so no need to create these every time.
        self.__df_container = {}

        # Store the table names here. Then use this where ever required.
        self.__table_names = EFS_TABLES

        # Declare getter's for getting the corresponding DataFrame's.
        self.__get_features_df = lambda : self.__get_obj_df("feature")
        self.__get_archived_features_df = lambda : self.__get_obj_df("feature_staging")
        self.__get_group_features_df = lambda : self.__get_obj_df("group_features")
        self.__get_archived_group_features_df = lambda : self.__get_obj_df("group_features_staging")
        self.__get_feature_group_df = lambda : self.__get_obj_df("feature_group")
        self.__get_archived_feature_group_df = lambda : self.__get_obj_df("feature_group_staging")
        self.__get_entity_df = lambda : self.__get_obj_df("entity")
        self.__get_archived_entity_df = lambda : self.__get_obj_df("entity_staging")
        self.__get_data_source_df = lambda : self.__get_obj_df("data_source")
        self.__get_archived_data_source_df = lambda : self.__get_obj_df("data_source_staging")

        self.__good_status = "Good"
        self.__bad_status = "Bad"
        self.__repaired_status = "Repaired"

    @property
    def repo(self):
        """
        DESCRIPTION:
            Get the repository.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.repo
            vfs_v1
            >>>
        """
        return self.__repo

    @repo.setter
    def repo(self, value):
        """
        DESCRIPTION:
            Set the repository.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the repository name.
                Types: str.

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            # Example 1: Create a FeatureStore for repository 'abc' and
            #            then change the repository to 'xyz'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('abc')
            >>> fs.repo = 'xyz'
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["value", value, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        # remove all entries from container so they will be automatically
        # point to new repo for subsequent API's.
        self.__df_container.clear()
        self.__version = None

        # Set the repo value.
        self.__repo = value

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for FeatureStore object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        s = "VantageFeatureStore({})".format(self.__repo)
        try:
            version = "-v{}".format(self.__get_version())
        except Exception as e:
            version = ""
        return "{}{}".format(s, version)

    def __get_version(self):
        """
        DESCRIPTION:
            Internal method to get the FeatureStore version.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        if not self.__version:
            sql = "SELECT version FROM {}.{}".format(self.__repo, EFS_VERSION_SPEC["table_name"])
            self.__version = next(execute_sql(sql))[0]
        return self.__version

    @staticmethod
    def list_repos() -> DataFrame:
        """
        DESCRIPTION:
            Function to list down the repositories.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # List down all the FeatureStore repositories.
            >>> FeatureStore.list_repos()
                repos
            0  vfs_v1
            >>>
        """
        return DataFrame.from_query("select distinct DataBaseName as repos from dbc.tablesV where TableName='{}'".format(
            EFS_VERSION_SPEC["table_name"]))

    def setup(self, perm_size='10e9', spool_size='10e8'):
        """
        DESCRIPTION:
            Function to setup all the required objects in Vantage for the specified
            repository.
            Note:
                The function checks whether repository exists or not. If not exists,
                it first creates the repository and then creates the corresponding tables.
                Hence make sure the user with which is it connected to Vantage
                has corresponding access rights for creating DataBase and creating
                tables in the corresponding database.

        PARAMETERS:
            perm_size:
                Optional Argument.
                Specifies the number of bytes to allocate to FeatureStore "repo"
                for permanent space.
                Note:
                    Exponential notation can also be used.
                Default Value: 10e9
                Types: str or int

            spool_size:
                Optional Argument.
                Specifies the number of bytes to allocate to FeatureStore "repo"
                for spool space.
                Note:
                    Exponential notation can also be used.
                Default Value: 10e8
                Types: str or int

        RETURNS:
            bool

        RAISES:
            TeradatamlException

        EXAMPLES:
            # Setup FeatureStore for repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.setup()
            True
            >>>
        """

        repo_exists = get_connection().dialect._get_database_names(
            get_connection(), self.__repo)

        # If repo does not exist, then create it.
        if not repo_exists:
            _create_database(self.__repo, perm_size, spool_size)

        # Check whether version table exists or not. If exist, assume all
        # tables are available.
        all_tables_exist = get_connection().dialect.has_table(
            get_connection(), EFS_VERSION_SPEC['table_name'], schema=self.__repo)

        if not all_tables_exist:
            # Create the tables.
            table_specs = [EFS_FEATURES_SPEC,
                           EFS_DATA_SOURCE_SPEC,
                           EFS_ENTITY_SPEC,
                           EFS_ENTITY_XREF_SPEC,
                           EFS_FEATURE_GROUP_SPEC,
                           EFS_GROUP_FEATURES_SPEC,
                           EFS_VERSION_SPEC]

            staging_table_specs = [
                EFS_FEATURES_STAGING_SPEC,
                EFS_DATA_SOURCE_STAGING_SPEC,
                EFS_ENTITY_STAGING_SPEC,
                EFS_ENTITY_XREF_STAGING_SPEC,
                EFS_GROUP_FEATURES_STAGING_SPEC,
                EFS_FEATURE_GROUP_STAGING_SPEC
            ]

            triggers_specs = [
                EFS_FEATURES_TRG,
                EFS_GROUP_FEATURES_TRG,
                EFS_FEATURE_GROUP_TRG,
                EFS_DATA_SOURCE_TRG,
                EFS_ENTITY_TRG,
                EFS_ENTITY_XREF_TRG
            ]

            for table_spec in table_specs + staging_table_specs:
                params_ = {"table_name": table_spec["table_name"],
                           "columns": table_spec["columns"],
                           "primary_index": table_spec.get("primary_index"),
                           "unique": True if table_spec.get("primary_index") else False,
                           "schema_name": self.__repo,
                           "set_table": False
                           }
                if "foreign_keys" in table_spec:
                    params_["foreign_key_constraint"] = table_spec.get("foreign_keys")

                _create_table(**params_)

            for trigger_spec in triggers_specs:
                execute_sql(trigger_spec.format(schema_name=self.__repo))

            # After the setup is done, populate the version.
            insert_model = "insert into {}.{} values (?, ?);".format(self.__repo, EFS_VERSION_SPEC["table_name"])
            execute_sql(insert_model, (EFS_VERSION, datetime.datetime.now()))

        if repo_exists and all_tables_exist:
            print("EFS is already setup for the repo {}.".format(self.__repo))

    @property
    def grant(self):
        """
        DESCRIPTION:
            Grants access on FeatureStore.
            Note:
                One must have admin access to grant access.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            OperationalError

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Grant read access on FeatureStore to user 'BoB'.
            >>> fs.grant.read('BoB')
            True

            # Example 2: Grant write access on FeatureStore to user 'BoB'.
            >>> fs.grant.write('BoB')
            True

            # Example 3: Grant read and write access on FeatureStore to user 'BoB'.
            >>> fs.grant.read_write('BoB')
            True

        """
        table_names = {name: UtilFuncs._get_qualified_table_name(self.__repo, table_name)
                       for name, table_name in EFS_TABLES.items()}
        return Grant(list(table_names.values()))

    @property
    def revoke(self):
        """
        DESCRIPTION:
            Revokes access on FeatureStore.
            Note:
                One must have admin access to revoke access.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            OperationalError

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Revoke read access on FeatureStore from user 'BoB'.
            >>> fs.revoke.read('BoB')
            True

            # Example 2: Revoke write access on FeatureStore from user 'BoB'.
            >>> fs.revoke.write('BoB')
            True

            # Example 3: Revoke read and write access on FeatureStore from user 'BoB'.
            >>> fs.revoke.read_write('BoB')
            True
        """
        table_names = {name: UtilFuncs._get_qualified_table_name(self.__repo, table_name)
                       for name, table_name in EFS_TABLES.items()}
        return Revoke(list(table_names.values()))

    def repair(self):
        """
        DESCRIPTION:
            Repairs the existing repo.
            Notes:
                 * The method checks for the corresponding missing database objects which are
                   required for FeatureStore. If any of the database object is not available,
                   then it tries to create the object.
                 * The method repairs only the underlying tables and not data inside the
                   corresponding table.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            TeradatamlException

        EXAMPLES:
            # Repair FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.repair()
            True
            >>>
        """

        # Repair Features, Entities and DataSources first. Then FeatureGroup and then Group Features.
        group_features_ = [EFS_GROUP_FEATURES_STAGING_SPEC, EFS_GROUP_FEATURES_SPEC, EFS_GROUP_FEATURES_TRG, "GroupFeatures"]
        feature_group_ = [EFS_FEATURE_GROUP_STAGING_SPEC, EFS_FEATURE_GROUP_SPEC, EFS_FEATURE_GROUP_TRG, "FeatureGroup"]
        featuers_ = [EFS_FEATURES_STAGING_SPEC, EFS_FEATURES_SPEC, EFS_FEATURES_TRG, "Feature"]
        entities_ = [EFS_ENTITY_STAGING_SPEC, EFS_ENTITY_SPEC, EFS_ENTITY_TRG, "Entity"]
        entities_xref_ = [EFS_ENTITY_XREF_STAGING_SPEC, EFS_ENTITY_XREF_SPEC, EFS_ENTITY_XREF_TRG, "EntityXref"]
        data_sources_ = [EFS_DATA_SOURCE_STAGING_SPEC, EFS_DATA_SOURCE_SPEC, EFS_DATA_SOURCE_TRG, "DataSource"]


        for staging_table_, table_, trigger, obj_name in (group_features_, feature_group_, featuers_, entities_, entities_xref_, data_sources_):
            status = []
            print("Repairing objects related to {}.".format(obj_name))

            status.append(self.__try_create_table(staging_table_))
            status.append(self.__try_create_table(table_))
            status.append(self.__try_create_trigger(trigger, "{}_trg".format(table_["table_name"])))

            # Let user know about status.
            # If any of the status is Bad, then repair is failed.
            # Else, If any of the status is Repaired, then sucessfully repaired.
            #       Else no need to repair the object.
            if self.__bad_status in status:
                print("Unable to repair objects related to {}.".format(obj_name))
            else:
                if self.__repaired_status in status:
                    print("Successfully repaired objects related to {}.".format(obj_name))
                else:
                    print("{} objects are good and do not need any repair.".format(obj_name))

        # Repair the version table.
        status = self.__try_create_table(EFS_VERSION_SPEC)
        if status == self.__repaired_status:
            # After the setup is done, populate the version.
            insert_model = "insert into {}.{} values (?, ?);".format(self.__repo, EFS_VERSION_SPEC["table_name"])
            execute_sql(insert_model, (EFS_VERSION, datetime.datetime.now()))

        return True

    def __try_create_table(self, table_spec):
        """
        DESCRIPTION:
             Internal function to create a table from table spec.

        PARAMETERS:
            table_spec:
                Required Argument.
                Specifies the spec for the corresponding table.
                Types: dict

        RETURNS:
            str
            Note:
                Method can return three different values of strings.
                  * Good - When table to create already exists.
                  * Repaired - When is created.
                  * Bad - When table not exists and method unable to create table.

        RAISES:
            None

        EXAMPLES:
            self.__try_create_table(EFS_VERSION_SPEC)
        """
        try:
            _create_table(table_spec["table_name"],
                          columns=table_spec["columns"],
                          primary_index=table_spec.get("primary_index"),
                          unique=True if table_spec.get("primary_index") else False,
                          schema_name=self.__repo,
                          set_table=False)
            return self.__repaired_status
        except Exception as e:
            if "Table '{}' already exists".format(table_spec["table_name"]) in str(e):
                return self.__good_status
            else:
                print(str(e))
                return self.__bad_status

    def __try_create_trigger(self, trigger_spec, trigger_name):
        """
        DESCRIPTION:
             Internal function to create trigger.

        PARAMETERS:
            trigger_spec:
                Required Argument.
                Specifies the spec for the corresponding trigger.
                Types: str

            trigger_name:
                Required Argument.
                Specifies the name of the trigger to create.
                Types: str

        RETURNS:
            str
            Note:
                Method can return three different values of strings.
                  * Good - When trigger to create already exists.
                  * Repaired - When trigger is created.
                  * Bad - When trigger not exists and method unable to create trigger.

        RAISES:
            None

        EXAMPLES:
            self.__try_create_trigger(EFS_FEATURE_TRIGGER_SPEC)
        """
        try:
            execute_sql(trigger_spec.format(schema_name=self.__repo))
            return self.__repaired_status
        except Exception as e:
            if "Trigger '{}' already exists".format(trigger_name) in str(e):
                return self.__good_status
            else:
                print("Unable to create trigger '{}'. Error - {}".format(trigger_name, str(e)))
                return self.__bad_status

    def list_features(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the features.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective features or archived features.
                When set to False, effective features in FeatureStore are listed,
                otherwise, archived features are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            >>> load_example_data('dataframe', 'sales')
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create a FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name='sales',
            ...                                  entity_columns='accounts',
            ...                                  df=df,
            ...                                  timestamp_col_name='datetime')
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective Features in the repo 'vfs_v1'.
            >>> fs.list_features()
                 column_name description               creation_time modified_time  tags data_type feature_type  status group_name
            name
            Mar          Mar        None  2024-09-30 11:21:43.314118          None  None    BIGINT   CONTINUOUS  ACTIVE      sales
            Jan          Jan        None  2024-09-30 11:21:42.655343          None  None    BIGINT   CONTINUOUS  ACTIVE      sales
            Apr          Apr        None  2024-09-30 11:21:44.143402          None  None    BIGINT   CONTINUOUS  ACTIVE      sales
            Feb          Feb        None  2024-09-30 11:21:41.542627          None  None     FLOAT   CONTINUOUS  ACTIVE      sales
            >>>

            # Example 2: List all the archived Features in the repo 'vfs_v1'.
            # Note: Feature can only be archived when it is not associated with any Group.
            #       Let's remove Feature 'Feb' from FeatureGroup.
            >>> fg.remove(fs.get_feature('Feb'))
            True
            # Apply the modified FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True
            # Archive Feature 'Feb'.
            >>> fs.archive_feature('Feb')
            Feature 'Feb' is archived.
            True

            # List all the archived Features in the repo 'vfs_v1'.
            >>> fs.list_features(archived=True)
              name column_name description               creation_time modified_time  tags data_type feature_type  status               archived_time group_name
            0  Feb         Feb        None  2024-09-30 11:21:41.542627          None  None     FLOAT   CONTINUOUS  ACTIVE  2024-09-30 11:30:49.160000      sales
            >>>
        """
        return self.__get_archived_features_df() if archived else self.__get_features_df()

    def list_entities(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the entities.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective entities or archived entities.
                When set to False, effective entities in FeatureStore are listed,
                otherwise, archived entities are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            >>> load_example_data('dataframe', 'sales')
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create a FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name='sales',
            ...                                  entity_columns='accounts',
            ...                                  df=df,
            ...                                  timestamp_col_name='datetime')
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective Entities in the repo 'vfs_v1'.
            >>> fs.list_entities()
                                description
            name  entity_column
            sales accounts             None
            >>>

            # Example 2: List all the archived Entities in the repo 'vfs_v1'.
            # Note: Entity cannot be archived if it is a part of FeatureGroup.
            #       First create another Entity, and update FeatureGroup with
            #       other Entity. Then archive Entity 'sales'.
            >>> entity = Entity('store_sales', columns=df.accounts)
            # Update new entity to FeatureGroup.
            >>> fg.apply(entity)
            # Update FeatureGroup to FeatureStore. This will update Entity
            #    from 'sales' to 'store_sales' for FeatureGroup 'sales'.
            >>> fs.apply(fg)
            True
            # Let's archive Entity 'sales' since it is not part of any FeatureGroup.
            >>> fs.archive_entity('sales')
            Entity 'sales' is archived.
            True
            >>>

            # List the archived entities.
            >>> fs.list_entities(archived=True)
                name description               creation_time modified_time               archived_time entity_column
            0  sales        None  2024-10-18 05:41:36.932856          None  2024-10-18 05:50:00.930000      accounts
            >>>
        """
        return self.__get_archived_entity_df() if archived else self.__get_entity_df()

    def list_data_sources(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the Data Sources.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective data sources or archived data sources.
                When set to False, effective data sources in FeatureStore are listed,
                otherwise, archived data sources are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, FeatureStore, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Create teradataml DataFrame.
            >>> admissions=DataFrame("admissions_train")
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Create DataSource using teradataml DataFrame.
            >>> ds = DataSource(name='admissions', source=admissions)
            # Apply the DataSource to FeatureStore.
            >>> fs.apply(ds)
            True

            # Example 1: List all the effective DataSources in the repo 'vfs_v1'.
            >>> fs.list_data_sources()
                       description timestamp_col_name                            source
            name
            admissions        None               None  select * from "admissions_train"
            >>>

            # Example 2: List all the archived DataSources in the repo 'vfs_v1'.
            # Let's first archive the DataSource.
            >>> fs.archive_data_source('admissions')
            DataSource 'admissions' is archived.
            True
            # List archived DataSources.
            >>> fs.list_data_sources(archived=True)
                       description timestamp_col_name                            source               archived_time
            name
            admissions        None               None  select * from "admissions_train"  2024-09-30 12:05:39.220000
            >>>
        """
        return self.__get_archived_data_source_df() if archived else self.__get_data_source_df()

    def list_feature_groups(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the FeatureGroups.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective feature groups or archived feature groups.
                When set to False, effective feature groups in FeatureStore are listed,
                otherwise, archived feature groups are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureGroup, FeatureStore, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Create teradataml DataFrame.
            >>> admissions=DataFrame("admissions_train")
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Create a FeatureGroup from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame("admissions", df=admissions, entity_columns='id')
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective FeatureGroups in the repo 'vfs_v1'.
            >>> fs.list_feature_groups()
                       description data_source_name entity_name
            name
            admissions        None       admissions  admissions
            >>>

            # Example 2: List all the archived FeatureGroups in the repo 'vfs_v1'.
            # Let's first archive the FeatureGroup.
            >>> fs.archive_feature_group("admissions")
            True
            >>>
            # List archived FeatureGroups.
            >>> fs.list_feature_groups(archived=True)
                     name description data_source_name entity_name               archived_time
            0  admissions        None       admissions  admissions  2024-09-30 12:05:39.220000
            >>>
        """
        return self.__get_archived_feature_group_df() if archived else self.__get_feature_group_df()

    def get_feature(self, name):
        """
        DESCRIPTION:
            Retrieve the feature.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the feature to get.
                Types: str

        RETURNS:
            Feature.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Load the sales data to Vantage.
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame on sales data.
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            >>>
            # Create Feature for column 'Mar' with name 'sales_mar'.
            >>> feature = Feature('sales_mar', column=df.Mar)
            # Apply the Feature to FeatureStore.
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.apply(feature)
            True

            # Get the feature 'sales_mar' from repo 'vfs_v1'.
            >>> feature = fs.get_feature('sales_mar')
            >>> feature
            Feature(name=sales_mar)
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.list_features()
        df = df[df.name == name]

        # Check if a feature with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(
                msg_code, "get_feature()", "Feature with name '{}' does not exist.".format(name))
            raise TeradataMlException(error_msg, msg_code)

        return Feature._from_df(df)

    def get_group_features(self, group_name):
        """
        DESCRIPTION:
            Get the Features from the given feature group name.

        PARAMETERS:
            group_name:
                Required Argument.
                Specifies the name of the group the feature belongs to.
                Types: str

        RETURNS:
            List of Feature objects.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Load the sales data to Vantage.
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame on sales data.
            >>> df = DataFrame("sales")
            >>> df
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            >>>
            # Create FeatureGroup with name 'sales' from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(
            ...    name="sales", df=df, entity_columns="accounts", timestamp_col_name="datetime")
            # Apply the FeatureGroup to FeatureStore.
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.apply(fg)
            True

            # Get all the features belongs to the group 'sales' from repo 'vfs_v1'.
            >>> features = fs.get_group_features('sales')
            >>> features
            [Feature(name=Jan), Feature(name=Feb), Feature(name=Apr), Feature(name=Mar)]
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["group_name", group_name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Select active features.
        features_df = self.__get_features_df()
        features_df = features_df[((features_df.status != FeatureStatus.INACTIVE.name) & (features_df.group_name == group_name))]

        # Check if a feature with that group name exists or not. If not, raise error.
        if features_df.shape[0] == 0:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(
                msg_code, "get_group_features()", "No features found for group '{}'.".format(group_name))
            raise TeradataMlException(error_msg, msg_code)

        return Feature._from_df(features_df)

    def get_feature_group(self, name):
        """
        DESCRIPTION:
            Retrieve the FeatureGroup using name.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the feature group to be retrieved.
                Types: str

        RETURNS:
            Object of FeatureGroup

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Load the sales data to Vantage.
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame on sales data.
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            >>>
            # Create FeatureGroup with name 'sales' from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(
            ...    name="sales", df=df, entity_columns="accounts", timestamp_col_name="datetime")
            # Apply the FeatureGroup to FeatureStore.
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.apply(fg)
            True

            # Get FeatureGroup with group name 'sales' from repo 'vfs_v1'.
            >>> fg = fs.get_feature_group('sales')
            >>> fg
            FeatureGroup(sales, features=[Feature(name=Jan), Feature(name=Feb), Feature(name=Apr), Feature(name=Mar)], entity=Entity(name=sales), data_source=DataSource(name=sales))
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.list_feature_groups()
        df = df[df.name == name]

        # Check if a feature with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(
                msg_code, "get_feature_group()", "FeatureGroup with name '{}' does not exist.".format(name))
            raise TeradataMlException(error_msg, msg_code)

        return FeatureGroup._from_df(df,
                                     self.__repo,
                                     self.__get_features_df(),
                                     self.__get_entity_df(),
                                     self.__get_data_source_df()
                                     )

    def get_entity(self, name):
        """
        DESCRIPTION:
            Get the entity from feature store.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the entity.
                Types: str

        RETURNS:
            Object of Entity.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore, load_example_data
            # Load the admissions data to Vantage.
            >>> load_example_data("dataframe", "admissions_train")
            # Create DataFrame on admissions data.
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1
            >>>
            # Create Entity for column 'id' with name 'admissions_id'.
            >>> entity = Entity(name='admissions_id', description="Entity for admissions", columns=df.id)
            # Apply the Entity to FeatureStore 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(entity)
            True
            >>>

            # Get the Entity 'admissions_id' from repo 'vfs_v1'
            >>> entity = fs.get_entity('admissions_id')
            >>> entity
            Entity(name=admissions_id)
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.__get_entity_df()
        df = df[df.name==name]

        # Check if entity with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(
                msg_code, "get_entity()", "Entity with name '{}' does not exist.".format(name))
            raise TeradataMlException(error_msg, msg_code)
        return Entity._from_df(df)

    def get_data_source(self, name):
        """
        DESCRIPTION:
            Get the data source from feature store.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the data source.
                Types: str

        RETURNS:
            Object of DataSource.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Load the admissions data to Vantage.
            >>> load_example_data("dataframe", "admissions_train")
            # Create DataFrame on admissions data.
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1
            >>>
            # Create DataSource using DataFrame 'df' with name 'admissions'.
            >>> ds = DataSource('admissions', source=df)
            # Apply the DataSource to FeatureStore 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(ds)
            True
            >>>

            # Get the DataSource 'admissions' from repo 'vfs_v1'
            >>> ds = fs.get_data_source('admissions')
            >>> ds
            DataSource(name=admissions)
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.__get_data_source_df()
        df = df[df.name == name]

        # Check if a entity with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(
                msg_code, "get_data_source()", "DataSource with name '{}' does not exist.".format(name))
            raise TeradataMlException(error_msg, msg_code)

        return DataSource._from_df(df)

    def set_features_inactive(self, names):
        """
        DESCRIPTION:
            Mark the feature status as 'inactive'. Note that, inactive features are
            not available for any further processing. Set the status as 'active' with
            "set_features_active()" method.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name(s) of the feature(s).
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Load the admissions data to Vantage.
            >>> load_example_data("dataframe", "admissions_train")
            # Create DataFrame on admissions data.
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1
            >>>
            # Create FeatureGroup from DataFrame df.
            >>> fg = FeatureGroup.from_DataFrame(name='admissions', df=df, entity_columns='id')
            # Apply the FeatureGroup to FeatureStore 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(fg)
            True
            # Get FeatureGroup 'admissions' from FeatureStore.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))

            # Set the Feature 'programming' inactive.
            >>> fs.set_features_inactive('programming')
            True
            # Get FeatureGroup again after setting feature inactive.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=stats), Feature(name=admitted), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            >>>
        """
        return self.__set_active_inactive_features(names, active=False)

    def set_features_active(self, names):
        """
        DESCRIPTION:
            Mark the feature status as active. Set the status as 'inactive' with
            "set_features_inactive()" method. Note that, inactive features are
            not available for any further processing.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name(s) of the feature(s).
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Load the admissions data to Vantage.
            >>> load_example_data("dataframe", "admissions_train")
            # Create DataFrame on admissions data.
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1
            >>>
            # Create FeatureGroup from DataFrame df.
            >>> fg = FeatureGroup.from_DataFrame(name='admissions', df=df, entity_columns='id')
            # Apply the FeatureGroup to FeatureStore 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(fg)
            True
            # Get FeatureGroup 'admissions' from FeatureStore.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            # Set the Feature 'programming' inactive.
            >>> fs.set_features_inactive('programming')
            True
            # Get FeatureGroup again after setting feature inactive.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=stats), Feature(name=admitted), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            >>>

            # Mark Feature 'programming' from 'inactive' to 'active'.
            >>> fs.set_features_active('programming')
            # Get FeatureGroup again after setting feature active.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            >>>
        """
        return self.__set_active_inactive_features(names, active=True)

    def __set_active_inactive_features(self, names, active):
        """
        DESCRIPTION:
            Internal function to either active or inactive features.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name the feature.
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            # Example 1: Archive the feature 'feature1' in the repo
            #            'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.__archive_unarchive_features(name='feature1')
            True
            >>>
        """
        names = UtilFuncs._as_list(names)

        argument_validation_params = []
        argument_validation_params.append(["names", names, False, (str, list), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        status = FeatureStatus.ACTIVE.name if active else FeatureStatus.INACTIVE.name

        _update_data(table_name=EFS_FEATURES_SPEC["table_name"],
                     schema_name=self.__repo,
                     update_columns_values={"status": status},
                     update_conditions={"name": names}
                     )
        return True

    def apply(self, object):
        """
        DESCRIPTION:
            Register objects to repository.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to update the repository.
                Types: Feature OR DataSource OR Entity OR FeatureGroup.

        RETURNS:
            bool.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a Feature for column 'Feb' from 'sales' DataFrame
            #            and register with repo 'vfs_v1'.
            >>> # Create Feature.
            >>> from teradataml import Feature
            >>> feature = Feature('sales:Feb', df.Feb)
            >>> # Register the above Feature with repo.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(feature)
            True
            >>>

            # Example 2: create Entity for 'sales' DataFrame and register
            #            with repo 'vfs_v1'.
            >>> # Create Entity.
            >>> from teradataml import Entity
            >>> entity = Entity('sales:accounts', df.accounts)
            >>> # Register the above Entity with repo.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(entity)
            True
            >>>

            # Example 3: create DataSource for 'sales' DataFrame and register
            #            with repo 'vfs_v1'.
            >>> # Create DataSource.
            >>> from teradataml import DataSource
            >>> ds = DataSource('Sales_Data', df)
            >>> # Register the above DataSource with repo.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(ds)
            True
            >>>

            # Example 4: create FeatureStore with all the objects
            #            created in above examples and register with
            #            repo 'vfs_v1'.
            >>> # Create FeatureGroup.
            >>> from teradataml import FeatureGroup
            >>> fg = FeatureGroup('Sales',
            ...                   features=feature,
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> # Register the above FeatureStore with repo.
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.apply(fg)
            True
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", object, False, (Feature, Entity, DataSource, FeatureGroup)])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        return object.publish(self.__repo)

    def get_dataset(self, group_name):
        """
        DESCRIPTION:
            Returns teradataml DataFrame based on "group_name".

        PARAMETERS:
            group_name:
                Required Argument.
                Specifies the name of the feature group.
                Types: str

        RETURNS:
            teradataml DataFrame.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Load the sales data to Vantage.
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame on sales data.
            >>> df = DataFrame("sales")
            >>> df
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            >>>
            # Create FeatureGroup with name 'sales' from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(
            ...    name="sales", df=df, entity_columns="accounts", timestamp_col_name="datetime")
            # Apply the FeatureGroup to FeatureStore.
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.apply(fg)
            True

            # Get the DataSet for FeatureGroup 'sales'
            >>> df = fs.get_dataset('sales')
            >>> df
                          datetime    Jan    Feb    Apr    Mar
            accounts
            Orange Inc  04/01/2017    NaN  210.0  250.0    NaN
            Jones LLC   04/01/2017  150.0  200.0  180.0  140.0
            Blue Inc    04/01/2017   50.0   90.0  101.0   95.0
            Alpha Co    04/01/2017  200.0  210.0  250.0  215.0
            Yellow Inc  04/01/2017    NaN   90.0    NaN    NaN
            >>>
        """
        # Get the FeatureGroup first and extract all details.
        feature_group = self.get_feature_group(group_name)
        columns = [feature.column_name for feature in feature_group.features
                   if feature.status != FeatureStatus.INACTIVE]
        entity_columns = feature_group.entity.columns
        source = feature_group.data_source.source

        # Create DF from the source.
        df = DataFrame.from_query(source)

        # Select the corresponding columns.
        required_columns = entity_columns + columns
        if feature_group.data_source.timestamp_col_name:
            columns = [col for col in columns if col != feature_group.data_source.timestamp_col_name]
            required_columns = entity_columns + [feature_group.data_source.timestamp_col_name] + columns
        return df.select(required_columns)

    def __get_feature_group_names(self, name, type_):
        """
        DESCRIPTION:
            Internal function to get the associated group names for
            Feature or DataSource OR Entity.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Feature or DataSource or Entity.
                Types: str

            type_:
                 Required Argument.
                 Specifies the type of the objects stored in feature store.
                 Permitted Values:
                    * feature
                    * data_source
                    * entity
                 Types: str

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            >>> self.__get_feature_group_names('admissions', 'data_source')
        """
        if type_ == "feature":
            df = self.__get_features_df()
            return [rec.group_name for rec in df[df.name == name].itertuples() if rec.group_name is not None]
        elif type_ == "data_source":
            df = self.__get_feature_group_df()
            return [rec.name for rec in df[df.data_source_name == name].itertuples()]
        elif type_ == "entity":
            df = self.__get_feature_group_df()
            return [rec.name for rec in df[df.entity_name == name].itertuples()]

    def __remove_obj(self, name, type_, action="archive"):
        """
        DESCRIPTION:
            Internal function to get the remove Feature or DataSource OR
            Entity from repo.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Feature or DataSource or Entity.
                Types: str

            type_:
                 Required Argument.
                 Specifies the type of "name".
                 Types: str
                 Permitted Values:
                    * feature
                    * data_source
                    * entity

            action:
                 Optional Argument.
                 Specifies whether to remove from staging tables or not.
                 When set to True, object is removed from staging tables.
                 Otherwise, object is fetched from regular tables.
                 Default Value: True
                 Types: bool

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> self.__remove_obj('admissions', 'data_source')
        """
        _vars = {
            "data_source": {"class": DataSource, "error_msg": "Update these FeatureGroups with other DataSources"},
            "entity": {"class": Entity, "error_msg": "Update these FeatureGroups with other Entities"},
            "feature": {"class": Feature, "error_msg": "Remove the Feature from FeatureGroup"},
        }
        c_name_ = _vars[type_]["class"].__name__
        argument_validation_params = []
        argument_validation_params.append([type_, name, False, (str, _vars[type_]["class"]), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        # Extract the name if argument is class type.
        if isinstance(name, _vars[type_]["class"]):
            name = name.name

        # Before removing it, check if it is associated with any FeatureGroup.
        # If yes, raise error. Applicable only for Archive.
        if action == "archive":
            feature_groups = self.__get_feature_group_names(name, type_)
            if feature_groups:
                feature_groups = ", ".join(("'{}'".format(fg) for fg in feature_groups))
                message = ("{} '{}' is associated with FeatureGroups {}. {} and try deleting again.".format(
                    c_name_, name, feature_groups, _vars[type_]["error_msg"]))
                raise TeradataMlException(Messages.get_message(
                    MessageCodes.FUNC_EXECUTION_FAILED, '{}_{}'.format(action, type_), message),
                    MessageCodes.FUNC_EXECUTION_FAILED)

        if type_ == "entity":
            res = self._remove_entity(name, action)
        else:
            table_name = self.__table_names[type_]
            if action == "delete":
                table_name = self.__table_names["{}_staging".format(type_)]

            res = _delete_data(table_name=table_name,
                               schema_name=self.__repo,
                               delete_conditions=(Col("name") == name)
                               )

        if res == 1:
            print("{} '{}' is {}d.".format(c_name_, name, action))
            return True
        else:
            print("{} '{}' does not exist to {}.".format(c_name_, name, action))
            return False

    @db_transaction
    def _remove_entity(self, name, action):
        """
        DESCRIPTION:
            Internal function to get the remove Entity from repo.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Entity.
                Types: str

            action:
                 Required Argument.
                 Specifies whether to remove from staging tables or not.
                 When set to "delete", Entity is removed from staging tables.
                 Otherwise, Entity is removed from regular tables.
                 Types: str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> self._remove_entity('admissions', 'delete')
        """
        ent_table = self.__table_names["entity"]
        ent_table_xref = self.__table_names["entity_xref"]
        if action == "delete":
            ent_table = self.__table_names["entity_staging"]
            ent_table_xref = self.__table_names["entity_staging_xref"]

        # remove it from xref table first.
        _delete_data(table_name=ent_table_xref,
                     schema_name=self.__repo,
                     delete_conditions=(Col("entity_name") == name)
                     )

        # remove from entity table.
        res = _delete_data(table_name=ent_table,
                           schema_name=self.__repo,
                           delete_conditions=(Col("name") == name)
                           )

        return res

    def archive_data_source(self, data_source):
        """
        DESCRIPTION:
            Archives DataSource from repository. Note that archived DataSource
            is not available for any further processing. Archived DataSource can be 
            viewed using "list_archived_data_sources()" method.

        PARAMETERS:
            data_source:
                Required Argument.
                Specifies either the name of DataSource or Object of DataSource
                to archive from repository.
                Types: str OR DataSource

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataSource, FeatureStore, load_example_data
            # Create a DataSource using SELECT statement.
            >>> ds = DataSource(name="sales_data", source="select * from sales")
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Apply DataSource to FeatureStore.
            >>> fs.apply(ds)
            True
            # List the available DataSources.
            >>> fs.list_data_sources()
                       description timestamp_col_name               source
            name
            sales_data        None               None  select * from sales

            # Archive DataSource with name "sales_data".
            >>> fs.archive_data_source("sales_data")
            DataSource 'sales_data' is archived.
            True
            >>>
            # List the available DataSources after archive.
            >>> fs.list_data_sources()
            Empty DataFrame
            Columns: [description, timestamp_col_name, source]
            Index: []
        """
        return self.__remove_obj(name=data_source, type_="data_source")

    def delete_data_source(self, data_source):
        """
        DESCRIPTION:
            Removes the archived DataSource from repository.

        PARAMETERS:
            data_source:
                Required Argument.
                Specifies either the name of DataSource or Object of DataSource
                to remove from repository.
                Types: str OR DataSource

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create DataSource with source as teradataml DataFrame.
            >>> ds = DataSource(name="sales_data", source=df)
            # # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            # Apply the DataSource to FeatureStore.
            >>> fs.apply(ds)
            True
            # Let's first archive the DataSource.
            >>> fs.archive_data_source("sales_data")
            DataSource 'sales_data' is archived.
            True

            # Delete DataSource with name "sales_data".
            >>> fs.delete_data_source("sales_data")
            DataSource 'sales_data' is deleted.
            True
            >>>
        """
        return self.__remove_obj(name=data_source, type_="data_source", action="delete")

    def archive_feature(self, feature):
        """
        DESCRIPTION:
            Archives Feature from repository. Note that archived Feature
            is not available for any further processing. Archived Feature can be
            viewed using "list_archived_features()" method.

        PARAMETERS:
            feature:
                Required Argument.
                Specifies either the name of Feature or Object of Feature
                to archive from repository.
                Types: str OR Feature

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create Feature for Column 'Feb'.
            >>> feature = Feature(name="sales_data_Feb", column=df.Feb)
            # Create FeatureStore for the repo 'staging_repo'.
            >>> fs = FeatureStore("staging_repo")
            # Apply the Feature to FeatureStore.
            >>> fs.apply(feature)
            True
            # List the available Features.
            >>> fs.list_features()
                           column_name description               creation_time modified_time  tags data_type feature_type  status group_name
            name
            sales_data_Feb         Feb        None  2024-10-03 18:21:03.720464          None  None     FLOAT   CONTINUOUS  ACTIVE       None

            # Archive Feature with name "sales_data_Feb".
            >>> fs.archive_feature(feature=feature)
            Feature 'sales_data_Feb' is archived.
            True
            # List the available Features after archive.
            >>> fs.list_features()
            Empty DataFrame
            Columns: [column_name, description, creation_time, modified_time, tags, data_type, feature_type, status, group_name]
            Index: []
            >>>
        """
        return self.__remove_obj(name=feature, type_="feature")

    def delete(self):
        """
        DESCRIPTION:
            Removes the FeatureStore and its components from repository.
            Notes:
                 * The function removes all the associated database objects along with data.
                   Be cautious while using this function.
                 * The function tries to remove the underlying Database also once
                   all the Feature Store objects are removed.
                 * The user must have permission on the database used by this Feature Store
                    * to drop triggers.
                    * to drop the tables.
                    * to drop the Database.
                 * If the user lacks any of the mentioned permissions, Teradata recommends
                   to not use this function.

        PARAMETERS:
            None

        RETURNS:
            bool.

        RAISES:
            None

        EXAMPLES:
            # Setup FeatureStore for repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_v1")
            >>> fs.setup()
            True
            >>> # Delete FeatureStore.
            >>> fs.delete()
            True
            >>>
        """
        confirmation = input("The function removes Feature Store and drops the "
                             "corresponding repo also. Are you sure you want to proceed? (Y/N): ")

        if confirmation in ["Y", "y"]:
            return self.__drop_feature_store_objects(self.__repo)

        return False

    @staticmethod
    def __drop_feature_store_objects(repo_name):
        """
        DESCRIPTION:
            Removes the FeatureStore and it's components from repository.

        PARAMETERS:
            repo_name:
                Required Argument.
                Specifies the name of the repository.
                Types: str

        RETURNS:
            bool
        """
        # Drop all the tables and staging tables.
        tables_ = [
            EFS_GROUP_FEATURES_SPEC["table_name"],
            EFS_FEATURE_GROUP_SPEC["table_name"],
            EFS_FEATURES_SPEC['table_name'],
            EFS_ENTITY_XREF_SPEC['table_name'],
            EFS_ENTITY_SPEC["table_name"],
            EFS_DATA_SOURCE_SPEC["table_name"]
        ]

        tables_stg_ = [
            EFS_FEATURES_STAGING_SPEC['table_name'],
            EFS_ENTITY_STAGING_SPEC["table_name"],
            EFS_ENTITY_XREF_STAGING_SPEC["table_name"],
            EFS_DATA_SOURCE_STAGING_SPEC["table_name"],
            EFS_FEATURE_GROUP_STAGING_SPEC["table_name"],
            EFS_GROUP_FEATURES_STAGING_SPEC["table_name"]
        ]

        # Drop all the triggers first. So that tables can be dropped.
        triggers = ["{}_trg".format(table) for table in tables_]
        for trigger in triggers:
            execute_sql("drop trigger {}.{}".format(repo_name, trigger))

        for table in (tables_ + [EFS_VERSION_SPEC["table_name"]] + tables_stg_):
            db_drop_table(table, schema_name=repo_name)

        execute_sql("DROP DATABASE {}".format(repo_name))

        return True

    def delete_feature(self, feature):
        """
        DESCRIPTION:
            Removes the archived Feature from repository.

        PARAMETERS:
            feature:
                Required Argument.
                Specifies either the name of Feature or Object of Feature
                to remove from repository.
                Types: str OR Feature

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create Feature for Column 'Feb'.
            >>> feature = Feature(name="sales_data_Feb", column=df.Feb)
            # Create a feature store with name "staging_repo".
            >>> fs = FeatureStore("staging_repo")
            # Add the feature created above in the feature store.
            >>> fs.apply(feature)
            True
            # Let's first archive the Feature.
            >>> fs.archive_feature(feature=feature)
            Feature 'sales_data_Feb' is archived.
            True

            # Delete Feature with name "sales_data_Feb".
            >>> fs.delete_feature(feature=feature)
            Feature 'sales_data_Feb' is deleted.
            True
            >>>
        """
        return self.__remove_obj(name=feature, type_="feature", action="delete")

    def archive_entity(self, entity):
        """
        DESCRIPTION:
            Archives Entity from repository. Note that archived Entity
            is not available for any further processing. Archived Entity can be
            viewed using "list_archived_entities()" method.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies either the name of Entity or Object of Entity
                to remove from repository.
                Types: str OR Entity

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create Entity using teradataml DataFrame Column.
            >>> entity = Entity(name="sales_data", columns=df.accounts)
            # Create FeatureStore for repo 'staging_repo'.
            >>> fs = FeatureStore("staging_repo")
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity)
            True
            # List all the available entities.
            >>> fs.list_entities()
                                     description
            name       entity_column
            sales_data accounts             None

            # Archive Entity with name "sales_data".
            >>> fs.archive_entity(entity=entity.name)
            Entity 'sales_data' is archived.
            True
            # List the entities after archive.
            >>> fs.list_entities()
            Empty DataFrame
            Columns: [description]
            Index: []
        """
        return self.__remove_obj(name=entity, type_="entity")

    def delete_entity(self, entity):
        """
        DESCRIPTION:
            Removes archived Entity from repository.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies either the name of Entity or Object of Entity
                to delete from repository.
                Types: str OR Entity

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create Entity using teradataml DataFrame Column.
            >>> entity = Entity(name="sales_data", columns=df.accounts)
            # Create FeatureStore for repo 'staging_repo'.
            >>> fs = FeatureStore("staging_repo")
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity)
            True
            # Let's first archive the entity.
            >>> fs.archive_entity(entity=entity.name)
            Entity 'sales_data' is archived.
            True

            # Delete Entity with name "sales_data".
            >>> fs.delete_entity(entity=entity.name)
            Entity 'sales_data' is deleted.
            True
            >>>
        """
        return self.__remove_obj(name=entity, type_="entity", action="delete")

    def __get_features_where_clause(self, features):
        """
        Internal function to prepare a where clause on features df.
        """
        col_expr = Col("name") == features[0]
        for feature in features[1:]:
            col_expr = ((col_expr) | (Col("name") == feature))

        return col_expr

    def archive_feature_group(self, feature_group):
        """
        DESCRIPTION:
            Archives FeatureGroup from repository. Note that archived FeatureGroup
            is not available for any further processing. Archived FeatureGroup can be
            viewed using "list_archived_feature_groups()" method.
            Note:
                The function archives the associated Features, Entity and DataSource
                if they are not associated with any other FeatureGroups.

        PARAMETERS:
            feature_group:
                Required Argument.
                Specifies either the name of FeatureGroup or Object of FeatureGroup
                to archive from repository.
                Types: str OR FeatureGroup

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureGroup, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df, timestamp_col_name="datetime")
            # Create FeatureStore for the repo 'staging_repo'.
            >>> fs = FeatureStore("staging_repo")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True
            # List all the available FeatureGroups.
            >>> fs.list_feature_groups()
                  description data_source_name entity_name
            name
            sales        None            sales       sales

            # Archive FeatureGroup with name "sales".
            >>> fs.archive_feature_group(feature_group='sales')
            FeatureGroup 'sales' is archived.
            True
            >>>
            # List all the available FeatureGroups after archive.
            >>> fs.list_feature_groups()
            Empty DataFrame
            Columns: [description, data_source_name, entity_name]
            Index: []
        """
        argument_validation_params = []
        argument_validation_params.append(["feature_group", feature_group, False, (str, FeatureGroup), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        feature_group_name = feature_group if isinstance(feature_group, str) else feature_group.name

        fg = self.get_feature_group(feature_group_name) if isinstance(feature_group, str) else feature_group

        fg_df = self.list_feature_groups()

        # Find out shared Features. Extract the features which are mapped to
        # other groups. They can not be deleted.
        feature_names = [f.name for f in fg.features]
        features_df = self.list_features()
        col_expr = self.__get_features_where_clause(feature_names)
        features_df = features_df[((features_df.group_name != fg.name) & (col_expr))]
        shared_features = [f.name for f in features_df.drop_duplicate('name').itertuples()]
        feature_names_to_remove = [f for f in feature_names if f not in shared_features]

        # Find out shared Entities. If entity is not shared, then update 'entity_name'
        # to update value.
        entity_name = None
        ent = fg_df[((fg_df.entity_name == fg.entity.name) & (fg_df.name != fg.name))]
        recs = ent.shape[0]
        if recs == 0:
            entity_name = fg.entity.name

        # Find out shared DataSources. If datasource is not shared, then update 'data_source_name'.
        data_source_name = None
        ds_df = fg_df[((fg_df.data_source_name == fg.data_source.name) & (fg_df.name != fg.name))]
        recs = ds_df.shape[0]
        if recs == 0:
            data_source_name = fg.data_source.name

        res = self._archive_feature_group(fg.name, feature_names_to_remove, entity_name, data_source_name)

        if res == 1:
            print("FeatureGroup '{}' is archived.".format(feature_group_name))
            return True

        print("FeatureGroup '{}' not exist to archive.".format(feature_group_name))
        return False

    @db_transaction
    def _archive_feature_group(self, group_name, feature_names, entity_name, data_source_name):
        """
        DESCRIPTION:
            Internal method to archive FeatureGroup from repository.

        PARAMETERS:
            group_name:
                Required Argument.
                Specifies the name of FeatureGroup to archive from repository.
                Types: str

            feature_names:
                Required Argument.
                Specifies the name of Features to archive from repository.
                Types: list

            entity_name:
                Required Argument.
                Specifies the name of Entity to archive from repository.
                Types: str

            data_source_name:
                Required Argument.
                Specifies the name of DataSource to archive from repository.
                Types: str

        RETURNS:
            bool.

        RAISES:
            OperationalError

        EXAMPLES:
            >>> self._archive_feature_group("group1", ["feature1"], "entity_name", None)
        """
        # Remove data for FeatureGroup from Xref table.
        # This allows to remove data from other tables.
        res = _delete_data(schema_name=self.__repo,
                           table_name=EFS_GROUP_FEATURES_SPEC["table_name"],
                           delete_conditions=(Col("group_name") == group_name)
                           )

        # Remove FeatureGroup.
        res = _delete_data(schema_name=self.__repo,
                           table_name=EFS_FEATURE_GROUP_SPEC["table_name"],
                           delete_conditions=(Col("name") == group_name)
                           )

        # Remove Features.
        if feature_names:
            _delete_data(schema_name=self.__repo,
                         table_name=EFS_FEATURES_SPEC["table_name"],
                         delete_conditions=self.__get_features_where_clause(feature_names)
                         )

        # Remove entities.
        if entity_name:
            _delete_data(schema_name=self.__repo,
                         table_name=EFS_ENTITY_XREF_SPEC["table_name"],
                         delete_conditions=(Col("entity_name") == entity_name)
                         )

            _delete_data(schema_name=self.__repo,
                         table_name=EFS_ENTITY_SPEC["table_name"],
                         delete_conditions=(Col("name") == entity_name)
                         )

        # Remove DataSource.
        if data_source_name:
            _delete_data(schema_name=self.__repo,
                         table_name=EFS_DATA_SOURCE_SPEC["table_name"],
                         delete_conditions=(Col("name") == data_source_name),
                         )

        return res

    @db_transaction
    def delete_feature_group(self, feature_group):
        """
        DESCRIPTION:
            Removes archived FeatureGroup from repository.
            Note:
                Unlike 'archive_feature_group()', this function does not delete the
                associated Features, Entity and DataSource. One should delete those
                using 'delete_feature()', 'delete_entity()' and 'delete_data_source()'.

        PARAMETERS:
            feature_group:
                Required Argument.
                Specifies either the name of FeatureGroup or Object of FeatureGroup
                to delete from repository.
                Types: str OR FeatureGroup

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureGroup, FeatureStore
            >>> load_example_data('dataframe', ['sales'])
            # Create teradataml DataFrame.
            >>> df = DataFrame("sales")
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df, timestamp_col_name="datetime")
            # Create FeatureStore for the repo 'staging_repo'.
            >>> fs = FeatureStore("staging_repo")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True
            # Let's first archive FeatureGroup with name "sales".
            >>> fs.archive_feature_group(feature_group='sales')
            FeatureGroup 'sales' is archived.
            True

            # Delete FeatureGroup with name "sales".
            >>> fs.delete_feature_group(feature_group='sales')
            FeatureGroup 'sales' is deleted.
            True
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["feature_group", feature_group, False, (str, FeatureGroup), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        fg_name = feature_group if isinstance(feature_group, str) else feature_group.name

        # Remove data for FeatureGroup.
        _delete_data(table_name=self.__table_names["group_features_staging"],
                     schema_name=self.__repo,
                     delete_conditions=(Col("group_name") == fg_name)
                     )

        res = _delete_data(table_name=self.__table_names["feature_group_staging"],
                           schema_name=self.__repo,
                           delete_conditions=(Col("name") == fg_name)
                           )

        if res == 1:
            print("FeatureGroup '{}' is deleted.".format(fg_name))
            return True

        print("FeatureGroup '{}' not exist to delete.".format(fg_name))
        return False

    def __get_obj_df(self, obj_type):
        """
        DESCRIPTION:
            Internal method to return either Features DataFrame OR Entity DataFrame
            OR DataSource DataFrame OR FeatureGroup DataFrame.

        PARAMETERS:
            obj_type
                Required Argument.
                Specifies the type of DataFrame to return.
                Allowed Values:
                    * feature
                    * feature_group
                    * entity
                    * data_source
                    * group_features

        RETURNS:
            teradataml DataFrame.

        RAISES:
            None

        EXAMPLES:
            fs.__get_features_df()
        """
        if obj_type not in self.__df_container:
            from teradataml.dataframe.dataframe import in_schema

            # For feature or feature_staging, join it with xref table
            # so group name appears while listing features.
            map_ = {"feature": "group_features", "feature_staging": "group_features_staging"}
            if obj_type in map_:
                features = DataFrame(in_schema(self.__repo, self.__table_names[obj_type]))
                features_xref = DataFrame(in_schema(self.__repo, self.__table_names[map_[obj_type]])).select(
                    ["feature_name", "group_name"])
                df = features.join(features_xref, on="name==feature_name", how='left')
                self.__df_container[obj_type] = df.select(features.columns+["group_name"])
            # For entity, join with xref table.
            elif obj_type == "entity" or obj_type == "entity_staging":
                ent_df = DataFrame(in_schema(self.__repo, self.__table_names[obj_type]))
                xref_df = DataFrame(in_schema(self.__repo, self.__table_names["{}_xref".format(obj_type)])).select(
                    ['entity_name', 'entity_column'])
                df = ent_df.join(xref_df, on="name==entity_name", how="inner")
                self.__df_container[obj_type] = df.select(ent_df.columns+["entity_column"])
            else:
                self.__df_container[obj_type] = DataFrame(in_schema(self.__repo, self.__table_names[obj_type]))

        return self.__df_container[obj_type]

    def version(self):
        """
        DESCRIPTION:
            Get the FeatureStore version.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the version of FeatureStore version for
            #            the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.version()
            '1.0.0'
            >>>
        """
        return self.__version