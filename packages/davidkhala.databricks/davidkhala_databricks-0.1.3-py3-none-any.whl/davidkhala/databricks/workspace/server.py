from typing import Iterator, List
from urllib.error import HTTPError

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterDetails, PythonPyPiLibrary, Library as NativeLibrary, \
    LibraryInstallStatus, LibraryFullStatus

from davidkhala.databricks.workspace.types import ClientWare


class ClusterWare(ClientWare):
    def __init__(self, client: WorkspaceClient):
        super().__init__(client)
        self.cluster_id = client.config.cluster_id

    def start(self):
        self.client.clusters.ensure_cluster_is_running(self.cluster_id)


class Cluster(ClusterWare):

    def clusters(self) -> Iterator[ClusterDetails]:
        return self.client.clusters.list()

    def cluster_ids(self) -> Iterator[str]:
        return (cluster.cluster_id for cluster in self.clusters())

    def as_one(self):
        if self.cluster_id is None:
            got = next(self.cluster_ids())
            self.cluster_id = got
        return self

    def pollute(self):
        self.client.config.cluster_id = self.cluster_id

    def stop(self):
        self.client.clusters.delete_and_wait(self.cluster_id)


class Library(ClusterWare):
    @staticmethod
    def from_pypi(*packages: PythonPyPiLibrary) -> List[NativeLibrary]:
        return list(map(lambda package: NativeLibrary(pypi=package), packages))

    def add_async(self, *packages: PythonPyPiLibrary):
        self.client.libraries.install(self.cluster_id, Library.from_pypi(*packages))

    def add(self, package_name: str):
        self.start()
        package = PythonPyPiLibrary(package=package_name)
        self.add_async(package)
        status = None
        while status != LibraryInstallStatus.INSTALLED:
            p = self.get(package.package)
            if p is None:
                raise HTTPError(self.client.config.host, 404,
                                f"package {package.package} not found on cluster {self.cluster_id}")
            status = p.status
            if status == LibraryInstallStatus.FAILED: raise RuntimeError(p.messages)

    def uninstall_a(self, package_name: str):
        self.uninstall_async(PythonPyPiLibrary(package=package_name))

    def uninstall_async(self, *packages: PythonPyPiLibrary):
        """
        The libraries won't be uninstalled until the cluster is restarted
        """
        self.client.libraries.uninstall(self.cluster_id, Library.from_pypi(*packages))

    def get(self, name) -> LibraryFullStatus | None:
        for library in self.list():
            package_name = library.library.pypi.package
            if name in [package_name, package_name.split("==")[0]]:
                return library

    def list(self, *, with_status: LibraryInstallStatus = None) -> Iterator[LibraryFullStatus]:
        for library in self.client.libraries.cluster_status(self.cluster_id):
            if with_status is not None and library.status != with_status: continue
            yield library
