from typing import Iterator

from databricks.sdk import WorkspaceExt
from databricks.sdk.service.workspace import ObjectInfo, ObjectType, ImportFormat

from davidkhala.databricks.workspace import APIClient, Workspace


class API(APIClient):

    def ls(self, path="/"):
        """
        function to retrieve objects within specified path
        :param path:
        :return:
        """
        return self.get('/workspace/list', {'path': path})

    def scan_notebooks(self, path="/") -> list:
        """
        Get Notebook Paths
        :param path:
        :return:
        """
        result = []
        response = self.ls(path)
        if "objects" in response:
            for object_item in response["objects"]:
                if object_item["object_type"] == "NOTEBOOK":
                    result.append([object_item["object_id"], object_item["path"]])
                elif object_item["object_type"] == "DIRECTORY":
                    result = result + self.scan_notebooks(object_item["path"])
        return result


class SDK:
    def __init__(self, w: WorkspaceExt):
        self.workspace = w

    @staticmethod
    def from_workspace(w: Workspace):
        return SDK(w.client.workspace)

    def upload_notebook(self, local_notebook_path: str, target_path, *, overwrite=True):
        from base64 import b64encode

        with open(local_notebook_path, encoding="utf-8") as file:
            self.workspace.import_(
                target_path,
                content=b64encode(file.read().encode()).decode(),
                format=ImportFormat.JUPYTER,
                overwrite=overwrite,
            )

    def ls(self, path="/") -> Iterator[ObjectInfo]:
        return self.workspace.list(path, recursive=True)

    def get_by(self, *, notebook_id: str | int = None, path: str = None) -> str | None:
        for o in self.ls():
            if o.object_type == ObjectType.NOTEBOOK:
                if notebook_id and o.object_id == int(notebook_id):
                    return o.path
                if path and path in o.path:
                    return str(o.object_id)
