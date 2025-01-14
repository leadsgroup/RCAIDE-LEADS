# RCAIDE/Library/Attributes/Propellants/Aviation_Gasoline.py
# 
# 
# Created:  Sep 2023, M. Clarke
# Modified: 
 
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
from .Propellant import Propellant 

# ----------------------------------------------------------------------------------------------------------------------
#  Aviation_Gasoline  
# ---------------------------------------------------------------------------------------------------------------------- 
class Aviation_Gasoline(Propellant):
    """
    A class representing aviation gasoline (avgas) fuel properties.

    Attributes
    ----------
    tag : str
        Identifier for the propellant ('Aviation_Gasoline')
    density : float
        Fuel density in kg/m³ (721.0)
    specific_energy : float
        Specific energy content in J/kg (43.71e6)

    Notes
    -----
    This class implements properties for aviation gasoline (avgas), commonly used in 
    piston-engine aircraft.

    **Definitions**
    
    'Avgas'
        Aviation gasoline, a high-octane fuel specifically formulated for 
        aircraft piston engines
    
    'Specific Energy'
        The amount of energy per unit mass of fuel, indicating the fuel's 
        energy content

    **Major Assumptions**
        * Properties are for standard temperature and pressure conditions
        * Fuel is assumed to be in liquid phase

    References
    ----------
    [1] Chevron Products Company. (n.d.). Aviation fuels. Chevron. https://www.chevron.com/-/media/chevron/operations/documents/aviation-tech-review.pdf 
    """

    def __defaults__(self):
        """
        Sets default values for aviation gasoline properties.

        Notes
        -----
        Initializes standard properties for AVGAS including density and specific 
        energy content. Values are based on industry standard specifications for 
        AVGAS 100LL.
        """
        self.tag             ='Aviation_Gasoline'
        self.density         = 721.0            # kg/m^3
        self.specific_energy = 43.71e6          # J/kg     
        
