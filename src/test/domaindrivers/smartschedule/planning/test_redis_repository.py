from datetime import datetime
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import cast, Final, Type
from unittest import TestCase

import injector
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.demand import Demand
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional
from redis import Redis
from testcontainers.redis import RedisContainer


class TestRedisRepository(TestCase):
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=tuple())

    JAN_10_20: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    NEEDED_RESOURCES: Final[ChosenResources] = ChosenResources({ResourceId.new_one()}, JAN_10_20)
    SCHEDULE: Final[Schedule] = Schedule({"Stage1": JAN_10_20})
    DEMAND_FOR_JAVA: Final[Demands] = Demands([Demand(Capability.skill("JAVA"))])
    DEMANDS_PER_STAGE: Final[DemandsPerStage] = DemandsPerStage.empty()
    STAGES: Final[ParallelStagesList] = ParallelStagesList.of(ParallelStages({Stage.from_name("Stage1")}))

    redis_project_repository: ProjectRepository

    def setUp(self) -> None:
        redis_container = RedisContainer("redis:5.0.3-alpine")
        redis_container.start()
        redis = redis_container.get_client()

        def configure(binder: injector.Binder) -> None:
            binder.bind(Redis, to=redis, scope=injector.singleton)

        dependency_resolver = DependencyResolverForTest(
            self.test_db_configuration.data_source().connection_url,
            additional_configure=configure,
        )
        self.redis_project_repository = dependency_resolver.resolve_dependency(
            cast(Type[ProjectRepository], ProjectRepository)
        )

    def test_can_save_and_load_project(self) -> None:
        # given
        project: Project = Project("project", self.STAGES)
        # and
        project.add_schedule_direct(self.SCHEDULE)
        # and
        project.add_demands(self.DEMAND_FOR_JAVA)
        # and
        project.add_chosen_resources(self.NEEDED_RESOURCES)
        # and
        project.add_demands_per_stage(self.DEMANDS_PER_STAGE)
        # and
        project = self.redis_project_repository.save(project)

        # when
        loaded: Optional[Project] = self.redis_project_repository.find_by_id(project.id)

        # then
        self.assertTrue(loaded.is_present())
        self.assertEqual(self.NEEDED_RESOURCES, loaded.get().get_chosen_resources())
        self.assertEqual(self.STAGES, loaded.get().get_parallelized_stages())
        self.assertEqual(self.SCHEDULE, loaded.get().get_schedule())
        self.assertEqual(self.DEMAND_FOR_JAVA, loaded.get().get_all_demands())
        self.assertEqual(self.DEMANDS_PER_STAGE, loaded.get().get_demands_per_stage())

    def test_can_load_multiple_projects(self) -> None:
        # given
        project: Project = Project("project", self.STAGES)
        project2: Project = Project("project2", self.STAGES)

        # and
        project = self.redis_project_repository.save(project)
        project2 = self.redis_project_repository.save(project2)

        # when
        loaded: list[Project] = self.redis_project_repository.find_all_by_id_in({project.id, project2.id})

        # then
        self.assertEqual(2, len(loaded))
        ids: set[ProjectId] = set(map(lambda project: project.id, loaded))
        self.assertCountEqual({project2.id, project.id}, ids)

    def test_can_load_all_projects(self) -> None:
        # given
        project: Project = Project("project", self.STAGES)
        project2: Project = Project("project2", self.STAGES)

        # and
        project = self.redis_project_repository.save(project)
        project2 = self.redis_project_repository.save(project2)

        # when
        loaded: list[Project] = self.redis_project_repository.find_all()

        # then
        self.assertEqual(2, len(loaded))
        ids: set[ProjectId] = set(map(lambda project: project.id, loaded))
        self.assertCountEqual({project2.id, project.id}, ids)
