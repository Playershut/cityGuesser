import sqlalchemy
from .db_session import SqlAlchemyBase


class Settings(SqlAlchemyBase):
    __tablename__ = 'settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    game_in_progress = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    chosen_city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
