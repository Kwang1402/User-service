from sqlalchemy.sql import text
from user_service.service_layer import unit_of_work


def fetch_models_from_database(
    table: str, condition: str, uow: unit_of_work.SqlAlchemyUnitOfWork
):
    with uow:
        sql = text(
            f"""
            SELECT * FROM {table} 
            WHERE {condition}
            """
        )

        results = uow.session.execute(sql).mappings().all()
    
    return [dict(result) for result in results] if results else []
