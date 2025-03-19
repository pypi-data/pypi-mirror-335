from typing import Iterator

from databricks.sdk.service.jobs import BaseJob, Job

from davidkhala.databricks.workspace.types import ClientWare


class Job(ClientWare):
    def ls(self) -> Iterator[BaseJob]:
        return self.client.jobs.list()

    def get(self, job_id: int) -> Job:
        return self.client.jobs.get(job_id)
