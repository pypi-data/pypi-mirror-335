import json

from databricks.sdk.errors import NotFound
from databricks.sdk.service.catalog import TableInfo
from davidkhala.syntax.js import Array

from davidkhala.databricks.workspace.types import ClientWare


class Table(ClientWare):
    """
    NOTE: table create is not supported by SDK. Use dataframe instead.
    """

    def get(self, full_name: str):
        return Table.pretty(self._get(full_name))

    def column_names(self, full_name: str) -> list[str]:
        return list(map(lambda column: column.name, self._get(full_name).columns))

    def _get(self, full_name: str) -> TableInfo:
        return self.client.tables.get(full_name)

    def exists(self, full_name: str) -> bool:
        r = self.client.tables.exists(full_name)
        return r.table_exists

    def list(self, catalog_name: str, schema_name: str):
        return self.client.tables.list(catalog_name, schema_name)

    def delete(self, full_name: str):
        try:
            return self.client.tables.delete(full_name)
        except NotFound as e:
            if str(e) == f"Table '{full_name}' does not exist.":
                return
            raise e

    @staticmethod
    def pretty(table: TableInfo):
        return {
            'catalog_name': table.catalog_name,
            'columns': Array(table.columns).map(lambda column: {
                'name': column.name,
                'nullable': column.nullable,
                'type': json.loads(column.type_json)['type']
            }),
            "data_source_format": table.data_source_format.name,
            'name': table.name,
            'schema_name': table.schema_name,
            'id': table.table_id,
        }
