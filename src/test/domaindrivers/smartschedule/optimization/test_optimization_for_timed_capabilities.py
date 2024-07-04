from unittest import TestCase

from domaindrivers.smartschedule.optimization.item import Item
from domaindrivers.smartschedule.optimization.optimization_facade import OptimizationFacade
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.optimization.total_capacity import TotalCapacity
from domaindrivers.smartschedule.optimization.total_weight import TotalWeight
from domaindrivers.smartschedule.shared.time_slot import TimeSlot

from .capability_capacity_dimension import CapabilityTimedCapacityDimension, CapabilityTimedWeightDimension


class TestOptimizationForTimedCapabilities(TestCase):
    facade: OptimizationFacade = OptimizationFacade()

    def test_nothing_is_chosen_when_no_capacities_in_time_slot(self) -> None:
        # given
        june: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2020, 6)
        october: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2020, 10)

        items: list[Item] = [
            Item("Item1", 100, TotalWeight.of(CapabilityTimedWeightDimension("COMMON SENSE", "Skill", june))),
            Item("Item2", 100, TotalWeight.of(CapabilityTimedWeightDimension("THINKING", "Skill", june))),
        ]

        # when
        result: Result = self.facade.calculate(
            items,
            TotalCapacity.of(CapabilityTimedCapacityDimension.of_random_uuid("anna", "COMMON SENSE", "Skill", october)),
        )

        # then
        self.assertEqual(0, result.profit, 0.0)
        self.assertEqual(0, len(result.chosen_items))

    def test_most_profitable_item_is_chosen(self) -> None:
        # given
        june: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2020, 6)

        items: list[Item] = [
            Item("Item1", 200, TotalWeight.of(CapabilityTimedWeightDimension("COMMON SENSE", "Skill", june))),
            Item("Item2", 100, TotalWeight.of(CapabilityTimedWeightDimension("THINKING", "Skill", june))),
        ]

        # when
        result: Result = self.facade.calculate(
            items,
            TotalCapacity.of(CapabilityTimedCapacityDimension.of_random_uuid("anna", "COMMON SENSE", "Skill", june)),
        )

        # then
        self.assertEqual(200, result.profit, 0.0)
        self.assertEqual(1, len(result.chosen_items))
