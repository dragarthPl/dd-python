from attr import frozen
from domaindrivers.smartschedule.planning.demands import Demands


@frozen
class DemandsPerStage:
    demands: dict[str, Demands]

    @classmethod
    def empty(cls) -> "DemandsPerStage":
        return cls({})
