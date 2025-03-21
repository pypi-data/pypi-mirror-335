from typing import Optional, List, Dict

from pydantic import BaseModel, ConfigDict


class ModelObjectField(BaseModel):
    """ """
    name: str
    model_name: str
    simple_type: str

    model_config = ConfigDict(
        protected_namespaces=()
    )


class ModelObject(BaseModel):
    """ """
    name: str
    model_name: str
    type: str
    sql_text: Optional[str] = None
    fields: List[ModelObjectField] = []

    childs: List['ModelObject'] = []

    model_config = ConfigDict(
        protected_namespaces=()
    )


class ModelSql(BaseModel):
    """
    """
    sql: str
    xsqls: Dict[str, str] = {}


class ModelSchema(BaseModel):
    """ """
    objects: List[ModelObject] = []
    sql: ModelSql
