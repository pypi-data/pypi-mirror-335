""" This module contains globally accessible enums """

from enum import Enum, StrEnum, IntEnum, auto

class OptionPayoff(Enum):
    """The payoff style of option contract."""

    CALL_OPTION = auto()
    PUT_OPTION = auto()

class Moneyness(Enum):
    """ The moneyness of an option in Delta-convention """
    TEN_DELTA_CALL = auto()
    TWENTY_FIVE_DELTA_CALL = auto()
    ATM = auto()
    TWENTY_FIVE_DELTA_PUT = auto()
    TEN_DELTA_PUT = auto()

class ExerciseStyle(Enum):
    """ The exercise style of an option"""
    EUROPEAN = auto()
    AMERICAN = auto()
    BERMUDAN = auto()