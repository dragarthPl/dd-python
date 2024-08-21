from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.demand import Demand
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestPlanningFacade(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = ("schema-planning.sql", "schema-availability.sql")
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    project_facade: PlanningFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.project_facade = dependency_resolver.resolve_dependency(PlanningFacade)

    def test_can_create_project_and_load_project_card(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))

        # when
        loaded: ProjectCard = self.project_facade.load(project_id)

        # then
        self.assertEqual(project_id, loaded.project_id)
        self.assertEqual("project", loaded.name)
        self.assertEqual("Stage1", loaded.parallelized_stages.print())

    def test_can_load_multiple_projects(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))
        project_id_2: ProjectId = self.project_facade.add_new_project_with_stages("project2", Stage.from_name("Stage2"))

        # when
        loaded: list[ProjectCard] = self.project_facade.load_all({project_id, project_id_2})

        # then
        projects = list(map(lambda x: x.project_id, loaded))
        self.assertTrue(all((project_id in projects, project_id_2 in projects)))

    def test_can_create_and_save_more_complex_parallelization(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")
        stage3: Stage = Stage.from_name("Stage3")
        stage2 = stage2.depends_on(stage1)
        stage3 = stage3.depends_on(stage2)

        # and
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", stage1, stage2, stage3)

        # when
        loaded: ProjectCard = self.project_facade.load(project_id)

        # then
        self.assertEqual("Stage1 | Stage2 | Stage3", loaded.parallelized_stages.print())

    def test_can_plan_demands(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))

        # when
        demand_for_java: Demands = Demands.of(Demand.demand_for(Capability.skill("JAVA")))
        self.project_facade.add_demands(project_id, demand_for_java)

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        self.assertEqual(demand_for_java, loaded.demands)

    def test_can_plan_new_demands(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))

        # when
        java: Demand = Demand.demand_for(Capability.skill("JAVA"))
        csharp: Demand = Demand.demand_for(Capability.skill("C#"))
        self.project_facade.add_demands(project_id, Demands.of(java))
        self.project_facade.add_demands(project_id, Demands.of(csharp))

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        self.assertEqual(Demands.of(java, csharp), loaded.demands)

    def test_can_plan_demands_per_stage(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))

        # when
        java: Demands = Demands.of(Demand.demand_for(Capability.skill("JAVA")))
        demands_per_stage: DemandsPerStage = DemandsPerStage({"Stage1": java})
        self.project_facade.define_demands_per_stage(project_id, demands_per_stage)

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        self.assertEqual(demands_per_stage, loaded.demands_per_stage)
        self.assertEqual(java, loaded.demands)

    def test_can_plan_needed_resources_in_time(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project")

        # when
        needed_resources: set[ResourceId] = {
            ResourceId.new_one(),
        }
        first_half_of_the_year: TimeSlot = TimeSlot(
            datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2021-06-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        self.project_facade.define_resources_within_dates(project_id, needed_resources, first_half_of_the_year)

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        self.assertEqual(ChosenResources(needed_resources, first_half_of_the_year), loaded.needed_resources)

    def test_can_redefine_stages(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", Stage.from_name("Stage1"))

        # when
        self.project_facade.define_project_stages(project_id, Stage.from_name("Stage2"))

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        self.assertEqual("Stage2", loaded.parallelized_stages.print())

    def test_can_calculate_schedule_after_passing_possible_start(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1").of_duration(timedelta(days=2))
        stage2: Stage = Stage.from_name("Stage2").of_duration(timedelta(days=5))
        stage3: Stage = Stage.from_name("Stage3").of_duration(timedelta(days=7))

        # and
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", stage1, stage2, stage3)

        # when
        self.project_facade.define_start_date(
            project_id, datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        )

        # then
        expected_schedule: dict[str, TimeSlot] = {
            "Stage1": TimeSlot(
                datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
            "Stage2": TimeSlot(
                datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-06T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
            "Stage3": TimeSlot(
                datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-08T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
        }
        loaded: ProjectCard = self.project_facade.load(project_id)
        for key, value in expected_schedule.items():
            self.assertTrue(
                loaded.schedule.dates.get(key, {}) == value,
            )
        # assertThat(loaded.schedule().dates()).containsExactlyInAnyOrderEntriesOf(expectedSchedule);

    def test_can_manually_add_schedule(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1").of_duration(timedelta(days=2))
        stage2: Stage = Stage.from_name("Stage2").of_duration(timedelta(days=5))
        stage3: Stage = Stage.from_name("Stage3").of_duration(timedelta(days=7))
        # and
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("project", stage1, stage2, stage3)

        # when
        dates: dict[str, TimeSlot] = {
            "Stage1": TimeSlot(
                datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
            "Stage2": TimeSlot(
                datetime.strptime("2021-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-08T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
            "Stage3": TimeSlot(
                datetime.strptime("2021-01-08T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                datetime.strptime("2021-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            ),
        }
        self.project_facade.define_manual_schedule(project_id, Schedule(dates))

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        for key, value in dates.items():
            self.assertTrue(
                loaded.schedule.dates.get(key, {}) == value,
            )
        # assertThat(loaded.schedule().dates()).containsExactlyInAnyOrderEntriesOf(dates);
