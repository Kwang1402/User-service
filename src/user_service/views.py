from sqlalchemy.sql import text
from user_service.service_layer import unit_of_work


def fetch_model_from_database(
    identifier: str, table: str, uow: unit_of_work.SqlAlchemyUnitOfWork
):
    with uow:
        sql = text(
            f"""
            SELECT * FROM {table} 
            WHERE id = :identifier OR message_id = :identifier
            """
        )

        result = (
            uow.session.execute(sql, {"identifier": identifier})
            .mappings()
            .one_or_none()
        )

    return dict(result) if result else None
