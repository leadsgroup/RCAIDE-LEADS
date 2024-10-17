# RCAIDE/Library/Compoments/Energy/Sources/Battery_Modules/Generic_Battery_Module.py
# 
# 
# Created:  Mar 2024, M. Clarke
# Modified: Sep 2024, S. Shekar
 
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE imports
from RCAIDE.Framework.Core        import Data
from RCAIDE.Library.Components    import Component   
from RCAIDE.Library.Methods.Energy.Sources.Batteries.Common.append_battery_conditions import append_battery_conditions, append_battery_segment_conditions
from RCAIDE.Library.Methods.Energy.Sources.Batteries.Lithium_Ion_Generic  import * 

# ----------------------------------------------------------------------------------------------------------------------
#  Battery
# ----------------------------------------------------------------------------------------------------------------------     
## @ingroup Library-Components-Energy-Batteries
class Generic_Battery_Module(Component):
    """Default battery module class."""
    def __defaults__(self):
        """This sets the default values.
    
        Assumptions:
            None
        
        Source:
            None
        """
      
       
        self.energy_density                         = 0.0
        self.current_energy                         = 0.0
        self.current_capacitor_charge               = 0.0
        self.capacity                               = 0.0
        self.nominal_capacity                       = 0.0

        self.mass_properties.volume                 = Data()
        self.mass_properties.length                 = 0.0
        self.mass_properties.length                 = 0.0
        self.mass_properties.width                  = 0.0
        self.mass_properties.height                 = 0.0
         
        self.cell                                   = Data()
        self.cell.chemistry                         = None                             
        self.cell.discharge_performance_map         = None  
        self.cell.ragone                            = Data()
        self.cell.ragone.const_1                    = 0.0     # used for ragone functions; 
        self.cell.ragone.const_2                    = 0.0     # specific_power=ragone_const_1*10^(specific_energy*ragone_const_2)
        self.cell.ragone.lower_bound                = 0.0     # lower bound specific energy for which ragone curves no longer make sense
        self.cell.ragone.i                          = 0.0
        self.cell.hyperbolic_curve_disharge_parameters =  [17.1, 0, 2.8, 6.9]
        #add internal resistance functionality
                       
 
    def append_operating_conditions(self,segment,bus):  
        append_battery_conditions(self,segment,bus)  
        return
    
    def append_battery_segment_conditions(self,bus, conditions, segment):
        append_battery_segment_conditions(self,bus, conditions, segment)
        return
    def energy_calc(self,state,bus,coolant_lines, t_idx, delta_t): 
        """Computes the state of the LFP battery cell.
           
        Assumptions:
            None
            
        Source:
            None
    
        Args:
            self               : battery        [unitless]
            state              : temperature    [K]
            bus                : pressure       [Pa]
            discharge (boolean): discharge flag [unitless]
            
        Returns: 
            None
        """      
        stored_results_flag, stored_battery_tag =  compute_li_generic_cell_performance(self,state,bus,coolant_lines, t_idx,delta_t) 
                        
        return stored_results_flag, stored_battery_tag
    
    def reuse_stored_data(self,state,bus,coolant_lines, t_idx, delta_t,stored_results_flag, stored_battery_tag):
        reuse_stored_li_generic_cell_data(self,state,bus,coolant_lines, t_idx, delta_t,stored_results_flag, stored_battery_tag)
        return    
    
    def compute_voltage(self,battery_conditions):
        """ Computes the voltage of a single LFP cell  
    
        Assumptions:
            None
        
        Source:
            None
    
        Args:
            self               : battery          [unitless] 
            battery_conditions : state of battery [unitless]
            
        Returns: 
            None
        """              

        return battery_conditions.voltage_under_load 
    
    def update_battery_age(self,segment,increment_battery_age_by_one_day = False):   
        """ This does nothing. """
        pass 
        return
    