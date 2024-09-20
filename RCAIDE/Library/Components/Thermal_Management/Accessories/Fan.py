# RCAIDE/Library/Compoments/Thermal_Management/Accessories/Fan.py
# 
#
# Created: March 2024  S. Shekar

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
from RCAIDE.Framework.Core import Data

# ----------------------------------------------------------------------
#  Fan
# ----------------------------------------------------------------------
class Fan(Data):
    """Holds values for a model Fan 

    Assumptions:
   Power 

    Source:
    None
    """

    def __defaults__(self):
        """This sets the default values.

        Assumptions:
        None

        Source:
        None

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """
        self.tag                       = 'Fan'
        self.efficiency                = 1.0
        
        return
   
    def compute_power_consumed (pressure_differerntial, density, mass_flow_rate,efficiency):
        return mass_flow_rate*pressure_differerntial/(density*efficiency)