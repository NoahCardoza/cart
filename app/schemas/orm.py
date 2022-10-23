from typing import Any

from pydantic import BaseModel
from pydantic.utils import GetterDict
from sqlalchemy.orm.base import instance_dict


class ORMNoLazyLoaderGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        try:
            return instance_dict(self._obj)[key]
        except KeyError:
            return default


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True
        getter_dict = ORMNoLazyLoaderGetter
