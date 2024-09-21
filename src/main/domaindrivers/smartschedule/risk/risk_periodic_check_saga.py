import hashlib
from datetime import datetime

import pytz
from attr import define
from attrs import field
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from domaindrivers.smartschedule.shared.event import Event


@define(slots=False)
class RiskPeriodicCheckSaga:
    _risk_saga_id: RiskPeriodicCheckSagaId = field(factory=RiskPeriodicCheckSagaId.new_one)
    _project_id: ProjectAllocationsId = field(default=None)
    _missing_demands: Demands = field(default=Demands.none())
    _earnings_value: Earnings = field(default=None, alias="earnings")
    _deadline: datetime = field(init=False)
    _version: int = field(init=False)

    @property
    def RISK_THRESHOLD_VALUE(self) -> Earnings:
        return Earnings.of(1000)

    @property
    def UPCOMING_DEADLINE_AVAILABILITY_SEARCH(self) -> int:
        return 30

    @property
    def UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION(self) -> int:
        return 15

    def are_demands_satisfied(self) -> bool:
        return False

    def missing_demands(self) -> Demands:
        return self._missing_demands

    def handle(self, event: Event) -> RiskPeriodicCheckSagaStep:
        match event:
            case EarningsRecalculated():
                return None
            case ProjectAllocationsDemandsScheduled():
                return None
            case ProjectAllocationScheduled():
                return None
            case ResourceTakenOver():
                return None
            case CapabilityReleased():
                return None
            case CapabilitiesAllocated():
                return None
            case _:
                raise NotImplementedError()

    def handle_weekly_check(self, when: datetime) -> RiskPeriodicCheckSagaStep:
        return None

    def project_id(self) -> ProjectAllocationsId:
        return self._project_id

    def earnings(self) -> Earnings:
        return self._earnings_value

    def deadline(self) -> datetime:
        if self._deadline:
            return self._deadline.replace(tzinfo=pytz.UTC)
        return self._deadline

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self._risk_saga_id).encode("utf-8"))
        m.update(str(self._project_id).encode("utf-8"))
        m.update(str(self._earnings_value).encode("utf-8"))
        m.update(str(self._deadline).encode("utf-8"))

        return int(m.hexdigest(), 16)
