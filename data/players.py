import sqlalchemy
from .db_session import SqlAlchemyBase


class Player(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False, unique=True)
    money = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cities_guessed = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    rank = sqlalchemy.Column(sqlalchemy.String, nullable=False)
