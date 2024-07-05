from decimal import Decimal

from attr import frozen
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability


@frozen
class AdditionalPricedCapability:
    value: Decimal
    available_resource_capability: AvailableResourceCapability
