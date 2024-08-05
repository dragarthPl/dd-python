import uuid
from datetime import datetime, timedelta
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class TestAllocationsToProject(TestCase):
    WHEN: Final[datetime] = datetime.min
    PROJECT_ID: Final[ProjectAllocationsId] = ProjectAllocationsId.new_one()
    ADMIN_ID: Final[ResourceId] = ResourceId.new_one()
    FEB_1: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2020, 2, 1)
    FEB_2: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2020, 2, 2)
    JANUARY: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2020, 1, 1)

    def test_can_allocate(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)

        # when
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        # then
        self.assertTrue(event.is_present())
        capabilities_allocated: CapabilitiesAllocated = event.get()
        self.assertEqual(
            event.get(),
            CapabilitiesAllocated(
                capabilities_allocated.event_id,
                capabilities_allocated.allocated_capability_id,
                self.PROJECT_ID,
                Demands.none(),
                self.WHEN,
            ),
        )

    def test_cant_allocate_when_requested_time_slot_not_withing_project_slot(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations(
            self.PROJECT_ID, Allocations.none(), Demands.none(), self.JANUARY
        )

        # when
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        # then
        self.assertFalse(event.is_present())

    def test_allocating_has_no_effect_when_capability_already_allocated(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)

        # and
        allocations.allocate(self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN)

        # when
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        # then
        self.assertFalse(event.is_present())

    def test_there_are_no_missing_demands_when_all_allocated(self) -> None:
        # given
        demands: Demands = Demands.of(
            Demand(Capability.permission("ADMIN"), self.FEB_1), Demand(Capability.skill("JAVA"), self.FEB_1)
        )
        # and
        allocations: ProjectAllocations = ProjectAllocations.with_demands(self.PROJECT_ID, demands)
        # and
        allocations.allocate(self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN)
        # when
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.skill("JAVA"), self.FEB_1, self.WHEN
        )
        # then
        self.assertTrue(event.is_present())
        capabilities_allocated: CapabilitiesAllocated = event.get()
        self.assertEqual(
            event.get(),
            CapabilitiesAllocated(
                capabilities_allocated.event_id,
                capabilities_allocated.allocated_capability_id,
                self.PROJECT_ID,
                Demands.none(),
                self.WHEN,
            ),
        )

    def test_missing_demands_are_present_when_allocating_for_different_than_demanded_slot(self) -> None:
        # given
        demands: Demands = Demands.of(
            Demand(Capability.permission("ADMIN"), self.FEB_1), Demand(Capability.skill("JAVA"), self.FEB_1)
        )
        # and
        allocations: ProjectAllocations = ProjectAllocations.with_demands(self.PROJECT_ID, demands)
        # and
        allocations.allocate(self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN)
        # when
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.skill("JAVA"), self.FEB_2, self.WHEN
        )
        # then
        self.assertTrue(event.is_present())
        self.assertEqual(allocations.missing_demands(), Demands.of(Demand(Capability.skill("JAVA"), self.FEB_1)))
        capabilities_allocated: CapabilitiesAllocated = event.get()
        self.assertEqual(
            event.get(),
            CapabilitiesAllocated(
                capabilities_allocated.event_id,
                capabilities_allocated.allocated_capability_id,
                self.PROJECT_ID,
                Demands.of(Demand(Capability.skill("JAVA"), self.FEB_1)),
                self.WHEN,
            ),
        )

    def test_can_release(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)
        # and
        allocated_admin: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )
        # when
        event: Optional[CapabilityReleased] = allocations.release(
            allocated_admin.get().allocated_capability_id, self.FEB_1, self.WHEN
        )

        # then
        self.assertTrue(event.is_present())
        self.assertEqual(
            event.get(), CapabilityReleased(event.get().event_id, self.PROJECT_ID, Demands.none(), self.WHEN)
        )

    def test_releasing_has_no_effect_when_capability_was_not_allocated(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)

        # when
        event: Optional[CapabilityReleased] = allocations.release(uuid.uuid4(), self.FEB_1, self.WHEN)

        # then
        self.assertFalse(event.is_present())

    def test_missing_demands_are_present_after_releasing_some_of_allocated_capabilities(self) -> None:
        # given
        demand_for_java: Demand = Demand(Capability.skill("JAVA"), self.FEB_1)
        demand_for_admin: Demand = Demand(Capability.permission("ADMIN"), self.FEB_1)
        allocations: ProjectAllocations = ProjectAllocations.with_demands(
            self.PROJECT_ID, Demands.of(demand_for_admin, demand_for_java)
        )
        # and
        allocated_admin: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )
        allocations.allocate(self.ADMIN_ID, Capability.skill("JAVA"), self.FEB_1, self.WHEN)
        # when
        event: Optional[CapabilityReleased] = allocations.release(
            allocated_admin.get().allocated_capability_id, self.FEB_1, self.WHEN
        )

        # then
        self.assertTrue(event.is_present())
        self.assertEqual(
            event.get(),
            CapabilityReleased(event.get().event_id, self.PROJECT_ID, Demands.of(demand_for_admin), self.WHEN),
        )

    def test_releasing_has_no_effect_when_releasing_slot_not_within_allocated_slot(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)
        # and
        allocated_admin: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        # when
        event: Optional[CapabilityReleased] = allocations.release(
            allocated_admin.get().allocated_capability_id, self.FEB_2, self.WHEN
        )

        # then
        self.assertFalse(event.is_present())

    def test_releasing_small_part_of_slot_leaves_the_rest(self) -> None:
        # given
        allocations: ProjectAllocations = ProjectAllocations.empty(self.PROJECT_ID)
        # and
        allocated_admin: Optional[CapabilitiesAllocated] = allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        # when
        fifteen_minutes_in_1_feb: TimeSlot = TimeSlot(
            self.FEB_1.since + timedelta(hours=1), self.FEB_1.since + timedelta(hours=2)
        )
        one_hour_before: TimeSlot = TimeSlot(self.FEB_1.since, self.FEB_1.since + timedelta(hours=1))
        the_rest: TimeSlot = TimeSlot(self.FEB_1.since + timedelta(hours=2), self.FEB_1.to)

        # when
        event: Optional[CapabilityReleased] = allocations.release(
            allocated_admin.get().allocated_capability_id, fifteen_minutes_in_1_feb, self.WHEN
        )

        # then
        self.assertEqual(
            event.get(), CapabilityReleased(event.get().event_id, self.PROJECT_ID, Demands.none(), self.WHEN)
        )
        self.assertTrue(
            AllocatedCapability.of(self.ADMIN_ID.id(), Capability.permission("ADMIN"), one_hour_before)
            in allocations.allocations().all
        )
        self.assertTrue(
            AllocatedCapability.of(self.ADMIN_ID.id(), Capability.permission("ADMIN"), the_rest)
            in allocations.allocations().all
        )
