from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.ump.metadata import datafile


def commit_session(session):
    if session is not None:
        session.commit()
        session.close()


class DB:
    def __init__(self):
        self.database = "sqlite3"  # default database

    def _create_db_engine(self, database):
        if self.database == "sqlite3":
            factory = SqlLiteFactory()
            engine = factory.create_database()
            return engine

    def get_db_session(self):
        engine = self._create_db_engine(self.database)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def get_connect(self):
        engine = self._create_db_engine(self.database)
        conn = engine.connect()
        return conn

    def get_db_engine(self):
        engine = self._create_db_engine(self.database)
        return engine


class SqlLiteFactory:
    def create_database(self):
        engine = create_engine("sqlite:///" + datafile, echo=False)
        return engine
