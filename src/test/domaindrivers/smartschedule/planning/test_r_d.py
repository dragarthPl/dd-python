from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

import pytest
from domaindrivers.smartschedule.allocation.resource_id import ResourceId
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.resource_name import ResourceName
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestRD(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-planning.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    JANUARY: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-31T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    FEBRUARY: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    MARCH: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-03-31T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    Q1: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-03-31T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_4: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    FEB_2_16: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-02-16T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    MAR_1_6: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-03-06T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )

    project_facade: PlanningFacade
    availability_facade: AvailabilityFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.project_facade = dependency_resolver.resolve_dependency(PlanningFacade)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)

    @pytest.mark.skip(reason="not implemented yet")
    def test_research_and_development_project_process(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("waterfall")
        # and

        r1: ResourceName = ResourceName("r1")
        java_available_in_january: ResourceId = self.resource_available_for_capability_in_period(
            r1, Capability.skill("JAVA"), self.JANUARY
        )
        r2: ResourceName = ResourceName("r2")
        php_available_in_february: ResourceId = self.resource_available_for_capability_in_period(
            r2, Capability.skill("PHP"), self.FEBRUARY
        )
        r3: ResourceName = ResourceName("r3")
        csharp_available_in_march: ResourceId = self.resource_available_for_capability_in_period(
            r3, Capability.skill("CSHARP"), self.MARCH
        )
        all_resources: set[ResourceName] = {r1, r2, r3}

        # when
        self.project_facade.define_resources_within_dates(project_id, all_resources, self.JANUARY)

        # then
        self.verify_that_resources_are_missing(project_id, {php_available_in_february, csharp_available_in_march})

        # when
        self.project_facade.define_resources_within_dates(project_id, all_resources, self.FEBRUARY)

        # then
        self.verify_that_resources_are_missing(project_id, {java_available_in_january, csharp_available_in_march})

        # when
        self.project_facade.define_resources_within_dates(project_id, all_resources, self.Q1)

        # then
        self.verify_that_no_resources_are_missing(project_id)

        # when
        self.project_facade.adjust_stages_to_resource_availability(
            project_id,
            self.Q1,
            Stage.from_name("Stage1").of_duration(timedelta(days=3)).with_chosen_resource_capabilities(r1),
            Stage.from_name("Stage2").of_duration(timedelta(days=15)).with_chosen_resource_capabilities(r2),
            Stage.from_name("Stage3").of_duration(timedelta(days=5)).with_chosen_resource_capabilities(r3),
        )

        # then
        loaded: ProjectCard = self.project_facade.load(project_id)
        schedule: Schedule = self.project_facade.load(project_id).schedule
        has_stage_with_slots = {
            "Stage1": self.JAN_1_4,
            "Stage2": self.FEB_2_16,
            "Stage3": self.MAR_1_6,
        }
        for key, value in has_stage_with_slots.items():
            self.assertTrue(
                schedule.dates.get(key, {}) == value,
            )
        self.project_is_not_parallelized(loaded)

    def resource_available_for_capability_in_period(
        self, resource: ResourceName, capability: Capability, slot: TimeSlot
    ) -> ResourceId:
        # todo
        return ResourceId.new_one()

    def project_is_not_parallelized(self, loaded: ProjectCard) -> None:
        self.assertEqual(loaded.parallelized_stages, ParallelStagesList.empty())

    def verify_that_no_resources_are_missing(self, project_id: ProjectId) -> None:
        pass

    def verify_that_resources_are_missing(self, project_id: ProjectId, missing_resources: set[ResourceId]) -> None:
        pass
