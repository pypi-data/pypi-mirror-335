import os

from databricks.connect import DatabricksSession, cli
from databricks.sdk.config import Config
from davidkhala.spark.session import ServerMore
from pyspark.sql.connect.session import SparkSession


class DatabricksConnect:

    @staticmethod
    def ping(serverless: bool = False):
        if serverless:
            os.environ['DATABRICKS_SERVERLESS_COMPUTE_ID'] = 'auto'
        cli.test()

    @staticmethod
    def get() -> (SparkSession, bool):
        builder = DatabricksSession.builder
        try:
            spark = builder.validateSession(True).getOrCreate()
            return spark, Session(spark).serverless
        except Exception as e:
            if str(e) == 'Cluster id or serverless are required but were not specified.':
                return builder.serverless(True).getOrCreate(), True
            else:
                raise e

    @staticmethod
    def from_servermore(config: Config) -> SparkSession:
        _builder = DatabricksSession.builder.validateSession(True)
        _builder.host(config.host)
        _builder.token(config.token)
        _builder.clusterId(config.cluster_id)
        return _builder.getOrCreate()

    @staticmethod
    def from_serverless(config: Config) -> SparkSession:
        # session validation flag is in vain. It will be overwritten
        # > Disable session validation for serverless
        _builder = DatabricksSession.builder
        _builder.host(config.host)
        _builder.token(config.token)
        _builder.serverless(True)
        return _builder.getOrCreate()


class Session(ServerMore):
    @property
    def serverless(self) -> bool:
        # assert on serverless config
        return (
                self.clusterId is None
                and self.conf.get('spark.sql.ansi.enabled') == 'true'
                and self.conf.get('spark.sql.shuffle.partitions', ) == 'auto'
                and self.conf.__len__() == 2
        )

    @property
    def appName(self):
        if not self.serverless:
            return super().appName

    @property
    def clusterId(self) -> str | None:
        return self.conf.get("spark.databricks.clusterUsageTags.clusterId")

    def is_servermore(self, cluster_id: str = None) -> bool:
        cluster_check = self.clusterId == cluster_id if cluster_id else self.clusterId is not None
        return (
                self.serverless is False
                and cluster_check
                and self.conf.__len__() > 427
        )

    @property
    def conf(self) -> dict:
        return self.spark.conf.getAll
