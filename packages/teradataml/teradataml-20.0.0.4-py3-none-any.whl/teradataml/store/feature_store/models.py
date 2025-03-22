"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements the models required for Teradata Enterprise Feature Store.
"""

from collections import OrderedDict
from datetime import datetime as dt
from teradatasqlalchemy import types as tdtypes
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.dataframe import DataFrame, in_schema
from teradataml.dataframe.sql import _SQLColumnExpression
from teradataml.dbutils.dbutils import db_transaction, _delete_data, execute_sql, _insert_data, _upsert_data
from teradataml.store.feature_store.constants import *
from teradataml.utils.validators import _Validators
import inspect


class Feature:
    """Class for Feature. """
    def __init__(self,
                 name,
                 column,
                 feature_type=FeatureType.CONTINUOUS,
                 description=None,
                 tags=None,
                 status=FeatureStatus.ACTIVE):
        """
        DESCRIPTION:
            Constructor for Feature.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the Feature.
                Types: str.

            column:
                Required Argument.
                Specifies the DataFrame Column.
                Types: teradataml DataFrame Column

            feature_type:
                Optional Argument.
                Specifies whether feature is continuous or discrete.
                Default Value: FeatureType.CONTINUOUS
                Types: FeatureType Enum

            description:
                Optional Argument.
                Specifies human readable description for Feature.
                Types: str

            tags:
                Optional Argument.
                Specifies the tags for Feature.
                Types: str OR list of str

            status:
                Optional Argument.
                Specifies whether feature is archived or active.
                Types: FeatureStatus Enum

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureType, load_example_data
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

            # create a Categorical Feature for column 'Feb' for 'sales' DataFrame and name it as
            # 'sales_Feb'.
            >>> from teradataml import Feature
            >>> feature = Feature('sales_Feb', column=df.Feb, feature_type=FeatureType.CATEGORICAL)
            >>> feature
            Feature(name=sales_Feb)
            >>>
        """
        self.name = name
        self.column_name = column.name
        self.description = description
        self.tags = UtilFuncs._as_list(tags) if tags else None
        self.data_type = column.type
        self.feature_type = feature_type
        self.status = status

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of Feature from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has Feature details.
                Types: teradataml DataFrame.

        RETURNS:
            Feature or list of Feature.

        RAISES:
            None

        EXAMPLES:
            >>> Feature._from_df(df)
        """
        _features = []
        recs = [rec._asdict() for rec in df.itertuples()]

        for rec in recs:
            # Pop out unnecessary details.
            rec.pop("creation_time")
            rec.pop("modified_time")
            rec.pop("group_name")
            rec["column"] = _SQLColumnExpression(rec.pop("column_name"),
                                                 type=getattr(tdtypes, rec.pop("data_type"))())
            rec["feature_type"] = FeatureType.CONTINUOUS if rec["feature_type"] == FeatureType.CONTINUOUS.name \
                else FeatureType.CATEGORICAL
            rec["status"] = FeatureStatus.ACTIVE if rec["status"] == FeatureStatus.ACTIVE.name else FeatureStatus.INACTIVE
            _features.append(cls(**rec))

        return _features if len(_features) > 1 else _features[0]

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for Feature object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        return "Feature(name={name})".format(name=self.name)

    def publish(self, repo):
        """
        DESCRIPTION:
            Method to publish the Feature details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the Feature details.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Publish the Feature details to repo 'vfs_test' for column
                         'Feb' from 'sales' DataFrame.
            >>> from teradataml import Feature
            >>> feature = Feature('sales:Feb', df.Feb)
            >>> feature.publish('vfs_test')
            True
            >>>

            # Example 2: Republish the Feature published in Example 1 by updating
            #            it's tags.
            >>> # First, Get the existing Feature.
            >>> from teradataml import FeatureStore
            >>> feature = FeatureStore('vfs_test').get_feature('sales:Feb')
            >>> # Update it's tags.
            >>> feature.tags = ["sales_data", "monthly_sales"]
            >>> # Republish the details to same repo.
            >>> feature.publish('vfs_test')
        """
        _upsert_data(schema_name=repo,
                     table_name=EFS_FEATURES_SPEC["table_name"],
                     insert_columns_values = OrderedDict({
                         'name': self.name,
                         'column_name': self.column_name,
                         'description': self.description,
                         'creation_time': dt.utcnow(),
                         'tags': ", ".join(self.tags) if self.tags else None,
                         'data_type': str(self.data_type),
                         'feature_type': self.feature_type.name,
                         'status': self.status.name}),
                     upsert_conditions=OrderedDict({
                         'name': self.name}),
                     update_columns_values=OrderedDict({
                         'column_name': self.column_name,
                         'description': self.description,
                         'modified_time': dt.utcnow(),
                         'tags': ", ".join(self.tags) if self.tags else None,
                         'data_type': str(self.data_type),
                         'feature_type': self.feature_type.name,
                         'status': self.status.name})
                     )
        return True


class Entity:
    """Class for Entity. """
    def __init__(self, name, columns, description=None):
        """
        DESCRIPTION:
            Constructor for creating Entity Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the entity.
                Types: str.

            columns:
                Required Argument.
                Specifies the names of the columns.
                Types: teradataml DataFrame Column OR list of teradataml DataFrame Columns.

            description:
                Optional Argument.
                Specifies human readable description for Feature.
                Types: str

        RETURNS:
            Object of Entity.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # create a Entity with column 'accounts' for 'sales' DataFrame and name it as
            # 'sales_accounts'.
            >>> from teradataml import Entity
            >>> entity = Entity('sales_accounts', df.accounts)
            >>> entity
            Entity(name=sales_accounts)
            >>>
        """
        self.name = name
        self.columns = [col if isinstance(col, str) else col.name for col in UtilFuncs._as_list(columns)]
        self.description = description

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of Entity from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has details for Entity.
                Types: teradataml DataFrame.

        RETURNS:
            Entity

        RAISES:
            None

        EXAMPLES:
            >>> Entity._from_df(df)
        """
        entity_name = None
        description = None
        columns = []

        # Get all the entity columns and update there.
        for rec in df.itertuples():
            entity_name = rec.name
            description = rec.description
            columns.append(rec.entity_column)

        return cls(name=entity_name, description=description, columns=columns)

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for Entity object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        return "Entity(name={})".format(self.name)

    @db_transaction
    def publish(self, repo):
        """
        DESCRIPTION:
            Method to publish the Entity details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the Entity details.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Publish the Entity details to repo 'vfs_test' for column
                         'accounts' from 'sales' DataFrame.
            >>> from teradataml import Entity
            >>> entity = Entity('sales:accounts', 'accounts')
            >>> entity.publish('vfs_test')
            True
            >>>
        """
        # Upsert should be triggered for every corresponding entity ID and column.
        _upsert_data(schema_name=repo,
                     table_name=EFS_ENTITY_SPEC["table_name"],
                     insert_columns_values=OrderedDict({
                         'name': self.name,
                         'description': self.description,
                         'creation_time': dt.utcnow()}),
                     upsert_conditions=OrderedDict({
                         'name': self.name}),
                     update_columns_values=OrderedDict({
                         'description': self.description,
                         'modified_time': dt.utcnow()})
                     )

        # Insert into xref table now. Before that, delete for that key.
        _delete_data(schema_name=repo,
                     table_name=EFS_ENTITY_XREF_SPEC["table_name"],
                     delete_conditions=_SQLColumnExpression("entity_name")==self.name)

        values = [(self.name, col) for col in self.columns]
        _insert_data(EFS_ENTITY_XREF_SPEC["table_name"], values, schema_name=repo)

        return True

    def __eq__(self, other):
        """
        Compare the Entity with other Entity to check if both are
        same or not.

        PARAMETERS:
            other :
                Required Argument.
                Specifies another Entity.
                Types: Entity

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create two entities and compare whether they are same or not.
            >>> from teradataml import Entity
            >>> entity1 = Entity('sales:accounts', 'accounts')
            >>> entity2 = Entity('sales:accounts', 'accounts')
            >>> entity1 == entity2
            True
            >>>
        """
        if not isinstance(other, Entity):
            return False
        # Both entities will be same only when corresponding columns are same.
        return set(self.columns) == set(other.columns)


class DataSource:
    """Class for DataSource. """
    def __init__(self, name, source, description=None, timestamp_col_name=None):
        """
        DESCRIPTION:
            Constructor for creating DataSource Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the DataSource.
                Types: str.

            source:
                Required Argument.
                Specifies the source query of DataSource.
                Types: str OR teradataml DataFrame.

            description:
                Optional Argument.
                Specifies human readable description for DataSource.
                Types: str

            timestamp_col_name:
                Optional Argument.
                Specifies the timestamp column indicating when the row was created.
                Types: str

        RETURNS:
            Object of DataSource.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a DataSource for above mentioned DataFrame with name 'Sales_Data'.
            >>> from teradataml import DataSource
            >>> data_source = DataSource('Sales_Data', df)
            >>> data_source
            DataSource(Sales_Data)
            >>>
        """
        self.name = name
        self.timestamp_col_name = timestamp_col_name
        self.source = source if isinstance(source, str) else source.show_query()
        self.description = description

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of DataSource from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has a single
                record denoting DataSource.
                Types: teradataml DataFrame.

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> DataSource._from_df(df)
        """
        rec = next(df.itertuples())._asdict()
        rec.pop("creation_time")
        rec.pop("modified_time")
        return cls(**(rec))

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for DataSource object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        return "DataSource(name={})".format(self.name)

    def publish(self, repo):
        """
        DESCRIPTION:
            Method to publish the DataSource details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the DataSource details.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Publish the above mentioned DataFrame as DataSource
            #            and name it as "Sales_Data".
            >>> from teradataml import DataSource
            >>> data_source = DataSource('Sales_Data', df)
            >>> data_source.publish('vfs_test')
            True
            >>>

            # Example 2: Republish the published DataSource in example 1 with
            #            updated description.
            >>> # First, Get the existing DataSource.
            >>> from teradataml import FeatureStore
            >>> data_source = FeatureStore('vfs_test').get_data_source('Sales_Data')
            >>> # Update it's description.
            >>> data_source.description = "Pivoted sales data."
            >>> # Republish the details to same repo.
            >>> data_source.publish('vfs_test')
        """
        _upsert_data(schema_name=repo,
                     table_name=EFS_DATA_SOURCE_SPEC["table_name"],
                     insert_columns_values=OrderedDict({
                         'name': self.name,
                         'description': self.description,
                         'timestamp_col_name': self.timestamp_col_name,
                         'source': self.source,
                         'creation_time': dt.utcnow()
                     }),
                     upsert_conditions={"name": self.name},
                     update_columns_values=OrderedDict({
                         'description': self.description,
                         'timestamp_col_name': self.timestamp_col_name,
                         'modified_time': dt.utcnow(),
                         'source': self.source})
                     )
        return True


class FeatureGroup:
    """Class for FeatureGroup. """
    def __init__(self, name, features, entity, data_source, description=None):
        """
        DESCRIPTION:
            Constructor for creating FeatureGroup Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the FeatureGroup.
                Types: str.

            features:
                Required Argument.
                Specifies the features required to create a group.
                Types: Feature or list of Feature.

            entity:
                Required Argument.
                Specifies the entity associated with corresponding features.
                Types: Entity

            data_source:
                Required Argument.
                Specifies the DataSource associated with Features.
                Types: str

            description:
                Optional Argument.
                Specifies human readable description for DataSource.
                Types: str

        RETURNS:
            Object of FeatureGroup.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup for above mentioned DataFrame.
            >>> # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)
            >>> # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)
            >>> # Create DataSource
            >>> data_source = DataSource("sales_source", df.show_query())
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
        """
        self.name = name
        self.features = UtilFuncs._as_list(features)
        self.entity = entity
        self.data_source = data_source
        self.description = description
        self.__redundant_features = []
        self._labels = []

    @property
    def features(self):
        """
        DESCRIPTION:
            Get's the features from FeatureGroup.

        PARAMETERS:
            None

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "sales")
            >>> # Let's create DataFrame first.
            >>> df = DataFrame("sales")
            >>> # create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)
            >>> # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)
            >>> # Create DataSource
            >>> data_source = DataSource("sales_source", df)
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Get the features from FeatureGroup
            >>> fg.features
            [Feature(name=sales:Jan), Feature(name=sales:Fan), Feature(name=sales:Mar), Feature(name=sales:Apr)]
            >>>
        """
        return [feature for feature in self._features if feature.name not in self._labels]

    @property
    def labels(self):
        """
        DESCRIPTION:
            Get's the labels from FeatureGroup.
            Note:
                Use this function only after setting the labels using "set_labels".

        PARAMETERS:
            None

        RETURNS:
            Feature OR list

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            >>> # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")
            >>> # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)
            >>> # Create Entity.
            >>> entity = Entity("id", df.id)
            >>> # Create DataSource
            >>> data_source = DataSource("admissions_source", df)
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True

            # Get the labels from FeatureGroup
            >>> fg.labels
            Feature(name=admitted)
            >>>
        """
        labels = [feature for feature in self._features if feature.name in self._labels]
        if len(labels) == 1:
            return labels[0]
        return labels

    @features.setter
    def features(self, features):
        """ Setter for features. """
        self._features = UtilFuncs._as_list(features)
        return True

    def set_labels(self, labels):
        """
        DESCRIPTION:
            Sets the labels for FeatureGroup.
            This method is helpful, when working with analytic functions to consume the Features. 
            Note:
                Label is for the current session only.

        PARAMETERS:
            labels:
                Required Argument.
                Specifies the name(s) of the features to refer as labels.
                Types: str or list of str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            >>> # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")
            >>> # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)
            >>> # Create Entity.
            >>> entity = Entity("id", df.id)
            >>> # Create DataSource
            >>> data_source = DataSource("admissions_source", df)
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            >>> # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True
        """
        self._labels = [] if labels is None else UtilFuncs._as_list(labels)
        return True

    @labels.setter
    def labels(self, labels):
        """
        DESCRIPTION:
            Sets the labels for FeatureGroup.
            This method is helpful, when working with analytic functions to consume the Features.
            Note:
                Label is for the current session only.

        PARAMETERS:
            labels:
                Required Argument.
                Specifies the name(s) of the features to refer as labels.
                Types: str or list of str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")
            # Create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)
            # Create Entity.
            >>> entity = Entity("id", df.id)
            # Create DataSource.
            >>> data_source = DataSource("admissions_source", df)
            # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Set feature 'admitted' as label.
            >>> fg.labels = 'admitted'
            True
        """
        return self.set_labels(labels)

    def reset_labels(self):
        """
        DESCRIPTION:
            Resets the labels for FeatureGroup.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            >>> # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")
            >>> # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)
            >>> # Create Entity.
            >>> entity = Entity("id", df.id)
            >>> # Create DataSource
            >>> data_source = DataSource("admissions_source", df)
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True

            >>> # Remove the labels from FeatureGroup.
            >>> fg.reset_labels()
            True
            >>>
        """
        self._labels = []
        return True

    def apply(self, object):
        """
        DESCRIPTION:
            Register objects to FeatureGroup.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to update the FeatureGroup.
                Types: Feature OR DataSource OR Entity.

        RETURNS:
            bool.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")
            >>> # Create FeatureGroup to use it in examples.
            >>> from teradataml import Feature, Entity, DataSource, FeatureGroup
            >>> feature = Feature('sales:Feb', df.Feb)
            >>> entity = Entity('sales:accounts', df.accounts)
            >>> data_source = DataSource('Sales_Data', df)
            >>> fg = FeatureGroup('Sales',
            ...                   features=feature,
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Example 1: create a new Feature for column df.Mar and
            #            apply the feature to FeatueGroup.
            >>> # Create Feature.
            >>> feature = Feature('sales:Mar', df.Mar)
            >>> # Register the above Feature with FeatureGroup.
            >>> fg.apply(feature)
            True
            >>>
        """
        if isinstance(object, Feature):
            # Before adding feature, check if already feature with
            # the name exists or not.
            feature_exists = [i for i in range(len(self._features)) if self._features[i].name == object.name]
            if feature_exists:
                self._features[feature_exists[0]] = object
            else:
                self._features.append(object)
        elif isinstance(object, Entity):
            self.entity = object
        elif isinstance(object, DataSource):
            self.data_source = object
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                     'object', "Feature or Entity or DataSource"),
                                      MessageCodes.UNSUPPORTED_DATATYPE)

        return True

    def remove(self, object):
        """
        DESCRIPTION:
            Method to remove the objects from FeatureGroup. One can use this
            method to detach either Feature or DataSource or Entity from
            FeatureGroup. Much useful to remove existing Features from
            FeatureGroup.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to be removed from FeatureGroup.
                Types: Feature OR Entity OR DataSource OR FeatureGroup.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")
            >>> # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Jan", df.Apr)
            >>> # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)
            >>> # Create DataSource
            >>> data_source = DataSource("sales_source", df.show_query())
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Example: Remove the Feature with name "sales:Feb" from FeatureGroup.
            >>> fg.remove(feb_feature)
            True
            >>>
        """
        get_msg = lambda object: "{} '{}' is not associated with FeatureGroup.".format(
            object.__class__.__name__, object.name)

        if isinstance(object, Feature):
            # Find the position of feature first, then pop it.
            index = [i for i in range(len(self._features)) if self._features[i].name == object.name]
            if index:
                self.__redundant_features.append(self._features.pop(index[0]))
            else:
                print(get_msg(object))
                return False
        elif isinstance(object, DataSource):
            if self.data_source.name == object.name:
                self.data_source = None
            else:
                print(get_msg(object))
                return False
        elif isinstance(object, Entity):
            if self.entity.name == object.name:
                self.entity = None
            else:
                print(get_msg(object))
                return False
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                           'object', "Feature or Entity or DataSource"),
                                      MessageCodes.UNSUPPORTED_DATATYPE)
        return True

    @classmethod
    def _from_df(cls, df, repo, features_df, entity_df, data_source_df):
        """
        DESCRIPTION:
            Internal method to create object of FeatureGroup from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has a single
                record denoting FeatureGroup.
                Types: teradataml DataFrame.

            repo:
                Required Argument.
                Specifies the repo name of FeatureStore.
                Types: str

            features_df:
                Required Argument.
                Specifies teradataml DataFrame which has features.
                Types: teradataml DataFrame.

            entity_df:
                Required Argument.
                Specifies teradataml DataFrame which has entities.
                Types: teradataml DataFrame.

            data_source_df:
                Required Argument.
                Specifies teradataml DataFrame which has data sources.
                Types: teradataml DataFrame.

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> FeatureGroup._from_df(df, "repo", features_df, entity_df, data_source_df)
        """
        rec = next(df.itertuples())._asdict()

        # Select active features.
        features_df = features_df[features_df.status != FeatureStatus.INACTIVE.name]
        req_features_df = features_df[features_df.group_name == rec["name"]]

        features = Feature._from_df(req_features_df)
        entity = Entity._from_df(entity_df[entity_df.name==rec['entity_name']])
        data_source = DataSource._from_df(data_source_df[data_source_df.name==rec['data_source_name']])

        return cls(name=rec["name"], features=features, entity=entity, data_source=data_source, description=rec["description"])

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for FeatureGroup object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        return "FeatureGroup({}, features=[{}], entity={}, data_source={})".format(
            self.name, ", ".join((str(feature) for feature in self.features)), self.entity, self.data_source)

    @db_transaction
    def publish(self, repo):
        """
        DESCRIPTION:
            Method to publish the FeatureGroup details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the FeatureGroup details.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup 'sales_data_fg' for above mentioned
            #            DataFrame and publish it to 'vfs_v1'.
            >>> # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Jan", df.Apr)
            >>> # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)
            >>> # Create DataSource
            >>> data_source = DataSource("sales_source", df.show_query())
            >>> # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> feature_group.publish('vfs_v1')

            # Example 2: Republish the FeatureGroup published in example1 with
            #            updated description.
            >>> # First, Get the existing FeatureGroup.
            >>> from teradataml import FeatureStore
            >>> fg = FeatureStore('vfs_test').get_feature_group('Sales')
            >>> # Update it's description.
            >>> fg.description = "Feature group for Sales."
            >>> # Republish the details to same repo.
            >>> fg.publish('vfs_v1')
        """

        # Do not publish if any of required associated parameter does not exist.
        message = "FeatureGroup can not be published with out {}"
        if not self.features:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("Features")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        if not self.data_source:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("DataSource")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        if not self.entity:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("Entity")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        # Before publish FeatureGroup, publish other elements.
        for feature in self.features:
            feature.publish(repo)

        self.entity.publish(repo)
        self.data_source.publish(repo)
        _upsert_data(schema_name=repo,
                     table_name=EFS_FEATURE_GROUP_SPEC["table_name"],
                     insert_columns_values=OrderedDict({
                         'name': self.name,
                         'description': self.description,
                         'data_source_name': self.data_source.name,
                         'entity_name': self.entity.name,
                         'creation_time': dt.utcnow()
                     }),
                     upsert_conditions={'name': self.name},
                     update_columns_values=OrderedDict({
                         'description': self.description,
                         'data_source_name': self.data_source.name,
                         'modified_time': dt.utcnow(),
                         'entity_name': self.entity.name})
                     )

        for feature in self.features:
            _upsert_data(schema_name=repo,
                         table_name=EFS_GROUP_FEATURES_SPEC["table_name"],
                         insert_columns_values=OrderedDict({
                             'feature_name': feature.name,
                             'group_name': self.name,
                             'modified_time': dt.utcnow()
                         }),
                         upsert_conditions={'feature_name': feature.name, "group_name": self.name},
                         update_columns_values=OrderedDict({
                             'modified_time': dt.utcnow()
                         })
                         )

        # Cut down the link between features and FeatureGroup if any of the
        # features is removed from FeatureGroup.
        if self.__redundant_features:
            col_expression = _SQLColumnExpression("feature_name") == self.__redundant_features[0].name
            for feature in self.__redundant_features[1:]:
                col_expression = ((col_expression) | (_SQLColumnExpression("feature_name") == feature.name))
            _delete_data(schema_name=repo,
                         table_name=EFS_GROUP_FEATURES_SPEC["table_name"],
                         delete_conditions=((_SQLColumnExpression("group_name") == self.name) & (col_expression)))
            # After removing the data, set this back.
            self.__redundant_features = []

        return True

    def __add__(self, other):
        """
        Combines two Feature groups.

        PARAMETERS:
            other :
                Required Argument.
                Specifies another FeatureGroup.
                Types: FeatureGroup

        RETURNS:
            FeatureGroup

        RAISES:
            TypeError, ValueError

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017

            # Example 1: create two feature groups and then create a new feature
            #            group by combining those two feature groups.
            # Creating first feature group.
            >>> f1 = Feature("sales_Jan", column=df.Jan)
            >>> f2 = Feature("sales_Feb", column=df.Feb)
            >>> entity = Entity(name="sales", columns='accounts')
            >>> data_source = DataSource("sales", source=df.show_query())
            >>> fg1 = FeatureGroup(name="sales_jan_feb", entity=entity, features=[f1, f2], data_source=data_source)
            >>> fg1
            FeatureGroup(sales_jan_feb, features=[Feature(name=sales_Jan), Feature(name=sales_Feb)], entity=Entity(name=sales), data_source=DataSource(name=sales))

            >>> # Creating second feature group.
            >>> f3 = Feature("sales_Mar", column=df.Mar)
            >>> f4 = Feature("sales_Apr", column=df.Apr)
            >>> data_source = DataSource("sales_Mar_Apr", source=df.show_query())
            >>> fg2 = FeatureGroup(name="sales_Mar_Apr", entity=entity, features=[f3, f4], data_source=data_source)
            >>> fg2
            FeatureGroup(sales_Mar_Apr, features=[Feature(name=sales_Mar), Feature(name=sales_Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))

            >>> # Combining two feature groups.
            >>> new_fg = feature_group1 + feature_group2
            >>> new_fg
            FeatureGroup(sales_jan_feb_sales_Mar_Apr, features=[Feature(name=sales_Jan), Feature(name=sales_Feb), Feature(name=sales_Mar), Feature(name=sales_Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))
            >>>
        """
        if not isinstance(other, FeatureGroup):
            err_ = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "other",
                                        "FeatureGroup")
            raise TypeError(err_)

        if self.entity != other.entity:
            raise ValueError("Two FeatureGroups can be merged only when the corresponding entities are same.")

        # While merging two datasets, time stamp columns also should be same.
        if ((self.data_source.timestamp_col_name and not other.data_source.timestamp_col_name) or
                (other.data_source.timestamp_col_name and not self.data_source.timestamp_col_name) or
                (self.data_source.timestamp_col_name != other.data_source.timestamp_col_name)):
            raise ValueError("Two FeatureGroups can be merged only when the corresponding "
                             "'timestamp_col_name' for the DataSources are same.")

        if self.entity == other.entity:

            existing_columns = {feature.column_name for feature in self.features}
            # New features should be combined features of both "self" and other.
            # However, these two features may share common features too. In such cases,
            # consider only one.
            effective_other_features = [feature for feature in other.features
                                        if feature.column_name not in existing_columns]

            # Prepare new DataSource.
            query_1 = self.data_source.source
            query_2 = other.data_source.source

            # If both the queries a.k.a sources are not same, then combine those
            # sources with join. While combining, make sure to specify only the
            # columns which are required.
            if query_2 != query_1:

                # Consider adding timestamp column to query.
                time_stamp_column = []
                if self.data_source.timestamp_col_name:
                    time_stamp_column.append("A.{}".format(self.data_source.timestamp_col_name))

                feature_columns = (["A.{}".format(feature.column_name) for feature in self.features] +
                                   ["B.{}".format(feature.column_name) for feature in effective_other_features])

                columns = ", ".join(["A.{}".format(col) for col in self.entity.columns] + time_stamp_column + feature_columns)
                on_clause_columns = [col for col in self.entity.columns]
                if self.data_source.timestamp_col_name:
                    on_clause_columns.append(self.data_source.timestamp_col_name)
                where_clause = " AND ".join(["A.{0} = B.{0}".format(column) for column in on_clause_columns])

                query = f"""
                SELECT {columns}
                FROM ({query_1.strip(";")}) AS A, ({query_2.strip(";")}) AS B
                WHERE {where_clause}
                """
                data_source = DataSource(name="{}_{}".format(self.data_source.name, other.data_source.name),
                                         source=query,
                                         description="Combined DataSource for {} and {}".format(
                                             self.data_source.name, other.data_source.name),
                                         timestamp_col_name=self.data_source.timestamp_col_name
                                         )
            else:
                data_source = self.data_source

            # Create new feature group.
            feature_group = FeatureGroup(name="{}_{}".format(self.name, other.name),
                                         features=self.features + effective_other_features,
                                         data_source=data_source,
                                         entity=Entity(name="{}_{}".format(self.name, other.name),
                                                       columns=self.entity.columns),
                                         description="Combined FeatureGroup for groups {} and {}.".format(
                                             self.name, other.name)
                                         )
            return feature_group

    @classmethod
    def from_query(cls, name, entity_columns, query, timestamp_col_name=None):
        """
        DESCRIPTION:
            Method to create FeatureGroup from Query.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Note:
                    * Entitiy, DataSource also get the same name as "name".
                      Users can change the name of Entity or DataSource by accessing
                      object from FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            query:
                Required Argument.
                Specifies the query for DataSource.
                Types: str.

            timestamp_col_name:
                Optional Argument.
                Specifies the name of the column in the Query which
                holds the record creation time.
                Types: str

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup from query 'SELECT * FROM SALES' and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_col_name.
            >>> from teradataml import FeatureGroup
            >>> query = 'SELECT * FROM SALES'
            >>> fg = FeatureGroup.from_query(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             query=query,
            ...             timestamp_col_name='datetime'
            ...         )
        """
        return cls.__create_feature_group(name, entity_columns, query, timestamp_col_name)

    @classmethod
    def from_DataFrame(cls, name, entity_columns, df, timestamp_col_name=None):
        """
        DESCRIPTION:
            Method to create FeatureGroup from DataFrame.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Note:
                    * Entitiy, DataSource also get the same name as "name".
                      User's can change the name of Entity or DataSource by accessing
                      object from FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            df:
                Required Argument.
                Specifies teradataml DataFrame for creating DataSource.
                Types: teradataml DataFrame.

            timestamp_col_name:
                Optional Argument.
                Specifies the name of the column in the Query which
                holds the record creation time.
                Types: str

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup from DataFrame created on 'sales' table and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_col_name.
            >>> from teradataml import FeatureGroup
            >>> df = DataFrame("sales")
            >>> fg = FeatureGroup.from_DataFrame(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             df=df,
            ...             timestamp_col_name='datetime'
            ...         )
        """
        return cls.__create_feature_group(name, entity_columns, df, timestamp_col_name)

    @classmethod
    def __create_feature_group(cls, name, entity_columns, obj, timestamp_col_name=None):
        """
        DESCRIPTION:
            Internal method to create FeatureGroup from either DataFrame or from Query.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            obj:
                Required Argument.
                Specifies either teradataml DataFrame or Query for creating DataSource.
                Types: teradataml DataFrame OR str.

            timestamp_col_name:
                Optional Argument.
                Specifies the name of the column in the Query or DataFrame which
                holds the record creation time.
                Types: str

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup from DataFrame created on 'sales' table and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_col_name.
            >>> from teradataml import FeatureGroup
            >>> df = DataFrame("sales")
            >>> fg = FeatureGroup.__create_feature_group(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             df=df,
            ...             timestamp_col_name='datetime'
            ...         )
        """
        # Check the caller. And decide the type of 'obj'.
        is_obj_dataframe = False
        if inspect.stack()[1][3] == 'from_DataFrame':
            # Perform the function validations.
            is_obj_dataframe = True

        argument_validation_params = []
        argument_validation_params.append(["name", name, False, str, True])
        argument_validation_params.append(["entity_columns", entity_columns, False, (str, list), True])
        argument_validation_params.append(["timestamp_col_name", timestamp_col_name, True, str, True])
        param = ["df", obj, False, DataFrame, True] if is_obj_dataframe else ["query", obj, False, str, True]
        argument_validation_params.append(param)
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = obj if is_obj_dataframe else DataFrame.from_query(obj)

        features = [Feature(name=col, column=df[col]) for col in df.columns if (
                col not in UtilFuncs._as_list(entity_columns) and col != timestamp_col_name)
            ]
        data_source = DataSource(
            name=name,
            source=df.show_query(),
            timestamp_col_name=timestamp_col_name
        )
        entity = Entity(name=name, columns=entity_columns)
        fg = FeatureGroup(
            name=name,
            features=features,
            data_source=data_source,
            entity=entity
        )
        return fg
