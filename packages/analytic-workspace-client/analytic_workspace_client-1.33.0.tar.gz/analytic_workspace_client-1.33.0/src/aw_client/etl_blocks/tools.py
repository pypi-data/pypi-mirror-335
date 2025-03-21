from typing import Any
import datetime


from aw_client.models.model_schema import ModelObject, ModelObjectField
from .test_data import ModelObjectTestData



try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql.types import DataType, StringType, DoubleType, TimestampType, LongType, BooleanType, \
        ByteType, ShortType, IntegerType, DecimalType, FloatType, DateType, StructType, StructField
except ImportError:
    raise Exception('Для использования Spark установите библиотеку с опцией [dev]: `pip install analytic-workspace-client[dev]`')


def build_spark_schema(test_data: ModelObjectTestData) -> StructType:
    """ """
    if test_data.schema is not None:
        return StructType(fields=[
            StructField(sf['model_name'], spark_type_for_simple_type(sf['simple_type']), True) for sf in test_data.schema
        ])
    return StructType(fields=[
        StructField(n, spark_type_for_python_value(v), True) for n, v in test_data.rows[0].items()
    ])


def build_dataframe(spark: SparkSession, test_data: ModelObjectTestData) -> DataFrame:
    """ """
    return spark.createDataFrame(test_data.rows, schema=build_spark_schema(test_data))


def build_model_object(test_data: ModelObjectTestData):
    """ """
    if test_data.schema is not None:
        fields = [
            ModelObjectField(name=f['model_name'], model_name=f['model_name'], simple_type=f['simple_type']) for f in test_data.schema
        ]
    else:
        fields = [
            ModelObjectField(name=n, model_name=n, simple_type=simple_type_for_python_value(v)) for n, v in test_data.rows[0].items()
        ]
    return ModelObject(
        name=test_data.model_name,
        model_name=test_data.model_name,
        type='table',
        sql_text=None,
        fields=fields
    )




def spark_type_for_simple_type(simple_type: str) -> DataType:
    """ 
    """
    if simple_type == 'number':
        return LongType()
    elif simple_type == 'float':
        return DoubleType()
    elif simple_type == 'date':
        return TimestampType()
    elif simple_type == 'bool':
        return BooleanType()
    else:
        return StringType()
        

def spark_type_for_python_value(value: Any) -> DataType:
    """ 
    Returns Spark type
    """
    if isinstance(value, datetime.date):
        return DateType()
    if isinstance(value, datetime.datetime):
        return TimestampType()
    if isinstance(value, int):
        return LongType()
    if isinstance(value, float):
        return DoubleType()
    if isinstance(value, bool):
        return BooleanType()
    return StringType()


def simple_type_for_python_value(value: Any) -> str:
    """ """
    if isinstance(value, datetime.date):
        return 'date'
    if isinstance(value, datetime.datetime):
        return 'date'
    if isinstance(value, int):
        return 'number'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, bool):
        return 'bool'
    return 'string'