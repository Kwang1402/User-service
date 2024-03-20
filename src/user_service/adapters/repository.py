import abc
from typing import Type
from user_service.domains import models


class AbstractRepository(abc.ABC):
    def __init__(self) -> None:
        self.seen = set()

    def add(self, model: Type[models.BaseModel]):
        self._add(model)
        self.seen.add(model)

    def get(self, model: Type[models.BaseModel], *args, **kwargs,) -> Type[models.BaseModel]:
        model = self._get(model,*args,**kwargs)
        if model:
            self.seen.add(model)
        return model

    @abc.abstractmethod
    def _add(self, model: Type[models.BaseModel], *args, **kwargs,):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, model: Type[models.BaseModel], *args, **kwargs,) -> Type[models.BaseModel]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, model: Type[models.BaseModel]):
        self.session.add(model)

    def _get(self, model: Type[models.BaseModel], *args, **kwargs,) -> Type[models.BaseModel]:
        return self.session.query(model).filter_by(**kwargs).one_or_none()
