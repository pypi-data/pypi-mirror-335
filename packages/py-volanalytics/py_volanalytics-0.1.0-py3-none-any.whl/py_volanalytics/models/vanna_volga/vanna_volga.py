""" 
Classical Vanna-Volga approximation 

References : 
[Consistent pricing of FX options](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=873788), Castagna and Mercurio, 2006
[Implementing Vanna-Volga](https://quantdev.blog/posts/implementing-vanna-volga/)
"""
import numpy as np
from typing import Any, List, Union
import attrs
from attrs import define, field

from py_volanalytics.market.european_vanilla_option_quote import EuropeanVanillaOptionQuote

@define(kw_only=True)
class VannaVolga:
    """ This is an abstraction of the Vanna-Volga approximation """
    
    option_quotes : List[EuropeanVanillaOptionQuote]
    spot_price : float = field(
        validator=attrs.validators.and_(
            attrs.validators.instance_of(float),
            attrs.validators.ge(0.0)
        )
    )

    