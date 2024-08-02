from typing import Any, cast

import injector
import jsonpickle
from sqlalchemy import Connection, create_engine, Engine, QueuePool
from sqlalchemy.orm import Session, sessionmaker


class DatabaseModule(injector.Module):
    __engine: Engine
    __database_uri: str
    __session_factory: sessionmaker[Session]

    def __init__(self, database_uri: str) -> None:
        self.__database_uri = database_uri

    @staticmethod
    def __custom_sqlalchemy_serialize(obj: Any) -> str:
        return cast(str, jsonpickle.encode(obj))

    @staticmethod
    def __custom_sqlalchemy_deserialize(data: str) -> Any:
        return jsonpickle.decode(data)

    def configure(self, _binder: injector.Binder) -> None:
        self.__engine: Engine = create_engine(
            self.__database_uri,
            json_serializer=self.__custom_sqlalchemy_serialize,
            json_deserializer=self.__custom_sqlalchemy_deserialize,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
        )

        self.__session_factory = sessionmaker(bind=self.__engine)

    @injector.singleton
    @injector.provider
    def engine(self) -> Engine:
        return self.__engine

    @injector.threadlocal
    @injector.provider
    def session(self) -> Session:
        return self.__session_factory()

    @injector.threadlocal
    @injector.provider
    def connection(self, current_session: Session) -> Connection:
        return current_session.connection()
