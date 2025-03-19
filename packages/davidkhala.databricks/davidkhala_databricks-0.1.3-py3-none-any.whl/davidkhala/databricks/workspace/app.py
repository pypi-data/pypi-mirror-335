from typing import Iterator

from databricks.sdk.service.apps import App

from davidkhala.databricks.workspace.types import ClientWare


class SparkApp(ClientWare):

    def ls(self) -> Iterator[App]:
        """
        If not found, this will block until get one
        :return:
        """
        return self.apps.list()

    @property
    def apps(self):
        return self.client.apps

    def names(self) -> Iterator[str]:
        return (app.name for app in self.ls())

    def purge(self):
        for name in self.names():
            self.apps.stop_and_wait(name)
            self.apps.delete(name)
