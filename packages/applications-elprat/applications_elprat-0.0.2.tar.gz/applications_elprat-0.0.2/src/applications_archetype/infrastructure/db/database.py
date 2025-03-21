"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from sqlalchemy import event

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from nomenclators_archetype.infrastructure.db.commons import Base


class Database:
    """ Clase para gestionar la base de datos """

    def __init__(self, db_url: str) -> None:
        connect_args = {}
        if "sqlite" in db_url:
            connect_args["check_same_thread"] = False  # Solo para SQLite
        self._engine = create_engine(
            db_url, echo=True, connect_args=connect_args)

        if "sqlite" in db_url:
            event.listen(self._engine, "connect", self.enable_foreign_keys)

        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    @staticmethod
    def enable_foreign_keys(dbapi_connection, connection_record):  # pylint: disable=redefined-outer-name,unused-argument
        """Enable foreign keys (only for SQLite)"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def create_database(self) -> None:
        """ Crea la base de datos """
        Base.metadata.create_all(self._engine)  # pylint: disable=no-member

    def new_session(self) -> Session:
        """ Crea una nueva sesión """
        return self._session_factory()
