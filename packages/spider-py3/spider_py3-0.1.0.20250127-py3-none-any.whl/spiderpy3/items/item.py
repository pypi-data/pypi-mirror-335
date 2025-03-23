from abc import ABCMeta
from copy import deepcopy
from pprint import pformat
from typing_extensions import Self
from typing import Dict, Any, Iterator, List
from collections.abc import MutableMapping

from spiderpy3.items.field import Field
from spiderpy3.exceptions import ItemInitError, ItemAttributeError
from spiderpy3.mixins.model import ModelMixin


class ItemMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        fields = {}
        if (m := attrs.get("_MODEL")) is not None:
            for column in m.columns():
                fields[column] = Field()
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        cls = super().__new__(mcs, name, bases, attrs)
        cls._FIELDS = fields
        return cls


class Item(MutableMapping, metaclass=ItemMeta):
    _FIELDS: Dict[str, Field]
    _MODEL: ModelMixin

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._item = {}

        if args:
            raise ItemInitError(
                f"{self.__class__.__name__} 对象实例化。"
                f"不支持位置参数，请使用关键字参数传参！"
            )
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    # MutableMapping
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._FIELDS:
            self._item[key] = value
        else:
            raise KeyError(
                f"{self.__class__.__name__} 字段值赋值。"
                f"不支持赋值该字段值 {key}，请添加该字段到类定义中！"
            )

    # MutableMapping
    def __delitem__(self, key: str) -> None:
        del self._item[key]

    # Mapping
    def __getitem__(self, key: str) -> Any:
        return self._item[key]

    # Collection
    def __len__(self) -> int:
        return len(self._item)

    # Iterable
    def __iter__(self) -> Iterator[str]:
        return iter(self._item)

    def __repr__(self) -> str:
        return pformat(dict(self))

    __str__ = __repr__

    def to_dict(self) -> Dict[str, Any]:
        return dict(self)

    def copy(self) -> Self:
        return deepcopy(self)

    @property
    def unassigned_fields(self) -> List[str]:
        return [k for k in self._FIELDS.keys() if k not in self._item.keys()]

    # 补充限制属性操作
    def __setattr__(self, name: str, value: Any) -> None:
        valid_names = ["_FIELDS", "_MODEL", "_item"]
        if name not in valid_names:
            raise AttributeError(
                f"{self.__class__.__name__} 属性值设置。"
                f"不支持设置该属性值 {name}。如果是赋值该字段值，请使用 item[{name!r}] = {value!r}！"
            )
        super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> Any:
        fields = super().__getattribute__("_FIELDS")
        if name in fields:
            raise ItemAttributeError(
                f"{self.__class__.__name__} 属性值获取。"
                f"不支持获取该属性值 {name}，请使用 item[{name!r}] 来获取字段值！"
            )
        return super().__getattribute__(name)

    # 当 __getattribute__ 要抛出 AttributeError 异常的时候，__getattr__ 就不能空实现，因为该方法会拦截该异常
    def __getattr__(self, name: str) -> None:
        raise AttributeError(
            f"{self.__class__.__name__} 属性值获取。"
            f"不支持获取该属性值 {name}，如果是获取该字段值，请添加该字段值到类定义中，然后使用 item[{name!r}] 来获取字段值！"
        )
