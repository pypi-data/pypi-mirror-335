from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import platform

from davidkhala.databricks.workspace.types import ClientWare


class Catalog(ClientWare):

    @property
    def catalogs(self):
        return self.client.catalogs

    @property
    def default(self):
        """
        :return: default catalog name
        """
        return self.client.settings.default_namespace.get().namespace.value

    def create(self, name, *, with_metastore_level_storage=False, storage_root=None):

        if self.get(name):
            return

        if with_metastore_level_storage:
            return self.catalogs.create(name)
        else:
            if storage_root is None:
                storage_root = self.get().storage_root
            return self.catalogs.create(name, storage_root=storage_root)

    def get(self, name=None):
        if not name:
            name = self.default
        try:
            return self.catalogs.get(name)
        except platform.NotFound as e:
            if str(e) == f"Catalog '{name}' does not exist.":
                return None
            else:
                raise e

    def delete(self, name):
        return self.catalogs.delete(name, force=True)


class Schema:
    default = 'default'
    client: WorkspaceClient
    name = default
    catalog: str

    def __init__(self, client: WorkspaceClient, name=None, catalog: str = None):
        self.client = client
        if not catalog:
            catalog = Catalog(self.client).default
        self.catalog = catalog
        if name:
            self.name = name

    @property
    def schemas(self):
        return self.client.schemas

    def get(self):
        try:
            return self.schemas.get(f"{self.catalog}.{self.name}")
        except platform.NotFound as e:
            if str(e) == f"Schema '{self.catalog}.{self.name}' does not exist.":
                return None

    def create(self):
        try:
            return self.schemas.create(self.name, self.catalog)
        except platform.BadRequest as e:
            if str(e) == f"Schema '{self.name}' already exists":
                return
            raise e

    def delete(self):
        try:
            return self.schemas.delete(f"{self.catalog}.{self.name}", force=True)
        except platform.NotFound as e:
            if str(e) == f"Schema '{self.catalog}.{self.name}' does not exist.":
                return None
            raise e
