from decimal import Decimal
from typing import Final
from unittest import TestCase

from dateutil.relativedelta import relativedelta
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.potential_transfers import PotentialTransfers
from domaindrivers.smartschedule.allocation.potential_transfers_service import PotentialTransfersService
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.optimization.optimization_facade import OptimizationFacade
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade


class Project:
    project_allocations_id: ProjectAllocationsId
    earnings: Earnings
    demands: Demands
    allocations: Allocations

    def __init__(self, project_allocations_id: ProjectAllocationsId, demands: Demands, earnings: Earnings):
        self.project_allocations_id = project_allocations_id
        self.demands = demands
        self.earnings = earnings
        self.allocations = Allocations.none()

    def add(self, allocated_capability: AllocatedCapability) -> Allocations:
        self.allocations = self.allocations.add(allocated_capability)
        return self.allocations


class TestPotentialTransferScenarios(TestCase):
    JAN_1: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    FIFTEEN_MINUTES_IN_JAN: Final[TimeSlot] = TimeSlot(JAN_1.since, JAN_1.since + relativedelta(minutes=15))
    DEMAND_FOR_JAVA_JUST_FOR_15MIN_IN_JAN: Final[Demands] = Demands(
        [(Demand(Capability.skill("JAVA-MID"), FIFTEEN_MINUTES_IN_JAN))]
    )
    DEMAND_FOR_JAVA_MID_IN_JAN: Final[Demands] = Demands([(Demand(Capability.skill("JAVA-MID"), JAN_1))])
    DEMANDS_FOR_JAVA_AND_PYTHON_IN_JAN: Final[Demands] = Demands(
        [Demand(Capability.skill("JAVA-MID"), JAN_1), Demand(Capability.skill("PYTHON-MID"), JAN_1)]
    )

    BANKING_SOFT_ID: Final[ProjectAllocationsId] = ProjectAllocationsId.new_one()
    INSURANCE_SOFT_ID: Final[ProjectAllocationsId] = ProjectAllocationsId.new_one()
    STASZEK_JAVA_MID: Final[AllocatedCapability] = AllocatedCapability(
        AllocatableCapabilityId.new_one(), CapabilitySelector.can_just_perform(Capability.skill("JAVA-MID")), JAN_1
    )

    potential_transfers: PotentialTransfersService = PotentialTransfersService(SimulationFacade(OptimizationFacade()))

    def test_simulates_moving_capabilities_to_different_project(self) -> None:
        # given
        banking_soft: Project = Project(self.BANKING_SOFT_ID, self.DEMAND_FOR_JAVA_MID_IN_JAN, Earnings.of(9))
        insurance_soft: Project = Project(self.INSURANCE_SOFT_ID, self.DEMAND_FOR_JAVA_MID_IN_JAN, Earnings.of(90))

        banking_soft.add(self.STASZEK_JAVA_MID)
        projects: PotentialTransfers = self.to_potential_transfers(banking_soft, insurance_soft)

        # when
        result: float = self.potential_transfers.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.JAN_1
        )

        # then
        self.assertEqual(Decimal(81), result)

    def test_simulates_moving_capabilities_to_different_project_just_for_awhile(self) -> None:
        # given
        banking_soft: Project = Project(self.BANKING_SOFT_ID, self.DEMAND_FOR_JAVA_MID_IN_JAN, Earnings.of(9))
        insurance_soft: Project = Project(
            self.INSURANCE_SOFT_ID, self.DEMAND_FOR_JAVA_JUST_FOR_15MIN_IN_JAN, Earnings.of(99)
        )

        banking_soft.add(self.STASZEK_JAVA_MID)
        projects: PotentialTransfers = self.to_potential_transfers(banking_soft, insurance_soft)

        # when
        result: float = self.potential_transfers.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.FIFTEEN_MINUTES_IN_JAN
        )

        # then
        self.assertEqual(Decimal(90), result)

    def test_the_move_gives_zero_profit_when_there_are_still_missing_demands(self) -> None:
        # given
        banking_soft: Project = Project(self.BANKING_SOFT_ID, self.DEMAND_FOR_JAVA_MID_IN_JAN, Earnings.of(9))
        insurance_soft: Project = Project(
            self.INSURANCE_SOFT_ID, self.DEMANDS_FOR_JAVA_AND_PYTHON_IN_JAN, Earnings.of(99)
        )

        banking_soft.add(self.STASZEK_JAVA_MID)
        projects: PotentialTransfers = self.to_potential_transfers(banking_soft, insurance_soft)

        # when
        result: float = self.potential_transfers.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.JAN_1
        )

        # then
        self.assertEqual(Decimal(-9), result)

    def to_potential_transfers(self, *projects: Project) -> PotentialTransfers:
        allocations: dict[ProjectAllocationsId, Allocations] = {}
        demands: dict[ProjectAllocationsId, Demands] = {}
        earnings: dict[ProjectAllocationsId, Earnings] = {}
        for project in projects:
            allocations[project.project_allocations_id] = project.allocations
            demands[project.project_allocations_id] = project.demands
            earnings[project.project_allocations_id] = project.earnings
        return PotentialTransfers(ProjectsAllocationsSummary({}, allocations, demands), earnings)
