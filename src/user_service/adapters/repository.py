import abc
from typing import Type, List

from user_service.domains import models


class AbstractRepository(abc.ABC):
    def __init__(self) -> None:
        self.seen = set()

    def add(self, model: models.BaseModel):
        self._add(model)
        self.seen.add(model)

    def remove(self, model: models.BaseModel):
        self._remove(model)

    def get(
        self,
        model_type: Type[models.BaseModel],
        *args,
        **kwargs,
    ) -> List[models.BaseModel]:
        # print("something")
        results = self._get(model_type, *args, **kwargs)
        # print(results)
        if results:
            for result in results:
                self.seen.add(result)
        return results

    @abc.abstractmethod
    def _add(
        self,
        model: models.BaseModel,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(
        self,
        model: models.BaseModel,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(
        self,
        model_type: Type[models.BaseModel],
        *args,
        **kwargs,
    ) -> List[models.BaseModel]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, model: models.BaseModel):
        self.session.add(model)

    def _remove(self, model: models.BaseModel):
        self.session.delete(model)

    def _get(
        self,
        model_type: Type[models.BaseModel],
        *args,
        **kwargs,
    ) -> List[models.BaseModel]:
        return self.session.query(model_type).filter_by(**kwargs).all()
