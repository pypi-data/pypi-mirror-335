from davidkhala.spark.context import Wrapper


class DatabricksContext(Wrapper):
    """
    Extends :class:`SparkContext`
    """
    @property
    def sparkHome(self):
        _ = self.sc.sparkHome
        assert _ == '/databricks/spark'
        return _

    @property
    def appName(self):
        _ = self.sc.appName
        assert _ == 'Databricks Shell'
        return _

    @property
    def environment(self):
        _ = self.sc.environment
        assert _['PYTHONHASHSEED'] == '0'
        return _

    @property
    def pythonExec(self):
        _ = self.sc.pythonExec
        assert _ == '/databricks/python/bin/python'
        return _
