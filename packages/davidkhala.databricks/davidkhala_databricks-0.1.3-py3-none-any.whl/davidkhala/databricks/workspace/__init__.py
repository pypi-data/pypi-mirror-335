import pathlib

from databricks.sdk import WorkspaceClient
from databricks.sdk.config import Config
from databricks.sdk.core import ApiClient
from databricks.sdk.service.iam import User


class Workspace:
    client: WorkspaceClient

    def __init__(self, client: WorkspaceClient = None):
        if client is None:
            client = WorkspaceClient()
        self.client = client

    @staticmethod
    def from_local():
        from davidkhala.databricks.local import CONFIG_PATH
        if not pathlib.Path(CONFIG_PATH).exists():
            raise FileNotFoundError(CONFIG_PATH + " does not exist")
        return Workspace()

    @property
    def config(self) -> Config:
        """
        It returns raw token content. TAKE CARE for secret leakage.
        :return: {'host':'https://adb-662901427557763.3.azuredatabricks.net', 'token':'', 'auth_type':'pat'}
        """
        return self.client.config

    @property
    def config_token(self):
        return self.config.as_dict().get('token')

    @property
    def me(self) -> User:
        return self.client.current_user.me()

    @property
    def catalog(self) -> str:
        """
        :return: default catalog name
        """
        from davidkhala.databricks.workspace.catalog import Catalog

        return Catalog(self.client).default

    @property
    def cloud(self):
        token: str = self.config.token
        if token is not None:

            if token.startswith('https://adb-') and token.endswith('.azuredatabricks.net'):
                # adb-662901427557763.3.azuredatabricks.net
                return 'azure'
            elif token.startswith('https://dbc-') and token.endswith('.cloud.databricks.com'):
                # dbc-8df7b30e-676a.cloud.databricks.com
                return "aws"
            elif token.endswith('.gcp.databricks.com'):
                # 1105010096141051.1.gcp.databricks.com
                return "gcp"

    @property
    def metastore(self):
        """
        :return: current metastore
        """
        return self.client.metastores.current()

    @property
    def dbutils(self):
        return self.client.dbutils

    @property
    def api_client(self):
        return APIClient(self.client)


class APIClient:
    api_version = '/api/2.0'
    client: ApiClient

    def __init__(self, client: WorkspaceClient):
        self.client = client.api_client

    def get(self, route, data=None):
        return self.client.do(method='GET', path=self.api_version + route, body=data)
