from typing import Dict, Optional, Any, Union, List, Literal
from pathlib import Path
from collections import OrderedDict
import datetime
import inspect

from aw_client.core.compiler import ScriptCompiler
from aw_client.core.model_vault import Vault
from aw_client.core.spark import build_spark_session
from aw_client.core.bundle import NamedObjectsBundle
from aw_client.models.model_schema import ModelObject, ModelObjectField
from aw_etl.etl_blocks import ETLBlockActionResult
from .application import ETLBlockApplication
from .test_data import ModelObjectTestData
from .tools import build_dataframe, build_model_object, build_spark_schema
from .dto import ETLBlockMeta


try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql.types import DataType, StringType, DoubleType, TimestampType, LongType, BooleanType, \
        ByteType, ShortType, IntegerType, DecimalType, FloatType, DateType, StructType, StructField
except ImportError:
    raise Exception('Для использования Spark установите библиотеку с опцией [dev]: `pip install analytic-workspace-client[dev]`')



def get_etl_block_meta(block_path: Path) -> ETLBlockMeta:
    """ """
    block_meta_path = block_path / 'block_meta.json' if block_path.is_dir() else block_path

    if not block_meta_path.exists():
        raise Exception(f'Файл с метаданным блока не найден: {block_meta_path}')

    with open(block_meta_path, 'rt', encoding='utf-8') as f:
        return ETLBlockMeta.model_validate_json(f.read())


def get_etl_block_schema(block_path: Path, 
                         test_data: Union[ModelObjectTestData, List[ModelObjectTestData]],
                         params: Optional[Dict] = None, 
                         run_mode: Optional[Literal['']] = None, 
                         vault: Optional[Vault] = None,
                         model_script_code: Optional[str] = None) -> StructType:
    """ 
    Args:

    """
    block_code_path = block_path / 'block_code.py' if block_path.is_dir() else block_path
    
    if not block_code_path.exists():
        raise Exception(f'Файл с исходным кодом блока не найден: {block_code_path}')
    
    with open(block_code_path, 'rt', encoding='utf-8') as f:
        block_code = f.read()

    # Компиляция кода блока
    try:
        block_module = ScriptCompiler().compile(source_code=block_code, mode=ScriptCompiler.MODE_ETL_BLOCK)
    except ScriptCompiler.CannotCompile as e:
        raise Exception(f'Ошибка компиляции исходного кода блока: {e}')
    
    # Компиляция кода модели
    if model_script_code:
        try:
            model_module = ScriptCompiler().compile(source_code=model_script_code, mode=ScriptCompiler.MODE_ETL)
        except ScriptCompiler.CannotCompile as e:
            raise Exception(f'Ошибка компиляции исходного кода скрипта модели: {e}')
    else:
        model_module = None

    spark = build_spark_session()

    # Дочерние датафреймы
    dataframes = OrderedDict()
    for td in (test_data if isinstance(test_data, list) else [test_data]):
        df = build_dataframe(spark, td)
        if not dataframes:
            dataframes['child'] = df
    
    upstream_dataframes = NamedObjectsBundle(dataframes)

    # Дочерние схемы
    schemas = OrderedDict()
    for td in (test_data if isinstance(test_data, list) else [test_data]):
        schema = build_spark_schema(td)
        if not schemas:
            schemas['child'] = schema
        schemas[td.model_name] = schema

    upstream_schemas = NamedObjectsBundle(schemas)
    
    block_schema_parameters = inspect.signature(block_module['block_schema']).parameters

    app = ETLBlockApplication(
        spark_builder=build_spark_session,
        run_mode=run_mode or 'full',
        vault=vault or Vault(),
        model_module=model_module
    )

    child_objects_data = (test_data if isinstance(test_data, list) else [test_data]) if test_data is not None else None

    # Определение параметров для передачи
    block_schema_kwargs = {}
    if 'params' in block_schema_parameters:
        block_schema_kwargs['params'] = params
    if 'app' in block_schema_parameters:
        block_schema_kwargs['app'] = app
    if 'model_object' in block_schema_parameters:
        model_object = ModelObject(
            name='obj',
            model_name='obj',
            type='etl_block',
            fields=[],
            childs=[build_model_object(o) for o in child_objects_data]
        )
        block_schema_kwargs['model_object'] = model_object
    if 'schema' in block_schema_parameters:
        block_schema_kwargs['schema'] = upstream_schemas.first()
    if 'schemas' in block_schema_parameters:
        block_schema_kwargs['schemas'] = upstream_schemas
    if 'upstream_schema' in block_schema_parameters:
        block_schema_kwargs['upstream_schema'] = upstream_schemas.first()
    if 'upstream_schemas' in block_schema_parameters:
        block_schema_kwargs['upstream_schemas'] = upstream_schemas
    if 'df' in block_schema_parameters:
        block_schema_kwargs['df'] = upstream_dataframes.first()
    if 'dfs' in block_schema_parameters:
        block_schema_kwargs['dfs'] = upstream_dataframes
    if 'upstream_dataframe' in block_schema_parameters:
        block_schema_kwargs['upstream_dataframe'] = upstream_dataframes.first()
    if 'upstream_dataframes' in block_schema_parameters:
        block_schema_kwargs['upstream_dataframes'] = upstream_dataframes
    

    return block_module['block_schema'](**block_schema_kwargs)
    

def get_etl_block_data(block_path: Path, 
                       test_data: Union[ModelObjectTestData, List[ModelObjectTestData]],
                       params: Optional[Dict] = None, 
                       run_mode: Optional[Literal['']] = None, 
                       vault: Optional[Vault] = None,
                       model_script_code: Optional[str] = None) -> StructType:
    """ 
    Args:

    """
    block_code_path = block_path / 'block_code.py' if block_path.is_dir() else block_path
    
    if not block_code_path.exists():
        raise Exception(f'Файл с исходным кодом блока не найден: {block_code_path}')
    
    with open(block_code_path, 'rt', encoding='utf-8') as f:
        block_code = f.read()

    # Компиляция кода блока
    try:
        block_module = ScriptCompiler().compile(source_code=block_code, mode=ScriptCompiler.MODE_ETL_BLOCK)
    except ScriptCompiler.CannotCompile as e:
        raise Exception(f'Ошибка компиляции исходного кода блока: {e}')
    
    # Компиляция кода модели
    if model_script_code:
        try:
            model_module = ScriptCompiler().compile(source_code=model_script_code, mode=ScriptCompiler.MODE_ETL)
        except ScriptCompiler.CannotCompile as e:
            raise Exception(f'Ошибка компиляции исходного кода скрипта модели: {e}')
    else:
        model_module = None

    spark = build_spark_session()

    # Дочерние датафреймы
    dataframes = OrderedDict()
    for td in (test_data if isinstance(test_data, list) else [test_data]):
        df = build_dataframe(spark, td)
        if not dataframes:
            dataframes['child'] = df
        dataframes[td.model_name] = df
    
    upstream_dataframes = NamedObjectsBundle(dataframes)

    block_data_parameters = inspect.signature(block_module['block_data']).parameters

    app = ETLBlockApplication(
        spark_builder=build_spark_session,
        run_mode=run_mode or 'full',
        vault=vault or Vault(),
        model_module=model_module
    )

    child_objects_data = (test_data if isinstance(test_data, list) else [test_data]) if test_data is not None else None

    # Определение параметров для передачи
    block_data_kwargs = {}
    if 'params' in block_data_parameters:
        block_data_kwargs['params'] = params
    if 'app' in block_data_parameters:
        block_data_kwargs['app'] = app
    if 'model_object' in block_data_parameters:
        model_object = ModelObject(
            name='obj',
            model_name='obj',
            type='etl_block',
            fields=[],
            childs=[build_model_object(o) for o in child_objects_data]
        )
        block_data_kwargs['model_object'] = model_object
    if 'df' in block_data_parameters:
        block_data_kwargs['df'] = upstream_dataframes.first()
    if 'dfs' in block_data_parameters:
        block_data_kwargs['dfs'] = upstream_dataframes
    if 'upstream_dataframe' in block_data_parameters:
        block_data_kwargs['upstream_dataframe'] = upstream_dataframes.first()
    if 'upstream_dataframes' in block_data_parameters:
        block_data_kwargs['upstream_dataframes'] = upstream_dataframes
    
    return block_module['block_data'](**block_data_kwargs)
    

def run_block_action(
        block_path: Path,
        action_name: str,
        test_data: Union[ModelObjectTestData, List[ModelObjectTestData]],
        params: Optional[Dict] = None, 
        run_mode: Optional[Literal['']] = None, 
        vault: Optional[Vault] = None,
        model_script_code: Optional[str] = None
) -> ETLBlockActionResult:
    """ 
    Выполняет действие etl-блока 
    
    Args:
    -------------------------------------------------------
    block_path : Path
        Путь к исходным текстам блока
    """
    block_code_path = block_path / 'block_code.py' if block_path.is_dir() else block_path
    
    if not block_code_path.exists():
        raise Exception(f'Файл с исходным кодом блока не найден: {block_code_path}')
    
    with open(block_code_path, 'rt', encoding='utf-8') as f:
        block_code = f.read()

    # Компиляция кода блока
    try:
        block_module = ScriptCompiler().compile(source_code=block_code, mode=ScriptCompiler.MODE_ETL_BLOCK)
    except ScriptCompiler.CannotCompile as e:
        raise Exception(f'Ошибка компиляции исходного кода блока: {e}')
    
    # Проверяем, что функция для запуска действия объявлена в модуле блока
    block_action_function_name = f'block_action_{action_name}'
    if not block_action_function_name in block_module:
        raise Exception(f'Функция для обработки действия {block_action_function_name} '
                        'не найдена в исходном коде блока')
    
    # Компиляция кода модели
    if model_script_code:
        try:
            model_module = ScriptCompiler().compile(source_code=model_script_code, mode=ScriptCompiler.MODE_ETL)
        except ScriptCompiler.CannotCompile as e:
            raise Exception(f'Ошибка компиляции исходного кода скрипта модели: {e}')
    else:
        model_module = None

    spark = build_spark_session()

    # Дочерние схемы
    schemas = OrderedDict()
    for td in (test_data if isinstance(test_data, list) else [test_data]):
        schema = build_spark_schema(td)
        if not schemas:
            schemas['child'] = schema
        schemas[td.model_name] = schema

    upstream_schemas = NamedObjectsBundle(schemas)

    # Дочерние датафреймы
    dataframes = OrderedDict()
    for td in (test_data if isinstance(test_data, list) else [test_data]):
        df = build_dataframe(spark, td)
        if not dataframes:
            dataframes['child'] = df
        dataframes[td.model_name] = df
    
    upstream_dataframes = NamedObjectsBundle(dataframes)

    block_action_parameters = inspect.signature(block_module[block_action_function_name]).parameters

    app = ETLBlockApplication(
        spark_builder=build_spark_session,
        run_mode=run_mode or 'full',
        vault=vault or Vault(),
        model_module=model_module
    )

    child_objects_data = (test_data if isinstance(test_data, list) else [test_data]) if test_data is not None else None

    block_action_kwargs = {}
    if 'params' in block_action_parameters:
        block_action_kwargs['params'] = params
    if 'app' in block_action_parameters:
        block_action_kwargs['app'] = app
    if 'model_object' in block_action_parameters:
        model_object = ModelObject(
            name='obj',
            model_name='obj',
            type='etl_block',
            fields=[],
            childs=[build_model_object(o) for o in child_objects_data]
        )
        block_action_kwargs['model_object'] = model_object
    if 'schema' in block_action_parameters:
        block_action_kwargs['schema'] = upstream_schemas.first()
    if 'schemas' in block_action_parameters:
        block_action_kwargs['schemas'] = upstream_schemas
    if 'upstream_schema' in block_action_parameters:
        block_action_kwargs['upstream_schema'] = upstream_schemas.first()
    if 'upstream_schemas' in block_action_parameters:
        block_action_kwargs['upstream_schemas'] = upstream_schemas
    if 'df' in block_action_parameters:
        block_action_kwargs['df'] = upstream_dataframes.first()
    if 'dfs' in block_action_parameters:
        block_action_kwargs['dfs'] = upstream_dataframes
    if 'upstream_dataframe' in block_action_parameters:
        block_action_kwargs['upstream_dataframe'] = upstream_dataframes.first()
    if 'upstream_dataframes' in block_action_parameters:
        block_action_kwargs['upstream_dataframes'] = upstream_dataframes
    
    return block_module[block_action_function_name](**block_action_kwargs)



