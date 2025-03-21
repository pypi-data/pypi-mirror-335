from typing import List, TypedDict, Optional

from dataclasses import dataclass, field


class ModelObjectSchemaField(TypedDict):
    """ """
    model_name: str
    simple_type: str


@dataclass
class ModelObjectTestData:
    """ """
    model_name: str
    rows: List[dict] = field(default_factory=list)
    schema: Optional[List[ModelObjectSchemaField]] = None
