## @ingroup Analyses-Mission
# RCAIDE/Analyses/Mission/Mission.py
# (c) Copyright 2023 Aerospace Research Community LLC
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
# RCAIDE imports        
from . import Segments
from RCAIDE.Core import Container , Data 

# ----------------------------------------------------------------------------------------------------------------------
#  Mission
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Analyses-Mission
class Missions(Container):
    """ Mission.py: Top-level mission class
    
        Assumptions:
        None
        
        Source:
        None
    """ 
    
    def __defaults__(self):
        """This sets the default values.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            None
        """         
        self.tag      = 'missions'    

    def append_mission(self,mission): 
        
        self.append(mission)
        return        
    
     