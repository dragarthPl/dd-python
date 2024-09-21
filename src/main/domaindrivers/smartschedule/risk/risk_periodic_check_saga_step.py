from enum import Enum


class RiskPeriodicCheckSagaStep(Enum):
    FIND_AVAILABLE = 0
    DO_NOTHING = 1
    SUGGEST_REPLACEMENT = 2
    NOTIFY_ABOUT_POSSIBLE_RISK = 3
    NOTIFY_ABOUT_DEMANDS_SATISFIED = 4
