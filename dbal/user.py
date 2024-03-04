from dbal.base import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
)


user_table = Table(
    'user',
    Base.metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('user_id', Integer),
    Column('country', String(50), ForeignKey("country.name"), nullable=False),
    Column('country_url', String(50), ForeignKey("country.url_name"), nullable=False),
    Column('number', String(50), nullable=True),
    Column('code', String(50), nullable=True),
    Column('ems', String(50), nullable=True)
)
