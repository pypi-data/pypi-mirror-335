""" Quote for a European Vanilla Option """

from typing import Optional
import attrs
from attrs import define, field

from py_volanalytics.types.enums import ExerciseStyle, Moneyness

@define(repr=True, kw_only=True)
class EuropeanVanillaOptionQuote:
    """ Quote for European-style vanilla options """
    underlying : str = field(validator=attrs.validators.instance_of(str))
    accounting : Optional[str] = field(default=None)
    strike : Optional[float] = field(default=None)
    time_to_expiry : float = field(default=1.0, validator=attrs.validators.ge(0.0))
    exercise_style : ExerciseStyle = field(default=ExerciseStyle.EUROPEAN, validator=attrs.validators.instance_of(ExerciseStyle))
    moneyness : Optional[Moneyness] = field(default=None)
    quote : float = field(validator=attrs.validators.ge(0.0))

    def __attrs_post_init__(self):
        """ Perform validations over the whole instance """
        if (not self.strike) and (not self.moneyness):
            raise ValueError("Atleast one of option strike and moneyness must be supplied!")