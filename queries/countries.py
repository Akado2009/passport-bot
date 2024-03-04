from db.database import session
from sqlalchemy import select, distinct
from dbal.country import country_table
from typing import (
    Dict
)


def get_countries_names() -> Dict:
    result = []
    with session() as sess:
        result = sess.execute(
            select(
                distinct(country_table.c.name),
                country_table.c.url_name
            )
        ).all()

    return {
        c[0]: c[1] for c in result
    }

