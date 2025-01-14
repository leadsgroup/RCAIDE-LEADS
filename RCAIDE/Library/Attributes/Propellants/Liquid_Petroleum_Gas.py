# RCAIDE/Library/Attributes/Propellants/Liquid_Petroleum_Gas.py
# 
#
# Created:  Mar 2024, M. Clarke

# ---------------------------------------------------------------------------------------------------------------------- 
#  Imports
# ---------------------------------------------------------------------------------------------------------------------- 

from .Propellant import Propellant   

# ---------------------------------------------------------------------------------------------------------------------- 
#  Gaseous_Hydrogen Class
# ----------------------------------------------------------------------------------------------------------------------   
class Liquid_Petroleum_Gas(Propellant):
    """
    A class representing Liquid Petroleum Gas (LPG) fuel properties and composition 
    for propulsion applications. 

    Attributes
    ----------
    tag : str
        Identifier for the propellant ('Liquid_Petroleum_Gas')
    reactant : str
        Oxidizer used for combustion ('O2')
    density : float
        Fuel density in kg/m³ (509.26)
    specific_energy : float
        Specific energy content in J/kg (43.1e6)
    energy_density : float
        Energy density in J/m³ (21949.1e6)
    use_high_fidelity_kinetics_model : bool
        Flag for using detailed chemical kinetics (False)
    fuel_surrogate_chemical_properties : dict
        Simplified chemical composition for surrogate model
            - C3H8 : float
                Propane fraction (0.6)
            - C4H10 : float
                Butane fraction (0.4)
    fuel_chemical_properties : dict
        Detailed chemical composition for high-fidelity model
            - NC10H22 : float
                n-Decane fraction (0.16449)
            - NC12H26 : float
                n-Dodecane fraction (0.34308)
            - NC16H34 : float
                n-Hexadecane fraction (0.10335)
            - IC8H18 : float
                iso-Octane fraction (0.08630)
            - NC7H14 : float
                n-Heptene fraction (0.07945)
            - C6H5C2H5 : float
                Ethylbenzene fraction (0.07348)
            - C6H5C4H9 : float
                Butylbenzene fraction (0.05812)
            - C10H7CH3 : float
                Methylnaphthalene fraction (0.10972)
    global_warming_potential_100 : Data
        100-year global warming potentials
            - CO2 : float
                Carbon dioxide (1)
            - H2O : float
                Water vapor (0.06)
            - SO2 : float
                Sulfur dioxide (-226)
            - NOx : float
                Nitrogen oxides (52)
            - Soot : float
                Particulate matter (1166)
            - Contrails : float
                Contrail formation (11)

    Notes
    -----
    LPG is stored as a liquid under moderate pressure at ambient temperature. The 
    composition can vary seasonally and by region, but typically consists of a 
    propane-butane mixture.

    **Definitions**
    
    'Surrogate Model'
        Simplified two-component representation using propane and butane
    
    'High-Fidelity Model'
        Detailed representation including aromatic and aliphatic hydrocarbons
    
    'Global Warming Potential'
        Relative measure of heat trapped in atmosphere compared to CO2

    **Major Assumptions**
        * Surrogate model captures main combustion characteristics
        * Air composition is standard atmospheric

    References
    ----------
    [1] Unknown
    """

    def __defaults__(self):
        """This sets the default values. 
    
    Assumptions:
        None
    
    Source:
        None
        """    
        self.tag             = 'Liquid_Petroleum_Gas'
        self.reactant        = 'O2'
        self.density         = 509.26                           # kg/m^3 
        self.specific_energy = 43.1e6                           # J/kg
        self.energy_density  = 21949.1e6                        # J/m^3
        

        self.use_high_fidelity_kinetics_model      =  False 
        self.fuel_surrogate_chemical_properties    = {'C3H8': 0.6, 'C4H10':0.4}
        self.fuel_chemical_properties              = {'NC10H22':0.16449, 'NC12H26':0.34308, 'NC16H34':0.10335, 'IC8H18':0.08630, 'NC7H14':0.07945, 'C6H5C2H5': 0.07348, 'C6H5C4H9': 0.05812, 'C10H7CH3': 0.10972}      # [2] More accurate kinetic mechanism, slower simulation    
        self.air_chemical_properties               = {'O2':0.2095, 'N2':0.7809, 'AR':0.0096}
        self.surrogate_species_list                = ['CO', 'CO2', 'H2O']
        self.species_list                          = ['CO', 'CO2', 'H2O', 'NO', 'NO2', 'CSOLID']   
        self.surrogate_chemical_kinetics           = 'Fuel_Surrogate.yaml'
        self.chemical_kinetics                     = 'Fuel.yaml'
        self.oxidizer                              = 'Air.yaml'     
        
        self.global_warming_potential_100.CO2       = 1     # CO2e/kg  
        self.global_warming_potential_100.H2O       = 0.06  # CO2e/kg  
        self.global_warming_potential_100.SO2       = -226  # CO2e/kg  
        self.global_warming_potential_100.NOx       = 52    # CO2e/kg  
        self.global_warming_potential_100.Soot      = 1166  # CO2e/kg    
        self.global_warming_potential_100.Contrails = 11    # kg/CO2e/km          