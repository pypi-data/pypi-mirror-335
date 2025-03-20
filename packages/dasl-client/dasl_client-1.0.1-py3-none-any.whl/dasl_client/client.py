from copy import deepcopy
from typing import Optional, List

from dasl_api import (
    api,
    WorkspaceV1Api,
    WorkspaceV1CreateWorkspaceRequest,
    CoreV1Api,
    DbuiV1Api,
    DbuiV1TransformRequestTransformsInner,
    DbuiV1TransformRequestInput,
    DbuiV1TransformResponse,
)

from dasl_client.auth.auth import (
    Authorization,
    DatabricksTokenAuth,
    ServiceAccountKeyAuth,
)
from dasl_client.conn.conn import get_base_conn
from dasl_client.errors.errors import ConflictError, error_handler

from .types import *
from .helpers import Helpers


class Client:
    """
    Antimatter security lakehouse client.
    """

    def __init__(
        self,
        auth: Authorization,
    ):
        """
        Initialize a new client. You should generally prefer to use
        the new_workspace function if creating a new workspace or the
        for_workspace function if connecting to an existing workspace.

        :param auth: Authorization instance for authorizing requests to
            the dasl control plane.
        :returns Client
        """
        self.auth = auth

    @staticmethod
    def new_workspace(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Register a new workspace and return a client for it.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, the
            request will fail.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns Client
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()
            admin_config = AdminConfig(
                workspace_url=workspace_url,
                app_client_id=app_client_id,
                service_principal_id=service_principal_id,
                service_principal_secret=service_principal_secret,
            )
            workspace_name = Helpers.workspace_name_from_url(workspace_url)
            api_key = (
                api.WorkspaceV1Api(api_client=get_base_conn(host=dasl_host))
                .workspace_v1_create_workspace(
                    WorkspaceV1CreateWorkspaceRequest(
                        admin_user=admin_email,
                        workspace_name=workspace_name,
                        admin_config=admin_config.to_api_obj().spec,
                    )
                )
                .admin_service_account.apikey
            )
            return Client(
                ServiceAccountKeyAuth(workspace_name, api_key, host=dasl_host),
            )

    # TODO: should we allow user to use an API key here?
    @staticmethod
    def for_workspace(
        workspace_url: Optional[str] = None,
        api_token: Optional[str] = None,
        service_account_token: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Create a client for the argument workspace, if specified, or
        the current workspace if running in databricks notebook context.

        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise,
            requests using the client will fail.
        :param api_token: Your Databricks API token, which is used to
            auth to Databricks and subsequently prove your entitlement
            to the DASL backend. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise,
            request using the client will fail.
        :param service_account_token: Databricks service account token.
            If provided, the client will use this token for auth instead
            of the api_token.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns Client
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()
            if api_token is None:
                api_token = Helpers.api_token()

            if service_account_token is None:
                return Client(
                    DatabricksTokenAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        api_token,
                        host=dasl_host,
                    ),
                )
            else:
                return Client(
                    DatabricksServiceAccountKeyAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        service_account_token,
                        host=dasl_host,
                    )
                )

    @staticmethod
    def new_or_existing(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        api_token: Optional[str] = None,
        service_account_token: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Initialize a new client for the workspace associated with the
        argument Databricks workspace_url. If no such workspace exists,
        one will be created for you.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created. Ignored if
            the workspace already exists.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace. If
            the workspace already exists, the existing config will be
            updated to use this client ID.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
            If the workspace already exists, the existing config will be
            updated to use this service principal ID.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf. If the workspace already exists, the existing config
            will be updated to use this service principal secret.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, the
            request will fail. If the workspace already exists, the
            existing config will be updated to use this value.
        :param api_token: Your Databricks API token, which is used to
            auth to Databricks and subsequently prove your entitlement
            to the DASL backend. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, the
            request will fail. Ignored if the workspace doesn't exist.
        :param service_account_token: Databricks service account token.
            If provided, the client will use this token for auth instead
            of the api_token. Ignored if the workspace doesn't exist.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns Client
        """
        try:
            return Client.new_workspace(
                admin_email,
                app_client_id,
                service_principal_id,
                service_principal_secret,
                workspace_url,
                dasl_host,
            )
        except ConflictError:
            result = Client.for_workspace(
                workspace_url, api_token, service_account_token, dasl_host
            )
            result.put_admin_config(
                AdminConfig(
                    workspace_url=workspace_url,
                    app_client_id=app_client_id,
                    service_principal_id=service_principal_id,
                    service_principal_secret=service_principal_secret,
                )
            )
            return result

    def _workspace_client(self) -> WorkspaceV1Api:
        return WorkspaceV1Api(self.auth.client())

    def _core_client(self) -> CoreV1Api:
        return CoreV1Api(self.auth.client())

    def _dbui_client(self) -> DbuiV1Api:
        return DbuiV1Api(self.auth.client())

    def _workspace(self) -> str:
        return self.auth.workspace()

    def get_admin_config(self) -> AdminConfig:
        """
        Retrieve the AdminConfig from the DASL server. Note that the
        service principal secret will be redacted server side, so if you
        plan to make changes and issue a request using put_admin_config,
        you will need to repopulate the service_principal_secret correctly
        before passing the result back to put_admin_config.

        :returns AdminConfig
        """
        with error_handler():
            return AdminConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_admin_config(
                    self._workspace()
                )
            )

    def put_admin_config(
        self,
        config: AdminConfig,
    ) -> None:
        """
        Update the AdminConfig stored in the DASL server. See the AdminConfig
        docs for details about its contents.

        :param config: AdminConfig to replace the existing. Note that the
            service principal credentials will be verified server side before
            the request is accepted.
        """
        with error_handler():
            self._workspace_client().workspace_v1_put_admin_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_config(self) -> WorkspaceConfig:
        """
        Retrieve the WorkspaceConfig from the DASL server. The returned
        value can be updated directly and passed to put_config in order
        to make changes.
        """
        with error_handler():
            return WorkspaceConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_config(self._workspace())
            )

    def put_config(
        self,
        config_in: WorkspaceConfig,
    ) -> None:
        """
        Update the WorkspaceConfig stored in the DASL server. See the
        WorkspaceConfig docs for dtails about its contents.

        :param config_in: WorkspaceConfig to replace the existing.
        :returns: WorkspaceConfig. Note that the returned value is a
            clone of config_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            config = deepcopy(config_in)
            if config.metadata is None:
                config.metadata = Metadata(
                    name="config",
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            config.metadata.version = None

            self._workspace_client().workspace_v1_put_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_datasource(self, name: str) -> DataSource:
        """
        Get the DataSource with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_datasource
        in order to make changes.

        :param name: The unique name of the DataSource within this workspace
        :returns DataSource
        """
        with error_handler():
            return DataSource.from_api_obj(
                self._core_client().core_v1_get_data_source(self._workspace(), name)
            )

    def delete_datasource(self, name: str) -> None:
        """
        Delete the DataSource with the argument name from the DASL server.
        The DataSource will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the DataSource within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_data_source(self._workspace(), name)

    def list_datasources(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> List[DataSource]:
        """
        List the DataSources in this workspace. Each element of the returned
        list contains all fields in the DataSource as if it were fetched
        using the get_datasource method.

        :param cursor: The pagination cursor returned from a previous
            request.
        :param limit: The maximum number of DataSources to include in
            the response. Note that the server also imposes a maximum,
            so this serves as an upper bound; there is no guarantee that
            you will receive this number of DataSources in the response,
            even if at least this many exist.
        :returns List[DataSource]: The requested list of DataSources.
        """
        with error_handler():
            response = self._core_client().core_v1_list_data_sources(
                workspace=self._workspace(), cursor=cursor, limit=limit
            )
            return [DataSource.from_api_obj(item) for item in response.items]

    def create_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Create a new DataSource. The chosen name must be unique for your
        workspace, and cannot refer to a DataSource that already exists
        and has not been deleted. See the documentation for delete_datasource
        as there are some caveats around name reuse.

        :param name: The unique name of this DataSource in the workspace.
        :param ds_in: The specification of the DataSource to create. See
            the documentation for the DataSource type for more details.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_data_source(
                self._workspace(), ds.to_api_obj()
            )
            return DataSource.from_api_obj(result)

    def replace_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Replace an existing DataSource. The name must refer to a DataSource
        that already exists in your workspace.

        :param name: The name of the existing DataSource to replace.
        :param ds_in: The specification of the DataSource taking the place
            of the existing DataSource.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            ds.metadata.version = None

            result = self._core_client().core_v1_replace_data_source(
                self._workspace(),
                name,
                ds.to_api_obj(),
            )
            return DataSource.from_api_obj(result)

    def get_rule(self, name: str) -> Rule:
        """
        Get the Rule with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_rule
        in order to make changes.

        :param name: The unique name of the Rule within this workspace
        :returns Rule
        """
        with error_handler():
            return Rule.from_api_obj(
                self._core_client().core_v1_get_rule(self._workspace(), name)
            )

    def delete_rule(self, name: str) -> None:
        """
        Delete the Rule with the argument name from the DASL server.
        The Rule will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the Rule within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_rule(self._workspace(), name)

    def list_rules(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Rule]:
        """
        List the Rules in this workspace. Each element of the returned
        list contains all fields in the Rule as if it were fetched
        using the get_rule method.

        :param cursor: The pagination cursor returned from a previous
            request.
        :param limit: The maximum number of Rules to include in the
            response. Note that the server also imposes a maximum, so
            this serves as an upper bound; there is no guarantee that
            you will receive this number of Rules in the response,
            even if at least this many exist.
        :returns List[Rule]: The requested list of Rules.
        """
        with error_handler():
            response = self._core_client().core_v1_list_rules(
                workspace=self._workspace(), cursor=cursor, limit=limit
            )
            return [Rule.from_api_obj(item) for item in response.items]

    def create_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Create a new Rule. The chosen name must be unique for your
        workspace, and cannot refer to a Rule that already exists
        and has not been deleted. See the documentation for delete_rule
        as there are some caveats around name reuse.

        :param name: The unique name of this Rule in the workspace.
        :param rule_in: The specification of the Rule to create. See
            the documentation for the Rule type for more details.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_rule(
                self._workspace(), rule.to_api_obj()
            )
            return Rule.from_api_obj(result)

    def replace_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Replace an existing Rule. The name must refer to a Rule
        that already exists in your workspace.

        :param name: The name of the existing Rule to replace.
        :param rule_in: The specification of the Rule taking the place
            of the existing Rule.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            rule.metadata.version = None

            result = self._core_client().core_v1_replace_rule(
                self._workspace(),
                name,
                rule.to_api_obj(),
            )
        return Rule.from_api_obj(result)

    def adhoc_transform(
        self,
        warehouse: str,
        preset: str,
        transforms: List[DbuiV1TransformRequestTransformsInner],
        input: Optional[DbuiV1TransformRequestInput] = None,
        autoloader_input: Optional[CoreV1DataSourceAutoloaderSpec] = None,
    ) -> DbuiV1TransformResponse:
        """
        Run a sequence of ADHOC transforms against a SQL warehouse to
        mimic the operations performed by a datasource.

        :param warehouse: The warehouse ID to run the transforms against.
        :param transforms: The sequence to transforms to run.
        :param input: The source of data to use.
        :param autoloader_input: The autoload specifications.
        :return: a DbuiV1TransformResponse object containing the results
            after running the transforms.
        :raises: NotFoundError if the rule does not exist
        """
        with error_handler():
            if autoloader_input is None:
                autoloader_input = Field(default=None, alias="autoloaderInput")
            request = DbuiV1TransformRequest(
                input=input,
                autoloader_input=autoloader_input,
                use_preset=preset,
                transforms=transforms,
            )
            return self._dbui_client().dbui_v1_transform(
                self._workspace(), warehouse, request
            )

    def get_observable_events(
        self,
        warehouse: str,
        kind: str,
        value: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dbui.ObservableEvents.EventsList:
        """
        Get the observable events associated with a specific field and value.

        :param warehouse: The warehouse id to perform the operation on
        :param kind: The observable kind
        :param value: The observable value
        :param cursor: A cursor to be used when paginating results
        :param limit: A limit of the number of results to return
        :returns EventsList
        """
        with error_handler():
            return Dbui.ObservableEvents.EventsList.from_api_obj(
                self._dbui_client().dbui_v1_get_observable_events(
                    self._workspace(),
                    warehouse=warehouse,
                    kind=kind,
                    value=value,
                    cursor=cursor,
                    limit=limit,
                )
            )
