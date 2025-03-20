from databricks.sdk.runtime import dbutils


class Helpers:
    default_dasl_host = "https://api.prod.sl.antimatter.io"

    @staticmethod
    def databricks_context():
        # TODO: test what happens in non-notebook context
        return dbutils.notebook.entry_point.getDbutils().notebook().getContext()

    @staticmethod
    def current_workspace_url() -> str:
        base_url = Helpers.databricks_context().browserHostName().get()
        return f"https://{base_url}"

    @staticmethod
    def api_token() -> str:
        return Helpers.databricks_context().apiToken().get()

    @staticmethod
    def workspace_name_from_url(url: str) -> str:
        # assumes the url is of the form <scheme>://<workspace name>\..*
        return url.split("//")[1].split(".")[0]
