from db.database import session
from sqlalchemy import (
    select,
    distinct,
    insert,
    update,
    delete,
)
from typing import (
    Any,
    List,
    Optional,
    Dict
)
from dbal.user import user_table


def check_if_exists(id: int, country: str) -> Optional[int]:
    with session() as sess:
        stmt = select(user_table.c.id).where(
            user_table.c.user_id == id,
            user_table.c.country == country
        )
        return sess.execute(stmt).one_or_none()


def create_user(data: Dict) -> None:
    with session() as sess:
        create_stmt = insert(user_table).values(data)
        sess.execute(create_stmt)
        sess.commit()


def update_user_value(id: int, column: str, value: Any) -> None:
    with session() as sess:
        update_stmt = update(user_table).values({
            column: value,
        }).where(
            user_table.c.user_id == id
        )
        sess.execute(update_stmt)
        sess.commit()


def select_ids_for_country(country: str) -> List[int]:
    with session() as sess:
        return sess.execute(
            select(
                distinct(user_table.c.id)
            ).where(
                user_table.c.country == country
            )
        ).scalars().all()


def get_user_subscriptions(user_id: int) -> List[Any]:
    with session() as sess:
        return sess.execute(
            select(
                user_table
            ).where(
                user_table.c.user_id == user_id
            )
        ).all()


def delete_user_subscription(user_id: int, country: str) -> None:
    with session() as sess:
        delete_stmt = delete(
            user_table
        ).where(
            user_table.c.user_id == user_id,
            user_table.c.country == country
        )
        sess.execute(delete_stmt)
        sess.commit()
    

def get_distinct_subs_for_checker() -> List[Any]:
    with session() as sess:
        return sess.execute(
            select(
                distinct(user_table.c.country_url),
                user_table.c.number,
                user_table.c.code,
                user_table.c.ems,
            ).where(
                user_table.c.number != None,
                user_table.c.code != None,
                user_table.c.ems != None
            )
        ).all()


def get_domain_subscriptions(c_url: str) -> List[Any]:
    with session() as sess:
        return sess.execute(
            select(
                user_table
            ).where(
                user_table.c.country_url == c_url
            )
        ).all()
