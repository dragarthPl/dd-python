from datetime import datetime
from functools import reduce
from typing import Final

import pytz
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from domaindrivers.smartschedule.allocation.potential_transfers_service import PotentialTransfersService
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_repository import RiskPeriodicCheckSagaRepository
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.published_event import PublishedEvent


class RiskPeriodicCheckSagaDispatcher:
    __risk_saga_repository: Final[RiskPeriodicCheckSagaRepository]
    __potential_transfers_service: Final[PotentialTransfersService]
    __capability_finder: Final[CapabilityFinder]
    __risk_push_notification: Final[RiskPushNotification]

    def __init__(
        self,
        state_repository: RiskPeriodicCheckSagaRepository,
        potential_transfers_service: PotentialTransfersService,
        capability_finder: CapabilityFinder,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self.__risk_saga_repository = state_repository
        self.__potential_transfers_service = potential_transfers_service
        self.__capability_finder = capability_finder
        self.__risk_push_notification = risk_push_notification

    def handle(self, event: PublishedEvent) -> None:
        match event:
            case EarningsRecalculated():
                self.handle_EarningsRecalculated(event)
            case ProjectAllocationScheduled():
                self.handle_ProjectAllocationScheduled(event)
            case NotSatisfiedDemands():
                self.handle_NotSatisfiedDemands(event)
            case ResourceTakenOver():
                self.handle_ResourceTakenOver(event)

    # @EventListener
    # remember about transactions spanning saga and potential external system
    def handle_EarningsRecalculated(self, event: EarningsRecalculated) -> None:
        found: RiskPeriodicCheckSaga = self.__risk_saga_repository.find_by_project_id(event.project_id)
        if not found:
            found = RiskPeriodicCheckSaga(project_id=event.project_id, earnings=event.earnings)
        next_step: RiskPeriodicCheckSagaStep = found.handle(event)
        self.__risk_saga_repository.save(found)
        self.__perform(next_step, found)

    # @EventListener
    # remember about transactions spanning saga and potential external system
    def handle_ProjectAllocationScheduled(self, event: ProjectAllocationScheduled) -> None:
        found: RiskPeriodicCheckSaga = self.__risk_saga_repository.find_by_project_id_or_create(event.project_id)
        next_step: RiskPeriodicCheckSagaStep = found.handle(event)
        self.__risk_saga_repository.save(found)
        self.__perform(next_step, found)

    # @EventListener
    # remember about transactions spanning saga and potential external system
    def handle_NotSatisfiedDemands(self, event: NotSatisfiedDemands) -> None:
        sagas: list[RiskPeriodicCheckSaga] = self.__risk_saga_repository.find_by_project_id_in_or_else_create(
            list(event.missing_demands.keys())
        )
        next_steps: dict[RiskPeriodicCheckSaga, RiskPeriodicCheckSagaStep] = {}
        for saga in sagas:
            missing_demands: Demands = event.missing_demands.get(saga.project_id())
            next_step: RiskPeriodicCheckSagaStep = saga.missing_demands(missing_demands)
            next_steps[saga] = next_step
        self.__risk_saga_repository.save_all(sagas)
        for saga, next_step in next_steps.items():
            self.__perform(next_step, saga)

    # @EventListener
    # remember about transactions spanning saga and potential external system
    def handle_ResourceTakenOver(self, event: ResourceTakenOver) -> None:
        interested: list[ProjectAllocationsId] = list(
            map(lambda owner: ProjectAllocationsId(owner.id()), event.previous_owners)
        )
        # transaction per one saga
        for saga in self.__risk_saga_repository.find_by_project_id_in(interested):
            self.handle_saga(saga, event)

    def handle_saga(self, saga: RiskPeriodicCheckSaga, event: ResourceTakenOver) -> None:
        next_step: RiskPeriodicCheckSagaStep = saga.handle(event)
        self.__risk_saga_repository.save(saga)
        self.__perform(next_step, saga)

    # @Scheduled(cron = "@weekly")
    def handle_weekly_check(self) -> None:
        sagas: list[RiskPeriodicCheckSaga] = self.__risk_saga_repository.find_all()
        for saga in sagas:
            next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(datetime.now(pytz.UTC))
            self.__risk_saga_repository.save(saga)
            self.__perform(next_step, saga)

    def __perform(self, next_step: RiskPeriodicCheckSagaStep, saga: RiskPeriodicCheckSaga) -> None:
        match next_step:
            case RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED:
                self.__risk_push_notification.notify_demands_satisfied(saga.project_id())
            case RiskPeriodicCheckSagaStep.FIND_AVAILABLE:
                self.__handle_find_available_for(saga)
            case RiskPeriodicCheckSagaStep.DO_NOTHING:
                pass
            case RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT:
                self.__handle_simulate_relocation(saga)
            case RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK:
                self.__risk_push_notification.notify_about_possible_risk(saga.project_id())

    def __handle_find_available_for(self, saga: RiskPeriodicCheckSaga) -> None:
        replacements: dict[Demand, AllocatableCapabilitiesSummary] = self.__find_available_replacements_for(
            saga.get_missing_demands()
        )
        if any(reduce(lambda x, y: x + y, (ac.all for ac in replacements.values()))):  # type: ignore
            self.__risk_push_notification.notify_about_availability(saga.project_id(), replacements)

    def __handle_simulate_relocation(self, saga: RiskPeriodicCheckSaga) -> None:
        for demand, replacements in self.__find_possible_replacements(saga.get_missing_demands()).items():
            for replacement in replacements.all:
                profit_after_moving_capabilities: float = (
                    self.__potential_transfers_service.profit_after_moving_capabilities(
                        saga.project_id(), replacement, replacement.time_slot
                    )
                )
                if profit_after_moving_capabilities > 0:
                    self.__risk_push_notification.notify_profitable_relocation_found(
                        saga.project_id(), replacement.allocatable_capability_id
                    )

    def __find_available_replacements_for(self, demands: Demands) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self.__capability_finder.find_available_capabilities(demand.capability, demand.slot)
            for demand in demands.all
        }

    def __find_possible_replacements(self, demands: Demands) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self.__capability_finder.find_capabilities(demand.capability, demand.slot) for demand in demands.all
        }
