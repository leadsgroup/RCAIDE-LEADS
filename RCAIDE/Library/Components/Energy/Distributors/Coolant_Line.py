# RCAIDE/Library/Compoments/Energy/Networks/Distribution/Coolant_Line.py 
# 
# Created:  Aug 2024, S. Shekar

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
# RCAIDE imports  
from RCAIDE.Library.Components                                import Component
from RCAIDE.Library.Components.Component                      import Container    

# ----------------------------------------------------------------------------------------------------------------------
#  Coolant Line
# ---------------------------------------------------------------------------------------------------------------------- 
class Coolant_Line(Component):
    """ Coolant line class.
    """ 
    
    def __defaults__(self):
        """This sets the default values.
    
        Assumptions:
            None
        
        Source:
            None
        """          
        self.tag                           = 'coolant_line'  

                    
    def __init__ (self, distributor=None):
        
        """This initializes empty containers to add heat acqusition systems
           for battery_modules that are present on a particular bus.
    
        Assumptions:
            None
        
        Source:
            None
        """               
        self.active                        = True 
        self.efficiency                    = 1.0
 
            
        for tag, item in  distributor.items():
            self.identical_batteries  =  distributor.identical_batteries
            if tag == 'battery_modules':
                self.battery_modules  = Container()
                for battery in item:
                    self.battery_modules[battery.tag] = Container()