import abc
from user_service.domains import models


class AbstractRepository(abc.ABC):
    def __init__(self) -> None:
        self.seen = set()

    def add(self, model: models.User):
        self._add(model)
        self.seen.add(model)

    def get(self, id) -> models.User:
        user = self._get(id)
        if user:
            self.seen.add(user)
        return user

    def get_by_email(self, email) -> models.User:
        user = self._get_by_email(email)
        if user:
            self.seen.add(user)
        return user

    @abc.abstractmethod
    def _add(self, user: models.User):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> models.User:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_email(self, email) -> models.User:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, user):
        self.session.add(user)

    def _get(self, id):
        return self.session.query(models.User).filter_by(id=id).one_or_none()

    def _get_by_email(self, email):
        return self.session.query(models.User).filter_by(email=email).one_or_none()
