from typing import TypedDict

from davidkhala.gcp.auth.service_account import ServiceAccount
from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.connect.streaming.readwriter import DataStreamReader, DataStreamWriter

from davidkhala.databricks.connect import Session


class AuthOptions(TypedDict):
    clientId: str
    clientEmail: str
    privateKey: str
    privateKeyId: str
    projectId: str


class PubSub:
    auth: AuthOptions
    spark: Session
    source: DataStreamReader
    sink: DataStreamWriter

    def __init__(self, auth: AuthOptions | None, spark: SparkSession):
        self.auth = auth
        s = Session(spark)
        assert s.is_servermore()  # Not support in serverless compute
        self.spark = s

    def with_service_account(self, info: ServiceAccount.Info):
        self.auth = AuthOptions(
            clientId=info.get('client_id'),
            clientEmail=info.get('client_email'),
            privateKey=info.get('private_key'),
            privateKeyId=info.get('private_key_id'),
            projectId=info.get('project_id'),
        )
        return self

    @property
    def subscription_id(self) -> str | None:
        if self.source:
            # Databricks Connect
            return self.source._options["subscriptionId"]

    def read_stream(self, topic_id, subscription_id=None):
        _sub_id = subscription_id
        if subscription_id is None:
            import uuid
            _sub_id = f"databricks{uuid.uuid4().hex}"
            print(f"use random assigned subscription_id=[{_sub_id}]")

        self.source = (
            self.spark.readStream.format("pubsub")
            .option('deleteSubscriptionOnStreamStop', subscription_id is None)
            .option("subscriptionId", _sub_id)
            .option("topicId", topic_id)
            .options(**self.auth)
        )
        return self

    def read_start(self) -> DataFrame:
        pubsub_df = self.source.load()
        assert pubsub_df.isStreaming == True
        return pubsub_df

    def disconnect(self):
        self.spark.disconnect()
