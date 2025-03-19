from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState, StatementResponse, GetWarehouseResponse

from davidkhala.databricks.workspace.types import ClientWare


class Warehouse(ClientWare):
    warehouse_id: str

    def __init__(self, client: WorkspaceClient, warehouse_id: str = None):
        """
        :param client:
        :param warehouse_id: e.g. '7969d92540da7f02'
        """
        super().__init__(client)
        self.warehouse_id = warehouse_id

    def get_one(self):
        for warehouse in self.ls():
            self.warehouse_id = warehouse.id
            return self

    @staticmethod
    def from_http_path(client: WorkspaceClient, http_path: str):
        """
        :param client:
        :param http_path: e.g. '/sql/1.0/warehouses/7969d92540da7f02'
        :return:
        """
        return Warehouse(client, http_path.split('/')[-1])

    def ls(self):
        return self.client.warehouses.list()

    def run_async(self, query: str):
        return self.client.statement_execution.execute_statement(query, self.warehouse_id)

    def run(self, query: str) -> StatementResponse:
        r = self.run_async(query)
        return self.wait_until_statement_success(r)

    def wait_until_statement_success(self, r: StatementResponse) -> StatementResponse:
        if r.status.state == StatementState.PENDING:
            next_response = self.client.statement_execution.get_statement(r.statement_id)
            return self.wait_until_statement_success(next_response)
        assert r.status.state == StatementState.SUCCEEDED
        return r

    def start(self) -> GetWarehouseResponse:
        return self.client.warehouses.start_and_wait(self.warehouse_id)

    def stop(self) -> GetWarehouseResponse:
        return self.client.warehouses.stop_and_wait(self.warehouse_id)

    @staticmethod
    def pretty(r: StatementResponse):
        return {
            'schema': r.manifest.schema.as_dict().get('columns'),
            'data': r.result.data_array,
        }
