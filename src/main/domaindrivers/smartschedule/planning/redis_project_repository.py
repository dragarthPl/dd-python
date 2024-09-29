from typing import Any, Awaitable, cast

import jsonpickle
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.utils.optional import Optional
from injector import inject
from redis import Redis


class RedisProjectRepository(ProjectRepository):
    __redis: Redis

    @inject
    def __init__(self, redis: Redis) -> None:
        self.__redis = redis

    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        value: Awaitable[str | None] | str = self.__redis.hget("projects", str(project_id.id()))
        if value is None:
            return Optional.empty()
        return Optional.of(jsonpickle.decode(value))

    def save(self, project: Project) -> Project:
        self.__redis.hset("projects", str(project.id.id()), jsonpickle.encode(project))
        return project

    def find_all_by_id_in(self, project_id: set[ProjectId]) -> list[Project]:
        ids: list[Any] = list(set(map(lambda p: str(p.id()), project_id)))
        projects: list[str] = cast(list[str], self.__redis.hmget("projects", *ids))
        return list(jsonpickle.decode(value) for value in projects)

    def find_all(self) -> list[Project]:
        projects: list[str] = cast(list[str], self.__redis.hvals("projects"))
        return list(jsonpickle.decode(value) for value in projects)
