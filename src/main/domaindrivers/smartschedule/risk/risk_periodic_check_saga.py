import hashlib
from datetime import datetime

import pytz
from attr import define
from attrs import field
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from domaindrivers.smartschedule.shared.published_event import PublishedEvent


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
        return not self._missing_demands.all

    def missing_demands(self, missing_demands: Demands) -> RiskPeriodicCheckSagaStep:
        self._missing_demands = missing_demands
        if self.are_demands_satisfied():
            return RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    def get_missing_demands(self) -> Demands:
        return self._missing_demands

    def handle(self, event: PublishedEvent) -> RiskPeriodicCheckSagaStep:
        match event:
            case ProjectAllocationScheduled():
                self._deadline = event.from_to.to
                return RiskPeriodicCheckSagaStep.DO_NOTHING
            case EarningsRecalculated():
                self._earnings_value = event.earnings
                return RiskPeriodicCheckSagaStep.DO_NOTHING
            case ResourceTakenOver():
                if event.occurred_at() > self.deadline():
                    return RiskPeriodicCheckSagaStep.DO_NOTHING
                return RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK
            case _:
                raise NotImplementedError()

    def handle_weekly_check(self, when: datetime) -> RiskPeriodicCheckSagaStep:
        if not self.deadline() or when > self.deadline():
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        if self.are_demands_satisfied():
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        days_to_deadline: int = (self.deadline() - when).days
        if days_to_deadline > self.UPCOMING_DEADLINE_AVAILABILITY_SEARCH:
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        if days_to_deadline > self.UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION:
            return RiskPeriodicCheckSagaStep.FIND_AVAILABLE
        if self.earnings() > self.RISK_THRESHOLD_VALUE:
            return RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT
        return RiskPeriodicCheckSagaStep.DO_NOTHING

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
