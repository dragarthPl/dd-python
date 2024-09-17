import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.event import Event


@frozen
class EarningsRecalculated(Event):
    uuid: UUID
    project_id: ProjectAllocationsId
    earnings: Earnings
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at

    @classmethod
    def of(cls, project_id: ProjectAllocationsId, earnings: Earnings, instant: datetime) -> "EarningsRecalculated":
        return cls(
            uuid.uuid4(),
            project_id,
            earnings,
            instant,
        )
