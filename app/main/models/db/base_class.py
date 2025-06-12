from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    __abstract__ = True

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def as_dict(self, attr=None):
        if attr is not None:
            resp = {}
            for c in self.__table__.columns:
                if c.name not in attr:
                    resp.update({c.name: getattr(self, c.name)})
            return resp
        else:
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def add_key(self, key, val):
        data = self.as_dict()
        data.update({
            key: val
        })
        return data

    def append_key(self, json, excl=None):
        data = self.as_dict()
        data.update(json)
        if excl is not None:
            for e in excl:
                del data[e]
        return data
