## @ingroup Analyses-Mission-Segments-Vertical_Flight
# RCAIDE/Analyses/Mission/Segments/Vertical_Flight/Descent.py
# (c) Copyright 2023 Aerospace Research Community LLC
# 
# Created:  Jul 2023, M. Clarke
 
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports 
from RCAIDE.Core                                 import Units 
from RCAIDE.Analyses.Mission.Segments.Evaluate   import Evaluate 
from RCAIDE.Methods.Mission                      import Common,Segments

# ----------------------------------------------------------------------------------------------------------------------
#  Descent
# ----------------------------------------------------------------------------------------------------------------------

## @ingroup Analyses-Mission-Segments-Vertical_Flight
class Descent(Evaluate):
    """ A vertically descending hover for VTOL aircraft. Although the vehicle moves, no aerodynamic drag and lift are used.
    
        Assumptions:
        Your vehicle creates a negligible drag and lift force during a vertical descent.
        
        Source:
        None
    """      
    
    def __defaults__(self):
        """ This sets the default solver flow. Anything in here can be modified after initializing a segment.
    
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
        
        # -------------------------------------------------------------------------------------------------------------- 
        #   User Inputs
        # -------------------------------------------------------------------------------------------------------------- 
        
        self.altitude_start    = None # Optional
        self.altitude_end      = 1. * Units.km
        self.descent_rate      = 1.  * Units.m / Units.s
        self.true_course_angle = 0.0 * Units.degrees 

        # -------------------------------------------------------------------------------------------------------------- 
        #  Mission Specific Unknowns and Residuals 
        # --------------------------------------------------------------------------------------------------------------
        ones_row = self.state.ones_row
        self.state.unknowns.throttle   = ones_row(1) * 0.5
        self.state.residuals.forces    = ones_row(1) * 0.0 
        
        # -------------------------------------------------------------------------------------------------------------- 
        #  Mission specific processes 
        # --------------------------------------------------------------------------------------------------------------  
        initialize                         = self.process.initialize
        iterate                            = self.process.iterate 
        initialize.conditions              = Segments.Vertical_Flight.Descent.initialize_conditions
        iterate.residuals.total_forces     = Common.Residuals.vertical_flight_forces
        return
       