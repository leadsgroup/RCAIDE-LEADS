# RCAIDE/Library/Attributes/Atmospheres/Earth/__init__.py
# 

"""
Earth atmospheric models for aircraft performance analysis.

The models provide essential atmospheric properties including pressure, temperature,
density, and other parameters needed for aircraft performance calculations.

See Also
--------
RCAIDE.Library.Attributes.Atmospheres.Atmosphere : Base atmospheric model class
RCAIDE.Library.Attributes.Planets.Earth : Earth environmental parameters
"""

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

from .Constant_Temperature import Constant_Temperature
from .US_Standard_1976     import US_Standard_1976