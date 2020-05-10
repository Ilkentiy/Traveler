import sqlalchemy
from sqlalchemy import orm
import datetime
from .db_session import SqlAlchemyBase

class Travel(SqlAlchemyBase):
    __tablename__ = 'travel'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    headline = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    img_1 = sqlalchemy.Column(sqlalchemy.BLOB)
    img_2 = sqlalchemy.Column(sqlalchemy.BLOB)
    img_3 = sqlalchemy.Column(sqlalchemy.BLOB)
    date = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)

    route = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

