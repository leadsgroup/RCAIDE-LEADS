
## @ingroup Energy-Thermal_Management-Batteries-Heat_Addition_Systems
# RCAIDE/Energy/Thermal_Management/Batteries/Heat_Addition_Systems/No_Heat_Addition/no_heat_power_consumed.py
# 
# 
# Created:  Mar 2024, 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE imports  
from RCAIDE.Core import Data  


# ----------------------------------------------------------------------------------------------------------------------
#  Compute Power Consumed by heating element
# ----------------------------------------------------------------------------------------------------------------------
def compute_reservoir_temperature(RES,battery_conditions,state,dt,i):
    
    # Ambient Air Temperature 
    T_ambient                   = state.conditions.freestream.temperature[i,0] 
    
    battery_conditions.thermal_management_system.RES.coolant_temperature[i+1,0] = T_ambient

    return 
