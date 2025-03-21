from typing import Optional, Any, List, Union

import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ETLBlockParamType(str, Enum):
    """ """
    STRING = 'string'
    TEXT = 'text'
    PASSWORD = 'password'
    SQL_TEXT = 'sql_text'
    NUMBER = 'number'
    FLOAT = 'float'
    BOOL = 'bool'
    DATE = 'date'
    DATETIME = 'datetime'
    SELECT = 'select'
    ACTION = 'action'


class ETLBlockParamGroupType(str, Enum):
    """ """
    GROUP = 'group'


class ETLBlockParamActionType(str, Enum):
    """ """
    ACTION = 'action'


# ----------------------------------------------------------------------------------------------------------------------
# Метаданные ETL блока
# ----------------------------------------------------------------------------------------------------------------------
class ETLBlockParam(BaseModel):
    """ Параметр ETL блока """
    code: str
    name: str
    type: ETLBlockParamType
    description: Optional[str] = None

    required: bool
    mult: bool
    domain: Optional[Any] = None
    extra: Optional[Any] = None


class ETLBlockParamGroup(BaseModel):
    """ Группа параметров ETL блока """
    code: str
    name: str

    type: ETLBlockParamGroupType
    description: Optional[str] = None
    view_options: Optional[dict] = None
    mult: bool
    params: List[Union['ETLBlockParam', 'ETLBlockParamAction', 'ETLBlockParamAction']] = []
    extra: Optional[Any] = None


class ETLBlockParamAction(BaseModel):
    code: str
    name: str
    type: ETLBlockParamActionType
    description: Optional[str] = None
    action: str
    extra: Optional[Any] = None


class ETLBlockMeta(BaseModel):
    """ Метаданные ETL-блока """
    uid: str  # уникальный идентификатор блока
    name: str  # название блока
    version: str  # версия блока
    description: str  # описание блока
    author: str  # автор блока
    updated_at: datetime.datetime  # дата и время последнего обновления
    params: List[Union[ETLBlockParam, ETLBlockParamAction, ETLBlockParamGroup]]
    engine_requires: Optional[List[str]] = []

    @property
    def verbose_name(self):
        return f'{self.name} v{self.version}'
