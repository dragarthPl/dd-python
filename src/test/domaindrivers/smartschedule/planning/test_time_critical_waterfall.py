from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestTimeCriticalWaterfall(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-risk.sql",
        "schema-planning.sql",
        "schema-availability.sql",
        "schema-resources.sql",
        "schema-allocations.sql",
    )
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    JAN_1_5: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_1_3: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )
    JAN_1_4: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").astimezone(pytz.UTC),
    )

    project_facade: PlanningFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.project_facade = dependency_resolver.resolve_dependency(PlanningFacade)

    def test_time_critical_waterfall_project_process(self) -> None:
        # given
        project_id: ProjectId = self.project_facade.add_new_project_with_stages("waterfall")

        # and
        stage_before_critical: Stage = Stage.from_name("stage1").of_duration(timedelta(days=2))

        critical_stage: Stage = Stage.from_name("stage2").of_duration(self.JAN_1_5.duration())
        stage_after_critical: Stage = Stage.from_name("stage3").of_duration(timedelta(days=3))
        self.project_facade.define_project_stages(
            project_id, stage_before_critical, critical_stage, stage_after_critical
        )

        # when
        self.project_facade.plan_critical_stage(project_id, critical_stage, self.JAN_1_5)

        # then
        schedule: Schedule = self.project_facade.load(project_id).schedule
        has_stage_with_slots = {
            "stage1": self.JAN_1_3,
            "stage2": self.JAN_1_5,
            "stage3": self.JAN_1_4,
        }
        for key, value in has_stage_with_slots.items():
            self.assertTrue(
                schedule.dates.get(key, {}) == value,
            )
