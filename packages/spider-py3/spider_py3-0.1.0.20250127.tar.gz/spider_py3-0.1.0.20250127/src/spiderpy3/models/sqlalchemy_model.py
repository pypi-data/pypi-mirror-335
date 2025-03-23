import re
import json
import hashlib
from abc import ABCMeta
from decimal import Decimal
from datetime import datetime
from typing_extensions import Self
from typing import Dict, List, Any, Optional
from sqlalchemy import Engine
from sqlalchemy.types import Text, TypeDecorator
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, JSON
from sqlalchemy.exc import NoResultFound

from spiderpy3.mixins.model import ModelMixin

Base = declarative_base()


class MediumText(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(Text(length=16777215))  # MEDIUMTEXT：最大长度 16 MB（16777215 字节）
        return super().load_dialect_impl(dialect)


class LongText(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(Text(length=4294967295))  # LONGTEXT：最大长度 4 GB（4294967295 字节）
        return super().load_dialect_impl(dialect)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class SqlalchemyModelMeta(type(Base), ABCMeta):
    def __new__(cls, name, bases, attrs):
        if attrs.get("__abstract__") is True:
            return super().__new__(cls, name, bases, attrs)

        tablename = attrs.get("__tablename__")
        if not (isinstance(tablename, str) and tablename):
            raise ValueError(f"{name}.__tablename__ 非法赋值！")

        engine = attrs.get("__engine__")
        if not isinstance(engine, Engine):
            raise ValueError(f"{name}.__engine__ 非法赋值！")

        data_columns = attrs.get("__data_columns__")
        if not (isinstance(data_columns, list) and all(map(lambda _: isinstance(_, str), data_columns))):
            raise ValueError(f"{name}.__data_columns__ 非法赋值！")

        session = attrs.get("__session__")
        if session is None:
            session = sessionmaker(bind=engine)()
            attrs["__session__"] = session
        else:
            if not isinstance(session, Session):
                raise ValueError(f"{name}.__session__ 非法赋值！")

        return super().__new__(cls, name, bases, attrs)


class SqlalchemyModel(Base, ModelMixin, metaclass=SqlalchemyModelMeta):
    __abstract__ = True

    __tablename__: str
    __engine__: Engine
    __data_columns__: List[str]
    __session__: Session

    id = Column(Integer, comment='ID', primary_key=True, autoincrement=True)
    data_id = Column(String(32), comment='数据ID', nullable=False, unique=True)
    data_columns = Column(JSON, comment='数据字段', nullable=False)
    data_status = Column(SmallInteger, comment='数据状态', default=1, index=True)
    data_create_time = Column(DateTime, comment='数据创建时间', default=datetime.now)
    data_update_time = Column(DateTime, comment='数据更新时间', default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, data_id={self.data_id})>"

    def to_row(self) -> Dict[str, Any]:
        row = json.loads(json.dumps(
            {column.name: getattr(self, column.name) for column in self.__table__.columns},
            ensure_ascii=False,
            cls=JSONEncoder
        ))
        return row

    @classmethod
    def gen_data_id(cls, data: Dict[str, Any]) -> str:
        data_columns = cls.__data_columns__
        data_columns_value_strs = []
        for data_column in data_columns:
            if data_column in data:
                data_column_value_str = str(data[data_column])
                data_columns_value_strs.append(data_column_value_str)
            else:
                raise ValueError(f"data 必须提供 {data_column} 字段！")
        data_id = hashlib.md5("".join(data_columns_value_strs).encode()).hexdigest()
        return data_id

    @classmethod
    def get_data_id(cls, data: Dict[str, Any]) -> str:
        if "data_id" in data:
            if isinstance(data["data_id"], str) and re.match(r"^[0-9a-f]{32}$", data["data_id"]) is not None:
                return data["data_id"]
        return cls.gen_data_id(data)

    @classmethod
    def get_ins_by_data_id(cls, data: Dict[str, Any]) -> Optional[Self]:
        session = cls.__session__
        data_id = cls.get_data_id(data)
        try:
            ins: Self = session.query(cls).filter_by(data_id=data_id).one()
        except NoResultFound:
            return
        return ins

    @classmethod
    def get_row_by_data_id(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ins = cls.get_ins_by_data_id(data)
        if ins is None:
            return
        data = ins.to_row()
        return data

    @classmethod
    def save(cls, data: Dict[str, Any]) -> bool:
        session = cls.__session__

        ins = cls.get_ins_by_data_id(data)
        update = False if ins is None else True

        if not update:
            # 插入
            ins = cls(
                data_id=cls.get_data_id(data),  # noqa
                data_columns=cls.__data_columns__,  # noqa
                **data  # noqa
            )
            session.add(ins)
        else:
            # 更新
            if ins is None:
                ins = cls.get_ins_by_data_id(data)
            for k, v in data.items():
                setattr(ins, k, v)

        session.commit()

        return update

    @classmethod
    def create_table(cls) -> None:
        Base.metadata.create_all(cls.__engine__)

    @classmethod
    def columns(cls) -> List[str]:
        return [c.name for c in cls.__table__.columns]
