from typing import Type, List, Dict, Any

from user_service.domains import models
from user_service.service_layer import unit_of_work


def fetch_models_from_database(
    model_type: Type[models.BaseModel],
    uow: unit_of_work.SqlAlchemyUnitOfWork,
    *args,
    **kwargs
) -> List[Dict[str, Any]]:
    with uow:
        results = uow.repo.get(model_type=model_type, *args, **kwargs)
        return [result.json for result in results] if results else []
