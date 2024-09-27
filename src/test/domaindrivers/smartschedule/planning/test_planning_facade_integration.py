from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher


class PlanningFacadeIntegrationTest(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = ("schema-planning.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    project_facade: PlanningFacade
    events_publisher: EventsPublisher

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
