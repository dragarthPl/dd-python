import os
from pathlib import Path
from unittest import TestCase

import sqlalchemy
from attr import frozen
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

CURRENT_DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_PATH = os.path.join(CURRENT_DIR_PATH.parent.parent.parent.parent, "main", "resources")


@frozen
class DataSource:
    connection_url: str
    container_host_ip: str
    exposed_port: str
    database_username: str
    database_password: str
    database_name: str


class TestDbConfiguration:
    __test__ = False
    __scripts: dict[str, str]
    __postgres_sqlcontainer: PostgresContainer

    def __init__(self, scripts: tuple[str, ...] = None):
        self.__scripts = {}
        self.__postgres_sqlcontainer = PostgresContainer("postgres:16")
        self.__postgres_sqlcontainer.start()
        if scripts:
            self.__load_scripts(scripts)
            self.__execute_scripts(scripts)

    @property
    def postgres_sqlcontainer(self) -> PostgresContainer:
        return self.__postgres_sqlcontainer

    def data_source(self) -> DataSource:
        return DataSource(
            connection_url=self.__postgres_sqlcontainer.get_connection_url(),
            container_host_ip=self.__postgres_sqlcontainer.get_container_host_ip(),
            exposed_port=self.__postgres_sqlcontainer.get_exposed_port(5432),
            database_username=self.__postgres_sqlcontainer.username,
            database_password=self.__postgres_sqlcontainer.password,
            database_name=self.__postgres_sqlcontainer.dbname,
        )

    def __load_scripts(self, scripts: tuple[str, ...]) -> None:
        for script in scripts:
            script_full_path = Path(os.path.join(RESOURCES_PATH, script))
            if not script_full_path.exists():
                raise FileNotFoundError(f"Script {script_full_path} not found")

            with script_full_path.open() as f:
                self.__scripts[str(script)] = f.read()

    def __execute_scripts(self, scripts: tuple[str, ...]) -> None:
        for script in scripts:
            engine = sqlalchemy.create_engine(self.data_source().connection_url)
            with engine.begin() as connection:
                connection.execute(text(self.__scripts[script]))


class TestPostgresSqlContainer(TestCase):
    def test_postgre_sql_container(self) -> None:
        test_db_configuration = TestDbConfiguration(scripts=("schema-planning.sql",))
        try:
            data_source: DataSource = test_db_configuration.data_source()
            self.assertTrue(data_source.connection_url.startswith("postgresql+psycopg2://"))
            engine = sqlalchemy.create_engine(data_source.connection_url)
            with engine.begin() as connection:
                (version,) = connection.execute(sqlalchemy.text("SELECT version()")).fetchone()
                self.assertTrue(version.startswith("PostgreSQL 16"))
        finally:
            test_db_configuration.postgres_sqlcontainer.stop()
