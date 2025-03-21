from typing import Optional, Callable

try:
    from pyspark.sql import SparkSession
except ImportError:
    raise Exception('Для использования Spark установите библиотеку с опцией [dev]: `pip install analytic-workspace-client[dev]`')

from aw_client.core.model_vault import Vault
from aw_client.core.compiler import CompiledModule


class ETLBlockApplication:
    """ """
    def __init__(self, 
                 spark_builder: Callable, 
                 run_mode: str, 
                 vault: Vault,
                 model_module: Optional[CompiledModule] = None):
        self._spark_builder = spark_builder
        self._spark = None
        self._run_model = run_mode
        self._model_module = model_module
        self._vault = vault
    
    @property
    def spark(self) -> SparkSession:
        if self._spark is None:
            self._spark = self._spark_builder()
        return self._spark
    
    @property
    def is_spark_initialized(self) -> bool:
        return self._spark is not None
    
    @property
    def model_module(self) -> Optional[CompiledModule]:
        """ """
        return self._model_module

    @property
    def vault(self) -> Vault:
        """ """
        return self._vault

    @property
    def run_mode(self) -> str:
        """ """
        return self.run_mode
    