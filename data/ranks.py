import sqlalchemy
from .db_session import SqlAlchemyBase


class Ranks(SqlAlchemyBase):
    __tablename__ = 'ranks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    rank = sqlalchemy.Column(sqlalchemy.String, nullable=False)
