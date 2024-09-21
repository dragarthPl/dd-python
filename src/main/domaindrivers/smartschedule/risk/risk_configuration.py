from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.potential_transfers_service import PotentialTransfersService
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.resource.resource_facade import ResourceFacade
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_dispatcher import RiskPeriodicCheckSagaDispatcher
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_repository import RiskPeriodicCheckSagaRepository
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_repository_sqlalchemy import (
    RiskPeriodicCheckSagaRepositorySqlalchemy,
)
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.risk.verify_critical_resource_available_during_planning import (
    VerifyCriticalResourceAvailableDuringPlanning,
)
from domaindrivers.smartschedule.risk.verify_enough_demands_during_planning import VerifyEnoughDemandsDuringPlanning
from domaindrivers.smartschedule.risk.verify_needed_resources_available_in_time_slot import (
    VerifyNeededResourcesAvailableInTimeSlot,
)
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade
from domaindrivers.utils.events_publisher_in_memory import EventBus
from injector import Module, provider, singleton


class RiskConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            cast(Type[RiskPeriodicCheckSagaRepository], RiskPeriodicCheckSagaRepository),
            to=RiskPeriodicCheckSagaRepositorySqlalchemy,
        )

    @singleton
    @provider
    def risk_saga_dispatcher(
        self,
        state_repository: RiskPeriodicCheckSagaRepository,
        potential_transfers_service: PotentialTransfersService,
        capability_finder: CapabilityFinder,
        risk_push_notification: RiskPushNotification,
        event_bus: EventBus,
    ) -> RiskPeriodicCheckSagaDispatcher:
        risk_periodic_check_saga_dispatcher = RiskPeriodicCheckSagaDispatcher(
            state_repository, potential_transfers_service, capability_finder, risk_push_notification
        )
        event_bus.subscribe(
            risk_periodic_check_saga_dispatcher.handle,
            "CapabilitiesAllocated",
            "CapabilityReleased",
            "EarningsRecalculated",
            "ProjectAllocationScheduled",
            "ProjectAllocationsDemandsScheduled",
            "ResourceTakenOver",
        )
        return risk_periodic_check_saga_dispatcher

    @singleton
    @provider
    def risk_push_notification(self, event_bus: EventBus) -> RiskPushNotification:
        risk_push_notification = RiskPushNotification()
        return risk_push_notification

    @singleton
    @provider
    def verify_enough_demands_during_planning(
        self,
        planning_facade: PlanningFacade,
        resource_facade: ResourceFacade,
        risk_push_notification: RiskPushNotification,
        event_bus: EventBus,
    ) -> VerifyEnoughDemandsDuringPlanning:
        verify_enough_demands_during_planning = VerifyEnoughDemandsDuringPlanning(
            planning_facade, SimulationFacade(), resource_facade, risk_push_notification
        )
        event_bus.subscribe(
            verify_enough_demands_during_planning.handle,
            "CapabilitiesDemanded",
        )
        return verify_enough_demands_during_planning

    @singleton
    @provider
    def verify_critical_resource_available_during_planning(
        self,
        availability_facade: AvailabilityFacade,
        risk_push_notification: RiskPushNotification,
        event_bus: EventBus,
    ) -> VerifyCriticalResourceAvailableDuringPlanning:
        verify_critical_resource_available_during_planning = VerifyCriticalResourceAvailableDuringPlanning(
            availability_facade, risk_push_notification
        )
        event_bus.subscribe(
            verify_critical_resource_available_during_planning.handle,
            "CriticalStagePlanned",
        )
        return verify_critical_resource_available_during_planning

    @singleton
    @provider
    def verify_needed_resources_available_in_time_slot(
        self,
        availability_facade: AvailabilityFacade,
        risk_push_notification: RiskPushNotification,
        event_bus: EventBus,
    ) -> VerifyNeededResourcesAvailableInTimeSlot:
        verify_needed_resources_available_in_time_slot = VerifyNeededResourcesAvailableInTimeSlot(
            availability_facade, risk_push_notification
        )
        event_bus.subscribe(
            verify_needed_resources_available_in_time_slot.handle,
            "NeededResourcesChosen",
        )
        return verify_needed_resources_available_in_time_slot
