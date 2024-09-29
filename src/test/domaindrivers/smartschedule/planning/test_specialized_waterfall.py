from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestSpecializedWaterfall(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-risk.sql",
        "schema-availability.sql",
        "schema-resources.sql",
        "schema-allocations.sql",
    )
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    JAN_1_2: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_1_4: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_1_5: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_1_6: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-06T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_4_8: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-08T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )

    project_facade: PlanningFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.project_facade = dependency_resolver.resolve_dependency(PlanningFacade)

    def test_specialized_waterfall_project_process(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("waterfall")
        # and
        critical_stage_duration: timedelta = timedelta(days=5)
        stage_1_duration: timedelta = timedelta(days=1)
        stage_before_critical: Stage = Stage.from_name("stage1").of_duration(stage_1_duration)
        critical_stage: Stage = Stage.from_name("stage2").of_duration(critical_stage_duration)
        stage_after_critical: Stage = Stage.from_name("stage3").of_duration(timedelta(days=3))
        self.project_facade.define_project_stages(
            project_id, stage_before_critical, critical_stage, stage_after_critical
        )

        # and
        critical_resource_name: ResourceId = ResourceId.new_one()
        critical_capability_availability: ResourceId = self.resource_available_for_capability_in_period(
            critical_resource_name, Capability.skill("JAVA"), self.JAN_1_6
        )

        # when
        self.project_facade.plan_critical_stage_with_resource(
            project_id, critical_stage, critical_resource_name, self.JAN_4_8
        )

        # then
        self.verify_resources_not_available(project_id, critical_capability_availability, self.JAN_4_8)

        # when
        self.project_facade.plan_critical_stage_with_resource(
            project_id, critical_stage, critical_resource_name, self.JAN_1_6
        )

        # then
        self.assert_resources_available(project_id, critical_capability_availability)
        # and
        schedule: Schedule = self.project_facade.load(project_id).schedule
        has_stage_with_slots = {
            "stage1": self.JAN_1_2,
            "stage2": self.JAN_1_6,
            "stage3": self.JAN_1_4,
        }
        for key, value in has_stage_with_slots.items():
            self.assertTrue(
                schedule.dates.get(key, {}) == value,
            )

    def assert_resources_available(self, project_id: ProjectId, resource: ResourceId) -> None:
        pass

    def verify_resources_not_available(
        self, project_id: ProjectId, resource: ResourceId, requested_but_not_available: TimeSlot
    ) -> None:
        pass

    def resource_available_for_capability_in_period(
        self, resource: ResourceId, capability: Capability, slot: TimeSlot
    ) -> ResourceId:
        return None
