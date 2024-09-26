from datetime import datetime
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.publish_missing_demands_service import CreateHourlyDemandsSummaryService
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestCreateHourlyDemandsSummaryService(TestCase):
    NOW: datetime = datetime.now(pytz.UTC)
    JAN: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
    CSHARP: Demands = Demands.of(Demand(Capability.skill("CSHARP"), JAN))
    JAVA: Demands = Demands.of(Demand(Capability.skill("JAVA"), JAN))

    service: CreateHourlyDemandsSummaryService = CreateHourlyDemandsSummaryService()

    def test_creates_missing_demands_summary_for_all_given_projects(self) -> None:
        # given
        csharp_project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java_project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        csharp_project: ProjectAllocations = ProjectAllocations(csharp_project_id, Allocations.none(), self.CSHARP)
        java_project: ProjectAllocations = ProjectAllocations(java_project_id, Allocations.none(), self.JAVA)

        # when
        result: NotSatisfiedDemands = self.service.create([csharp_project, java_project], self.NOW)

        # then
        self.assertEqual(self.NOW, result.occurred_at())
        expected_missing_demands: dict[ProjectAllocationsId, Demands] = {
            java_project_id: self.JAVA,
            csharp_project_id: self.CSHARP,
        }
        self.assertEqual(result.missing_demands, expected_missing_demands)
