# RCAIDE/Framework/Mission/Segments/Vertical_Flight/Climb.py
# 
# 
# Created:  Jul 2023, M. Clarke
 
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports  
from RCAIDE.Framework.Core                                 import Units 
from RCAIDE.Framework.Mission.Segments.Evaluate   import Evaluate 
from RCAIDE.Library.Mission                      import Common,Segments

# ----------------------------------------------------------------------------------------------------------------------
#  Climb
# ---------------------------------------------------------------------------------------------------------------------- 
class Climb(Evaluate):
    """
    Mission segment for vertical climb in VTOL aircraft

    Attributes
    ----------
    altitude_start : float
        Initial altitude [m], optional
    altitude_end : float
        Final altitude [m], defaults to 1 km
    climb_rate : float
        Vertical rate of climb [m/s], defaults to 1 m/s
    true_course : float
        True course angle [rad], defaults to 0 degrees

    Notes
    -----
    This segment simulates pure vertical climb for VTOL aircraft where
    aerodynamic forces are considered negligible. Typically used for
    multicopter or helicopter hover-climb phases where the vehicle
    maintains vertical flight with minimal forward velocity.

    The segment processes include:
    - Vertical flight conditions initialization
    - Flight dynamics evaluation
    - Power and thrust calculations

    **Major Assumptions**
    * Negligible aerodynamic lift
    * Negligible aerodynamic drag
    * Pure vertical motion
    * No lateral-directional motion
    * Thrust aligned with vertical axis
    * Quasi-steady flight
    * Constant climb rate

    **Process Flow**
    
    Initialize:
    - conditions (vertical climb)

    Iterate:
    - residuals.flight_dynamics

    See Also
    --------
    RCAIDE.Framework.Mission.Segments.Evaluate
    RCAIDE.Library.Mission.Common
    RCAIDE.Library.Mission.Segments.Vertical_Flight
    """     
    
    def __defaults__(self):
        """
        Sets default values for segment parameters

        Notes
        -----
        Initializes segment with default values and sets up process flow.
        Called automatically when segment is instantiated.

        The process flow includes vertical flight dynamics evaluation
        with focus on thrust and power requirements for climbing flight.
        """              
        
        # -------------------------------------------------------------------------------------------------------------- 
        #   User Inputs
        # -------------------------------------------------------------------------------------------------------------- 
        
        self.altitude_start    = None # Optional
        self.altitude_end      = 1. * Units.km
        self.climb_rate        = 1.  * Units.m / Units.s
        self.true_course       = 0.0 * Units.degrees  
        
        # -------------------------------------------------------------------------------------------------------------- 
        #  Mission specific processes 
        # --------------------------------------------------------------------------------------------------------------  
        initialize                         = self.process.initialize
        iterate                            = self.process.iterate 
        initialize.conditions              = Segments.Vertical_Flight.Climb.initialize_conditions
        iterate.residuals.flight_dynamics  = Common.Residuals.flight_dynamics
    
        return
       