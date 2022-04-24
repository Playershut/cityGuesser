import sqlalchemy
from .db_session import SqlAlchemyBase


class Roles(SqlAlchemyBase):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    role_id = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=False)
    guild_id = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=False)
