from typing import List, Tuple, Optional

import builtins


class CompiledModule:
    """ """
    def __init__(self, compiled_globals: dict):
        self.compiled_globals = compiled_globals

    def __contains__(self, item):
        return item in self.compiled_globals

    def __getattr__(self, item):
        return self.compiled_globals[item]

    def __getitem__(self, item):
        return self.compiled_globals[item]

    @property
    def is_empty(self) -> bool:
        """ Возвращает True, если в модуле нет кода (только одни комментарии, например) """
        return len(set(self.compiled_globals) - {'__builtins__'}) == 0


class ScriptCompiler:
    """ """

    class CompilerException(Exception):
        """ """

    # Список исключений
    class Misconfigured(CompilerException):
        """ """

    class ForbiddenImport(CompilerException):
        """ Исключение, которое возникает при наличии некорректных импортов в коде """

    class CannotCompile(CompilerException):
        """ Исключение, которое вызывается при невозможности компиляции кода """

    # Перечисление режимов работы компилятора
    MODE_ETL = 1
    MODE_VIRTUAL_OBJECT_SCHEMA = 2
    MODE_ETL_BLOCK = 3

    def __init__(self, mode: Optional[int] = None):
        self.mode = mode

    def compile(self, source_code: str, mode: int = None) -> CompiledModule:
        """ """
        try:
            byte_code = compile(source_code, filename='<string>', mode='exec')
        except SyntaxError as e:
            raise ScriptCompiler.CannotCompile(f'Ошибка компиляции: {e.msg} (line {e.lineno}): {e.text}')

        try:
            compiled_globals = self._get_globals(mode=mode if mode is not None else self.mode)
            exec(byte_code, compiled_globals)
        except Exception as e:
            raise ScriptCompiler.CompilerException(f'Ошибка компиляции: {e}')

        return CompiledModule(compiled_globals=compiled_globals)

    def _get_globals(self, mode: int) -> dict:
        """ """
        if mode == ScriptCompiler.MODE_ETL:
            safe_names, safe_modules = self._safe_globals_for_model_etl_script()
        elif mode == ScriptCompiler.MODE_ETL_BLOCK:
            safe_names, safe_modules = self._safe_globals_for_etl_block()
        elif mode == ScriptCompiler.MODE_VIRTUAL_OBJECT_SCHEMA:
            safe_names, safe_modules = self._safe_globals_for_virtual_object_schema_script()
        else:
            raise ScriptCompiler.Misconfigured(f'Указан некорректный режим компиляции {self.mode}')

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            """ """
            modules = name.split('.')
            if modules[0] not in safe_modules:
                raise ScriptCompiler.ForbiddenImport(f'Импорт модуля {modules[0]} запрещен')

            return __import__(name, globals, locals, fromlist, level)

        safe_builtins = {}
        for name in safe_names:
            safe_builtins[name] = getattr(builtins, name)

        safe_builtins['__import__'] = safe_import

        return {'__builtins__': safe_builtins}

    @staticmethod
    def _safe_globals_for_virtual_object_schema_script() -> Tuple[List[str], List[str]]:
        """ """
        safe_names = [
            'None', 'False', 'True', 'bool', 'bytes', 'chr', 'complex', 'float',
            'hex', 'id', 'int', 'str', 'getattr', 'setattr', 'delattr',
        ]

        safe_modules = ['pyspark', 'aw_etl']

        return safe_names, safe_modules

    @staticmethod
    def _safe_globals_full() -> Tuple[List[str], List[str]]:
        """ Возвращает полный набор разрешенных модулей """
        safe_names = [
            'None', 'False', 'True', 
            'abs', 'all', 'any', 'ascii', 
            'bin', 'bool', 'bytes', 'bytearray', 
            'callable', 'chr', 'classmethod', 'complex', 
            'delattr', 'dict', 'divmod', 
            'enumerate',
            'float', 'filter', 'format', 'frozenset',
            'getattr',
            'hasattr', 'hash', 'hex', 
            'id', 'int', 'isinstance', 'issubclass', 'iter',
            'len', 'list',
            'map', 'max', 'min',
            'next', 
            'object', 'oct', 'ord',
            'pow', 'print', 'property', 
            'range', 'repr', 'reversed', 'round', 
            'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super',
            'type', 'tuple', 
            'vars',
            'zip', 
            '__build_class__', '__name__',
            

            'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BufferError', 'BytesWarning',
            'DeprecationWarning', 'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError', 'FutureWarning',
            'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning', 'IndentationError', 'IndexError', 'KeyError',
            'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError', 'NotImplementedError', 'OSError',
            'OverflowError', 'PendingDeprecationWarning', 'ReferenceError', 'RuntimeError', 'RuntimeWarning',
            'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TypeError',
            'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
            'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError',
        ]

        safe_modules = [
            'pyspark', 'requests', 'pandas', 'numpy', 'aw_etl', 'pyparsing', 'pydantic',

            'mlflow', 'prophet', 'statmodels', 'torch', 'sklearn', 'numpy', 'catboost', 

            'array', 'calendar', 'codecs', 'collections', 'copy', 'csv', 'dataclasses', 'datetime', '_strptime',
            'decimal', 'enum', 'functools', 'hashlib', 'itertools', 'json', 'math', 'queue', 'random', 're',
            'statistics', 'string', 'time', 'urllib', 'xml',
            'zoneinfo', 'typing', 'uuid', 'logging',
        ]

        return safe_names, safe_modules

    @staticmethod
    def _safe_globals_for_model_etl_script() -> Tuple[List[str], List[str]]:
        """ """
        return ScriptCompiler._safe_globals_full()

    @staticmethod
    def  _safe_globals_for_etl_block() -> Tuple[List[str], List[str]]:
        """ """
        safe_names, safe_modules = ScriptCompiler._safe_globals_full()
        safe_modules.extend(['sqlglot', 'inspect'])

        return safe_names, safe_modules
