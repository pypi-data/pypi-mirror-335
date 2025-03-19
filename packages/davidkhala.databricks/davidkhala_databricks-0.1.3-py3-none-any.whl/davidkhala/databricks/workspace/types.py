from databricks.sdk import WorkspaceClient


class ClientWare:
    def __init__(self, client: WorkspaceClient):
        self.client = client