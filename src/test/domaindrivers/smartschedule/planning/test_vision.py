from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

import pytest
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.demand import Demand
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestVision(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-planning.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    JAN_1: Final[datetime] = datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    JAN_1_2: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_2_5: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_2_12: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-12T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    RESOURCE_1: Final[ResourceId] = ResourceId.new_one()
    RESOURCE_2: Final[ResourceId] = ResourceId.new_one()
    RESOURCE_4: Final[ResourceId] = ResourceId.new_one()

    project_facade: PlanningFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.project_facade = dependency_resolver.resolve_dependency(PlanningFacade)

    @pytest.mark.skip(reason="not implemented yet")
    def test_waterfall_project_process(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("vision")
        # when
        java: Demands = Demands.of(Demand.demand_for(Capability.skill("JAVA")))
        self.project_facade.add_demands(project_id, java)

        # then
        self.verify_possible_risk_during_planning(project_id, java)

        # when
        self.project_facade.define_project_stages(
            project_id,
            Stage.from_name("stage1").with_chosen_resource_capabilities(self.RESOURCE_1),
            Stage.from_name("stage2").with_chosen_resource_capabilities(self.RESOURCE_2, self.RESOURCE_1),
            Stage.from_name("stage3").with_chosen_resource_capabilities(self.RESOURCE_4),
        )

        # then
        project_card: ProjectCard = self.project_facade.load(project_id)
        self.assertTrue(
            all(
                stage in project_card.parallelized_stages.print()
                for stage in [
                    "stage1 | stage2, stage3",
                    "stage2, stage3 | stage1",
                ]
            )
        )

        # when
        self.project_facade.define_project_stages(
            project_id,
            Stage.from_name("stage1").of_duration(timedelta(days=1)).with_chosen_resource_capabilities(self.RESOURCE_1),
            Stage.from_name("stage2")
            .of_duration(timedelta(days=3))
            .with_chosen_resource_capabilities(self.RESOURCE_2, self.RESOURCE_1),
            Stage.from_name("stage3")
            .of_duration(timedelta(days=10))
            .with_chosen_resource_capabilities(self.RESOURCE_4),
        )
        # and
        self.project_facade.define_start_date(project_id, self.JAN_1)

        # then
        schedule: Schedule = self.project_facade.load(project_id).schedule
        has_stage_with_slots = {
            "stage1": self.JAN_1_2,
            "stage2": self.JAN_2_5,
            "stage3": self.JAN_2_12,
        }
        for key, value in has_stage_with_slots.items():
            self.assertTrue(
                schedule.dates.get(key, {}) == value,
            )

    def verify_possible_risk_during_planning(self, project_id: ProjectId, demands: Demands) -> None:
        pass
