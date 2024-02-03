from user_service.adapters import repository
from user_service.service_layer import unit_of_work
from user_service import bootstrap
import pytest


class FakeRepository(repository.AbstractRepository):
    def __init__(self, users):
        super.__init__()
        self._users = set(users)

    def _add(self, user):
        self._models.add(user)

    def _get(self, id):
        return (next(u for u in self._users if u.id == id), None)

    def _get_by_email(self, email):
        return (next(u for u in self._users if u.email == email), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.users = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass
