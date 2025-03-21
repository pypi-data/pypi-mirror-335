from typing import List, Dict, Union, Optional, Any


class NamedObjectsBundle:
    """ """
    def __init__(self, objs: Dict[str, Any]):
        self._obj_list: List[Any] = [df for _, df in objs.items()]
        self._obj_named: Dict[str, Any] = objs

    def first(self) -> Optional[Any]:
        """ """
        return self._obj_list[0] if self._obj_list else None
    
    def as_list(self) -> List[Any]:
        return self._obj_list
    
    def as_named(self) -> Dict[str, Any]:
        return self._obj_named
    
    def __getitem__(self, item):
        if isinstance(item, int):
            # если item указано целым числом, то возвращаем по индексу
            return self._obj_list[item]
        
        if not item in self._obj_named:
            raise Exception(f'Данные объекта с именем "{item}" не найдена')
        return self._obj_named[item]
    
    def __iter__(self):
        return iter(self._obj_named.values())

    def __bool__(self):
        return len(self._obj_list) > 0
    
    def __len__(self):
        return len(self._obj_list)
    
    def items(self):
        return self._obj_named.items()
