"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements constants required for Teradata Enterprise Feature Store.
"""

from teradatasqlalchemy.types import *
from enum import Enum

# Template for creating the triggers on
# corresponding tables.
_EFS_TRIGGER_TEMPLATE = """
CREATE TRIGGER {{schema_name}}.{table}_trg
  AFTER DELETE ON {{schema_name}}.{table}
  REFERENCING OLD AS DeletedRow
  FOR EACH ROW
    INSERT INTO {{schema_name}}.{table}_staging
    VALUES ({columns}, 
            current_timestamp(6)
            )
"""

# Table for storing the features.
EFS_FEATURES_SPEC = {
    "table_name": "_efs_features",
    "columns": {
        "name": VARCHAR(200),
        "column_name": VARCHAR(200),
        "description": VARCHAR(1024),
        "tags": VARCHAR(2000),
        "data_type": VARCHAR(1024),
        "feature_type": VARCHAR(100),
        "status": VARCHAR(100),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP
    },
    "primary_index": "name"
}

# Table for storing the features.
EFS_FEATURES_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_FEATURES_SPEC["table_name"]),
    "columns": {
        "name": VARCHAR(200),
        "column_name": VARCHAR(200),
        "description": VARCHAR(1024),
        "tags": VARCHAR(2000),
        "data_type": VARCHAR(1024),
        "feature_type": VARCHAR(100),
        "status": VARCHAR(100),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP,
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_FEATURES_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_FEATURES_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_FEATURES_SPEC["columns"]))
)

# Table for storing the entities. Every Dataset has column(s) that are unique.
# This table holds all such columns.
EFS_ENTITY_SPEC = {
    "table_name": "_efs_entity",
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP
    },
    "primary_index": ["name"]
}

EFS_ENTITY_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_ENTITY_SPEC["table_name"]),
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP,
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_ENTITY_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_ENTITY_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_ENTITY_SPEC["columns"]))
)

EFS_ENTITY_XREF_SPEC = {
    "table_name": "_efs_entity_xref",
    "columns": {
        "entity_name": VARCHAR(200),
        "entity_column": VARCHAR(200)
    },
    "primary_index": ["entity_name", "entity_column"],
    "foreign_keys": [
        (
            ["entity_name"],
            ["{}.name".format(EFS_ENTITY_SPEC["table_name"])],
            "entity_xref_fk"
        )
    ]
}

EFS_ENTITY_XREF_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_ENTITY_XREF_SPEC["table_name"]),
    "columns": {
        "entity_name": VARCHAR(200),
        "entity_column": VARCHAR(200),
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_ENTITY_XREF_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_ENTITY_XREF_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_ENTITY_XREF_SPEC["columns"]))
)

# Table for storing the Data sources. Column source stores
# the corresponding Query.
EFS_DATA_SOURCE_SPEC = {
    "table_name": "_efs_data_source",
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(1024),
        "timestamp_col_name": VARCHAR(50),
        "source": VARCHAR(5000),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP
    },
    "primary_index": "name"
}

EFS_DATA_SOURCE_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_DATA_SOURCE_SPEC["table_name"]),
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(1024),
        "timestamp_col_name": VARCHAR(50),
        "source": VARCHAR(5000),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP,
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_DATA_SOURCE_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_DATA_SOURCE_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_DATA_SOURCE_SPEC["columns"]))
)

# Table for storing the feature groups. This table holds all the required
# parameters for creating DataFrame.
EFS_FEATURE_GROUP_SPEC = {
    "table_name": "_efs_feature_group",
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(200),
        "data_source_name": VARCHAR(200),
        "entity_name": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP
    },
    "primary_index": "name",
    "foreign_keys": [
        (
            ["data_source_name"],
            ["{}.name".format(EFS_DATA_SOURCE_SPEC["table_name"])],
            "data_source_name_fk"
        ),
        (
            ["entity_name"],
            ["{}.name".format(EFS_ENTITY_SPEC["table_name"])],
            "entity_fk"
         )

    ]
}

EFS_FEATURE_GROUP_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_FEATURE_GROUP_SPEC["table_name"]),
    "columns": {
        "name": VARCHAR(200),
        "description": VARCHAR(200),
        "data_source_name": VARCHAR(200),
        "entity_name": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP,
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_FEATURE_GROUP_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_FEATURE_GROUP_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_FEATURE_GROUP_SPEC["columns"]))
)


# Table for storing the feature names and associated group names.
EFS_GROUP_FEATURES_SPEC = {
    "table_name": "_efs_group_features",
    "columns": {
        "feature_name": VARCHAR(200),
        "group_name": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP
    },
    "primary_index": ["feature_name", "group_name"],
    "foreign_keys": [
        (
            ["feature_name"],
            ["{}.name".format(EFS_FEATURES_SPEC["table_name"])],
            "feature_name_fk"
        ),
        (
            ["group_name"],
            ["{}.name".format(EFS_FEATURE_GROUP_SPEC["table_name"])],
            "group_name_fk"
         )

    ]
}

EFS_GROUP_FEATURES_STAGING_SPEC = {
    "table_name": "{}_staging".format(EFS_GROUP_FEATURES_SPEC["table_name"]),
    "columns": {
        "feature_name": VARCHAR(200),
        "group_name": VARCHAR(200),
        "creation_time": TIMESTAMP,
        "modified_time": TIMESTAMP,
        "archived_time": TIMESTAMP
    },
    "primary_index": None
}

EFS_GROUP_FEATURES_TRG = _EFS_TRIGGER_TEMPLATE.format(
    table=EFS_GROUP_FEATURES_SPEC["table_name"],
    columns=", ".join(("DeletedRow.{}".format(col) for col in EFS_GROUP_FEATURES_SPEC["columns"]))
)

# Table to store the version of feature store. This is very important.
# When teradataml incrementally adds functionality for feature store, this
# version will be deciding factor whether teradataml should automatically
# update metadata or not.
EFS_VERSION_SPEC = {
    "table_name": "_efs_version",
    "columns": {
        "version": VARCHAR(20),
        "creation_time": TIMESTAMP
    }
}

EFS_VERSION = "1.0.0"


EFS_TABLES = {
    "feature": EFS_FEATURES_SPEC["table_name"],
    "feature_staging": EFS_FEATURES_STAGING_SPEC["table_name"],
    "feature_group": EFS_FEATURE_GROUP_SPEC["table_name"],
    "feature_group_staging": EFS_FEATURE_GROUP_STAGING_SPEC["table_name"],
    "entity": EFS_ENTITY_SPEC["table_name"],
    "entity_staging": EFS_ENTITY_STAGING_SPEC["table_name"],
    "entity_xref": EFS_ENTITY_XREF_SPEC["table_name"],
    "entity_staging_xref": EFS_ENTITY_XREF_STAGING_SPEC["table_name"],
    "data_source": EFS_DATA_SOURCE_SPEC["table_name"],
    "data_source_staging": EFS_DATA_SOURCE_STAGING_SPEC["table_name"],
    "group_features": EFS_GROUP_FEATURES_SPEC["table_name"],
    "group_features_staging": EFS_GROUP_FEATURES_STAGING_SPEC["table_name"],
    "version": EFS_VERSION_SPEC["table_name"]
}


class FeatureStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2


class FeatureType(Enum):
    CONTINUOUS = 1
    CATEGORICAL = 2
