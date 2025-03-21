
try:
    from pyspark.sql import SparkSession
except ImportError:
    raise Exception('Для использования Spark установите библиотеку с опцией [dev]: `pip install analytic-workspace-client[dev]`')


def build_spark_session():
    """ """
    return SparkSession.builder \
        .master('local[*]') \
        .config('spark.driver.host', '127.0.0.1') \
        .config('spark.ui.enabled', 'false') \
        .getOrCreate()

