import copy
from datetime import datetime
import os
import pytest

from dasl_client import *

dasl_host = os.environ["DASL_API_URL"]
databricks_host = os.environ["DATABRICKS_HOST"]
databricks_client_id = os.environ["DATABRICKS_CLIENT_ID"]
databricks_client_secret = os.environ["DATABRICKS_CLIENT_SECRET"]
workspace = databricks_host.split("//")[1].split(".")[0]
app_client_id = "22853b93-68ba-4ae2-8e41-976417f501dd"
alternate_app_client_id = "335ac0d3-e0ea-4732-ba93-0277423b5029"


@pytest.fixture(scope="session")
def api_client():
    client = Client.new_workspace(
        admin_email="test@antimatter.io",
        app_client_id=app_client_id,
        service_principal_id=databricks_client_id,
        service_principal_secret=databricks_client_secret,
        workspace_url=databricks_host,
        dasl_host=dasl_host,
    )
    yield client


def test_admin_config(api_client):
    base_admin_config = AdminConfig(
        workspace_url=databricks_host,
        app_client_id=app_client_id,
        service_principal_id=databricks_client_id,
        service_principal_secret="********",
    )

    ac = api_client.get_admin_config()
    assert ac == base_admin_config

    other = AdminConfig(
        workspace_url=databricks_host,
        app_client_id=alternate_app_client_id,
        service_principal_id=databricks_client_id,
        service_principal_secret=databricks_client_secret,
    )
    api_client.put_admin_config(other)

    assert api_client.get_admin_config() == AdminConfig(
        workspace_url=databricks_host,
        app_client_id=alternate_app_client_id,
        service_principal_id=databricks_client_id,
        service_principal_secret="********",
    )

    ac.service_principal_secret = databricks_client_secret
    api_client.put_admin_config(ac)
    assert api_client.get_admin_config() == base_admin_config


def test_workspace_config(api_client):
    base_workspace_config = WorkspaceConfig(
        metadata=Metadata(
            name="config",
            workspace=workspace,
        ),
        dasl_storage_path="/Volumes/automated_test_cases/default/test",
        system_tables_config=SystemTablesConfig(
            catalog_name="automated_test_cases",
            var_schema="default",
        ),
        default_config=DefaultConfig(
            var_global=DefaultConfig.Config(
                bronze_schema="bronze",
                silver_schema="silver",
                gold_schema="gold",
                catalog_name="automated_test_cases",
            ),
        ),
    )

    api_client.put_config(base_workspace_config)
    got = api_client.get_config()

    # the server is going to populate created_timestamp, modified_timestamp,
    # version, and resource_status, so copy those over before comparing.
    base_workspace_config.metadata.created_timestamp = got.metadata.created_timestamp
    base_workspace_config.metadata.modified_timestamp = got.metadata.modified_timestamp
    base_workspace_config.metadata.version = got.metadata.version
    base_workspace_config.metadata.resource_status = got.metadata.resource_status

    assert api_client.get_config() == base_workspace_config

    base_workspace_config.default_config.var_global.bronze_schema = "bronze_new"
    api_client.put_config(base_workspace_config)
    got = api_client.get_config()
    base_workspace_config.metadata.modified_timestamp = got.metadata.modified_timestamp
    base_workspace_config.metadata.version = got.metadata.version
    base_workspace_config.metadata.resource_status = got.metadata.resource_status

    assert api_client.get_config() == base_workspace_config


def test_minimal_data_source(api_client):
    base_data_source = DataSource(
        source="test",
        schedule=Schedule(
            at_least_every="2h",
            enabled=True,
        ),
        bronze=BronzeSpec(
            bronze_table="test_bronze_table",
            skip_bronze_loading=False,
        ),
        silver=SilverSpec(),
        gold=GoldSpec(),
    )

    base_ds_1 = api_client.create_datasource("test_1", base_data_source)
    assert base_ds_1.source == base_data_source.source
    assert base_ds_1.schedule == base_data_source.schedule
    assert base_ds_1.bronze == base_data_source.bronze
    assert base_ds_1.silver == base_data_source.silver
    assert base_ds_1.gold == base_data_source.gold

    got = api_client.get_datasource("test_1")
    listed = api_client.list_datasources()
    assert len(listed) == 1
    assert listed[0] == got

    # the server is going to populate created_timestamp, modified_timestamp,
    # version, and resource_status, so copy those over before comparing.
    base_ds_1.metadata.created_timestamp = got.metadata.created_timestamp
    base_ds_1.metadata.created_by = got.metadata.created_by
    base_ds_1.metadata.modified_timestamp = got.metadata.modified_timestamp
    base_ds_1.metadata.version = got.metadata.version
    base_ds_1.metadata.resource_status = got.metadata.resource_status
    assert api_client.get_datasource("test_1") == base_ds_1

    base_ds_2 = api_client.create_datasource("test_2", base_data_source)
    assert base_ds_2.source == base_data_source.source
    assert base_ds_2.schedule == base_data_source.schedule
    assert base_ds_2.bronze == base_data_source.bronze
    assert base_ds_2.silver == base_data_source.silver
    assert base_ds_2.gold == base_data_source.gold

    got_2 = api_client.get_datasource("test_2")
    listed = api_client.list_datasources()
    assert len(listed) == 2
    assert listed[0] == got
    assert listed[1] == got_2

    base_ds_2.metadata.created_timestamp = got_2.metadata.created_timestamp
    base_ds_2.metadata.created_by = got_2.metadata.created_by
    base_ds_2.metadata.modified_timestamp = got_2.metadata.modified_timestamp
    base_ds_2.metadata.version = got_2.metadata.version
    base_ds_2.metadata.resource_status = got_2.metadata.resource_status
    assert api_client.get_datasource("test_2") == base_ds_2

    base_ds_2.bronze.bronze_table = "test_2"
    api_client.replace_datasource("test_2", base_ds_2)

    got_2 = api_client.get_datasource("test_2")
    base_ds_2.metadata.modified_timestamp = got_2.metadata.modified_timestamp
    base_ds_2.metadata.version = got_2.metadata.version
    base_ds_2.metadata.resource_status = got_2.metadata.resource_status

    assert api_client.get_datasource("test_2") == base_ds_2

    api_client.delete_datasource("test_1")
    listed = [
        item
        for item in api_client.list_datasources()
        if item.metadata.resource_status != "deletionPending"
    ]
    assert len(listed) == 1
    assert listed[0] == base_ds_2


def test_minimal_rule(api_client):
    base_rule = Rule(
        schedule=Schedule(
            at_least_every="2h",
            enabled=True,
        ),
        input=Rule.Input(
            stream=Rule.Input.Stream(
                tables=[
                    Rule.Input.Stream.Table(
                        name="test",
                    ),
                ],
            ),
        ),
        output=Rule.Output(
            summary="test",
        ),
    )

    base_rule_1 = api_client.create_rule("test_1", base_rule)
    assert base_rule_1.schedule == base_rule.schedule
    assert base_rule_1.input == base_rule.input
    assert base_rule_1.output == base_rule.output

    got = api_client.get_rule("test_1")
    listed = api_client.list_rules()
    assert len(listed) == 1
    assert listed[0] == got

    # the server is going to populate created_timestamp, modified_timestamp,
    # version, and resource_status, so copy those over before comparing.
    base_rule_1.metadata.created_timestamp = got.metadata.created_timestamp
    base_rule_1.metadata.created_by = got.metadata.created_by
    base_rule_1.metadata.modified_timestamp = got.metadata.modified_timestamp
    base_rule_1.metadata.version = got.metadata.version
    base_rule_1.metadata.resource_status = got.metadata.resource_status
    assert api_client.get_rule("test_1") == base_rule_1

    base_rule_2 = api_client.create_rule("test_2", base_rule)
    assert base_rule_2.schedule == base_rule.schedule
    assert base_rule_2.input == base_rule.input
    assert base_rule_2.output == base_rule.output

    got_2 = api_client.get_rule("test_2")
    listed = api_client.list_rules()
    assert len(listed) == 2
    assert listed[0] == got
    assert listed[1] == got_2

    base_rule_2.metadata.created_timestamp = got_2.metadata.created_timestamp
    base_rule_2.metadata.created_by = got_2.metadata.created_by
    base_rule_2.metadata.modified_timestamp = got_2.metadata.modified_timestamp
    base_rule_2.metadata.version = got_2.metadata.version
    base_rule_2.metadata.resource_status = got_2.metadata.resource_status
    assert api_client.get_rule("test_2") == base_rule_2

    base_rule_2.input.stream.tables[0].name = "test_2"
    api_client.replace_rule("test_2", base_rule_2)

    got_2 = api_client.get_rule("test_2")
    base_rule_2.metadata.modified_timestamp = got_2.metadata.modified_timestamp
    base_rule_2.metadata.version = got_2.metadata.version
    base_rule_2.metadata.resource_status = got_2.metadata.resource_status

    assert api_client.get_rule("test_2") == base_rule_2

    api_client.delete_rule("test_1")
    listed = [
        item
        for item in api_client.list_rules()
        if item.metadata.resource_status != "deletionPending"
    ]
    assert len(listed) == 1
    assert listed[0] == base_rule_2
