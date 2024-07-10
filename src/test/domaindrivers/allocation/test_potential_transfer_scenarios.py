import uuid
from decimal import Decimal
from typing import Final
from unittest import TestCase
from uuid import UUID

from dateutil.relativedelta import relativedelta
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project import Project
from domaindrivers.smartschedule.allocation.projects import Projects
from domaindrivers.smartschedule.optimization.optimization_facade import OptimizationFacade
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade


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

    BANKING_SOFT_ID: Final[UUID] = uuid.uuid4()
    INSURANCE_SOFT_ID: Final[UUID] = uuid.uuid4()
    STASZEK_JAVA_MID: Final[AllocatedCapability] = AllocatedCapability(
        uuid.uuid4(), Capability.skill("JAVA-MID"), JAN_1
    )

    simulation_facade: AllocationFacade = AllocationFacade(SimulationFacade(OptimizationFacade()))

    def test_simulates_moving_capabilities_to_different_project(self) -> None:
        # given
        banking_soft: Project = Project(self.DEMAND_FOR_JAVA_MID_IN_JAN, Decimal(9))
        insurance_soft: Project = Project(self.DEMAND_FOR_JAVA_MID_IN_JAN, Decimal(90))
        projects: Projects = Projects({self.BANKING_SOFT_ID: banking_soft, self.INSURANCE_SOFT_ID: insurance_soft})
        # and
        banking_soft.add(self.STASZEK_JAVA_MID)

        # when
        result: float = self.simulation_facade.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.JAN_1
        )

        # then
        self.assertEqual(Decimal(81), result)

    def test_simulates_moving_capabilities_to_different_project_just_for_awhile(self) -> None:
        # given
        banking_soft: Project = Project(self.DEMAND_FOR_JAVA_MID_IN_JAN, Decimal(9))
        insurance_soft: Project = Project(self.DEMAND_FOR_JAVA_JUST_FOR_15MIN_IN_JAN, Decimal(99))
        projects: Projects = Projects({self.BANKING_SOFT_ID: banking_soft, self.INSURANCE_SOFT_ID: insurance_soft})
        # and
        banking_soft.add(self.STASZEK_JAVA_MID)

        # when
        result: float = self.simulation_facade.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.FIFTEEN_MINUTES_IN_JAN
        )

        # then
        self.assertEqual(Decimal(90), result)

    def test_the_move_gives_zero_profit_when_there_are_still_missing_demands(self) -> None:
        # given
        banking_soft: Project = Project(self.DEMAND_FOR_JAVA_MID_IN_JAN, Decimal(9))
        insurance_soft: Project = Project(self.DEMANDS_FOR_JAVA_AND_PYTHON_IN_JAN, Decimal(99))
        projects: Projects = Projects({self.BANKING_SOFT_ID: banking_soft, self.INSURANCE_SOFT_ID: insurance_soft})
        # and
        banking_soft.add(self.STASZEK_JAVA_MID)

        # when
        result: float = self.simulation_facade.check_potential_transfer(
            projects, self.BANKING_SOFT_ID, self.INSURANCE_SOFT_ID, self.STASZEK_JAVA_MID, self.JAN_1
        )

        # then
        self.assertEqual(Decimal(-9), result)
