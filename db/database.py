from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbal.base import Base
from dbal.country import country_table
from dbal.user import user_table


def init_db():
    engine = create_engine('sqlite:///passport.db')
    Base.metadata.bind = engine
    Base.metadata.create_all(engine,tables=[country_table, user_table])
    return sessionmaker(bind=engine)

session = init_db()