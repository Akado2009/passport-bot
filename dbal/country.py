from dbal.base import Base
from sqlalchemy import Column, String, Integer, Table


country_table = Table(
    'country',
    Base.metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', String(50), unique=True, nullable=False),
    Column('url_name', String(50), unique=True, nullable=False)
)