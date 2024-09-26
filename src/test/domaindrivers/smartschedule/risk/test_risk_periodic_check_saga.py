from datetime import datetime, timedelta
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestRiskPeriodicCheckSaga(TestCase):
    JAVA: Capability = Capability.skill("JAVA")
    ONE_DAY: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2022, 1, 1)
    SINGLE_DEMAND: Demands = Demands.of(Demand(JAVA, ONE_DAY))
    MANY_DEMANDS: Demands = Demands.of(Demand(JAVA, ONE_DAY), Demand(JAVA, ONE_DAY))
    PROJECT_DATES: TimeSlot = TimeSlot(
        datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC),
        datetime.strptime("2021-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC),
    )
    PROJECT_ID: ProjectAllocationsId = ProjectAllocationsId.new_one()
    CAPABILITY_ID: AllocatableCapabilityId = AllocatableCapabilityId.new_one()

    def test_updates_initial_demands_on_saga_creation(self) -> None:
        # when
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )

        # then
        self.assertEqual(self.SINGLE_DEMAND, saga.get_missing_demands())

    def test_updates_deadline_on_deadline_set(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # then
        self.assertEqual(self.PROJECT_DATES.to, saga.deadline())

    def test_update_missing_demands(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )

        # when
        next_step: RiskPeriodicCheckSagaStep = saga.missing_demands(self.MANY_DEMANDS)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)
        self.assertEqual(self.MANY_DEMANDS, saga.get_missing_demands())

    def test_no_new_steps_on_when_missing_demands(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )

        # when
        next_step: RiskPeriodicCheckSagaStep = saga.missing_demands(self.MANY_DEMANDS)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_updated_earnings_on_earnings_recalculated(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )

        # when
        next_step: RiskPeriodicCheckSagaStep = saga.handle(
            EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC))
        )
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

        # then
        self.assertEqual(Earnings.of(1000), saga.earnings())

        # when
        next_step = saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(900), datetime.now(pytz.UTC)))

        # then
        self.assertEqual(Earnings.of(900), saga.earnings())
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_informs_about_demands_satisfied_when_no_missing_demands(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC)))
        # when
        still_missing: RiskPeriodicCheckSagaStep = saga.missing_demands(self.SINGLE_DEMAND)
        zero_demands: RiskPeriodicCheckSagaStep = saga.missing_demands(Demands.none())

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, still_missing)
        self.assertEqual(RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED, zero_demands)

    def test_do_nothing_on_resource_taken_over_when_after_deadline(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        after_deadline: datetime = self.PROJECT_DATES.to + timedelta(hours=100)
        next_step: RiskPeriodicCheckSagaStep = saga.handle(
            ResourceTakenOver.of(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {
                    Owner.of(self.PROJECT_ID.id()),
                },
                self.ONE_DAY,
                after_deadline,
            )
        )

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_notify_about_risk_on_resource_taken_over_when_before_deadline(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        before_deadline: datetime = self.PROJECT_DATES.to - timedelta(hours=100)
        next_step: RiskPeriodicCheckSagaStep = saga.handle(
            ResourceTakenOver.of(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {Owner.of(self.PROJECT_ID.id())},
                self.ONE_DAY,
                before_deadline,
            )
        )

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK, next_step)

    def test_no_next_step_on_capability_released(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )

        # when
        next_step: RiskPeriodicCheckSagaStep = saga.missing_demands(self.SINGLE_DEMAND)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_weekly_check_should_result_in_nothing_when_all_demands_satisfied(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC)))
        # and
        saga.missing_demands(Demands.none())
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        way_before_deadline: datetime = self.PROJECT_DATES.to - timedelta(days=1)
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(way_before_deadline)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_weekly_check_should_result_in_nothing_when_after_deadline(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC)))
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        way_after_deadline: datetime = self.PROJECT_DATES.to + timedelta(days=300)
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(way_after_deadline)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_weekly_check_does_nothing_when_no_deadline(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )

        # when
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(datetime.now(pytz.UTC))

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_weekly_check_should_result_in_nothing_when_not_close_to_deadline_and_demands_not_satisfied(self) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.SINGLE_DEMAND
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC)))
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        way_before_deadline: datetime = self.PROJECT_DATES.to - timedelta(days=300)
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(way_before_deadline)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.DO_NOTHING, next_step)

    def test_weekly_check_should_result_in_find_available_when_close_to_deadline_and_demands_not_satisfied(
        self,
    ) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(1000), datetime.now(pytz.UTC)))
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        close_to_deadline: datetime = self.PROJECT_DATES.to - timedelta(days=20)
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(close_to_deadline)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.FIND_AVAILABLE, next_step)

    def test_weekly_check_should_result_in_replacement_suggesting_when_high_value_project_really_close_to_deadline_and_demands_not_satisfied(
        self,
    ) -> None:
        # given
        saga: RiskPeriodicCheckSaga = RiskPeriodicCheckSaga(
            project_id=self.PROJECT_ID, missing_demands=self.MANY_DEMANDS
        )
        # and
        saga.handle(EarningsRecalculated.of(self.PROJECT_ID, Earnings.of(10000), datetime.now(pytz.UTC)))
        # and
        saga.handle(ProjectAllocationScheduled.of(self.PROJECT_ID, self.PROJECT_DATES, datetime.now(pytz.UTC)))

        # when
        really_close_to_deadline: datetime = self.PROJECT_DATES.to - timedelta(days=2)
        next_step: RiskPeriodicCheckSagaStep = saga.handle_weekly_check(really_close_to_deadline)

        # then
        self.assertEqual(RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT, next_step)
