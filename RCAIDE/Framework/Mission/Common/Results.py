# RCAIDE/Framework/Analyses/Mission/Segments/Conditions/Results.py
# 
# 
# Created:  Jul 2023, M. Clarke
# Updated:  May 2024, M. Guidotti

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports 
from RCAIDE.Framework.Mission.Common import Conditions

# python imports
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------------------------------------------------- 

class Results(Conditions):
    """
    Data structure for storing mission analysis results and aerodynamic data

    Attributes
    ----------
    tag : str
        Identifier, defaults to 'results'

    S_ref : ndarray
        Reference area [m^2]
    c_ref : ndarray
        Reference chord [m]
    b_ref : ndarray
        Reference span [m]
    X_ref : ndarray
        X reference location [m]
    Y_ref : ndarray
        Y reference location [m]
    Z_ref : ndarray
        Z reference location [m]

    frames : Conditions
        Reference frame data:
        
        - inertial : Conditions
            - position_vector [m]
            - velocity_vector [m/s]
            - acceleration_vector [m/s^2]
            - angular_velocity_vector [rad/s]
            - angular_acceleration_vector [rad/s^2]
            - gravity_force_vector [N]
            - total_force_vector [N]
            - total_moment_vector [N-m]
            - time [s]
            - aircraft_range [m]

        - body : Conditions
            - inertial_rotations [rad]
            - thrust_force_vector [N]
            - moment_vector [N-m]
            - velocity_vector [m/s]
            - thrust_moment_vector [N-m]
            - transform_to_inertial [ndarray]

        - wind : Conditions
            - body_rotations [rad]
            - velocity_vector [m/s]
            - force_vector [N]
            - moment_vector [N-m]
            - transform_to_inertial [ndarray]

        - planet : Conditions
            - start_time [s]
            - latitude [rad]
            - longitude [rad]
            - true_course [rad]
            - true_heading [rad]

    freestream : Conditions
        Flow conditions:
        - velocity [m/s]
        - mach_number [-]
        - pressure [Pa]
        - temperature [K]
        - density [kg/m^3]
        - speed_of_sound [m/s]
        - dynamic_viscosity [N-s/m^2]
        - altitude [m]
        - gravity [m/s^2]
        - reynolds_number [-]
        - dynamic_pressure [Pa]
        - delta_ISA [K]

    aerodynamics : Conditions
        Aerodynamic properties:
        
        - angles : Conditions
            - alpha [rad]
            - beta [rad]
            - phi [rad]
            
        - coefficients : Conditions
            - lift [-]
            - drag [-]
            - surface_pressure [-]
            (includes detailed breakdowns of lift/drag components)

    control_surfaces : Conditions
        Control surface data for:
        - aileron
        - elevator
        - rudder
        - flap
        - slat
        Each includes:
        - deflection [rad]
        - static_stability coefficients

    stability : Conditions
        Stability derivatives and parameters:
        - static_margin [-]
        - neutral_point [-]
        - static_stability derivatives

    emissions : Conditions
        Emissions data

    noise : Conditions
        Acoustic data

    energy : Conditions
        Energy and propulsion data:
        - throttle [-]
        - thrust_force_vector [N]
        - power [W]
        - vehicle_mass_rate [kg/s]

    weights : Conditions
        Mass properties:
        - total_mass [kg]
        - total_moment_of_inertia [kg-m^2]
        - vehicle_mass_rate [kg/s]

    Notes
    -----
    This class provides a comprehensive data structure for storing all results
    from mission analysis. It inherits from Conditions to provide data
    structure functionality.

    **Major Assumptions**
    * All arrays properly sized for mission points
    * Units are consistent throughout
    * Reference frame transformations are valid
    * Coefficient subscripts follow standard conventions:
        - X,Y,Z : force components
        - L,M,N : moment components
        - u,v,w : velocity components
        - p,q,r : angular rates

    See Also
    --------
    RCAIDE.Framework.Mission.Common.Conditions
    RCAIDE.Framework.Mission.Common.State
    """
    
    
    def __defaults__(self):
        """
        Sets default values for results container

        Notes
        -----
        Initializes all results arrays with zeros.
        Creates nested Conditions objects for organizing data.
        Called automatically when class is instantiated.

        **Major Assumptions**
        * One column arrays for scalar quantities
        * Three column arrays for vector quantities
        * Empty arrays for undefined quantities
        """ 
        
        self.tag                                              = 'results' 
 
        # start default row vectors
        ones_1col                                             = self.ones_row(1)  
        ones_3col                                             = self.ones_row(3)
        
        # ----------------------------------------------------------------------------------------------------------------------         
        # Reference Values 
        # ---------------------------------------------------------------------------------------------------------------------- 
    
        self.S_ref                                            = ones_1col * 0
        self.c_ref                                            = ones_1col * 0
        self.b_ref                                            = ones_1col * 0
        self.X_ref                                            = ones_1col * 0
        self.Y_ref                                            = ones_1col * 0
        self.Z_ref                                            = ones_1col * 0     
        
        # ----------------------------------------------------------------------------------------------------------------------         
        # Frames 
        # ---------------------------------------------------------------------------------------------------------------------- 
        self.frames                                           = Conditions()
        
        # inertial conditions
        self.frames.inertial                                                   = Conditions()        
        self.frames.inertial.position_vector                                   = ones_3col * 0
        self.frames.inertial.velocity_vector                                   = ones_3col * 0
        self.frames.inertial.acceleration_vector                               = ones_3col * 0
        self.frames.inertial.angular_velocity_vector                           = ones_3col * 0
        self.frames.inertial.angular_acceleration_vector                       = ones_3col * 0
        self.frames.inertial.gravity_force_vector                              = ones_3col * 0
        self.frames.inertial.total_force_vector                                = ones_3col * 0
        self.frames.inertial.total_moment_vector                               = ones_3col * 0
        self.frames.inertial.time                                              = ones_1col * 0
        self.frames.inertial.aircraft_range                                    = ones_1col * 0

                                                                               
        # body conditions                                                      
        self.frames.body                                                       = Conditions()        
        self.frames.body.inertial_rotations                                    = ones_3col * 0
        self.frames.body.thrust_force_vector                                   = ones_3col * 0
        self.frames.body.moment_vector                                         = ones_3col * 0
        self.frames.body.velocity_vector                                       = ones_3col * 0
        self.frames.body.thrust_moment_vector                                  = ones_3col * 0 
        self.frames.body.transform_to_inertial                                 = np.empty([0,0,0])
                                                                               
        # wind frame conditions                                                
        self.frames.wind                                                       = Conditions()
        self.frames.wind.body_rotations                                        = ones_3col * 0 # rotations in [X,Y,Z] -> [phi,theta,psi]
        self.frames.wind.velocity_vector                                       = ones_3col * 0
        self.frames.wind.force_vector                                          = ones_3col * 0
        self.frames.wind.moment_vector                                         = ones_3col * 0
        self.frames.wind.transform_to_inertial                                 = np.empty([0,0,0]) 
                                                                               
        # planet frame conditions                                              
        self.frames.planet                                                     = Conditions()
        self.frames.planet.start_time                                          = None
        self.frames.planet.latitude                                            = ones_1col * 0
        self.frames.planet.longitude                                           = ones_1col * 0
        self.frames.planet.true_course                                         = ones_1col * 0
        self.frames.planet.true_heading                                        = ones_1col * 0

        # ----------------------------------------------------------------------------------------------------------------------         
        # Freestream 
        # ----------------------------------------------------------------------------------------------------------------------    
        self.freestream                                                        = Conditions()        
        self.freestream.velocity                                               = ones_1col * 0
        self.freestream.u                                                      = ones_1col * 0
        self.freestream.v                                                      = ones_1col * 0
        self.freestream.w                                                      = ones_1col * 0
        self.freestream.mach_number                                            = ones_1col * 0
        self.freestream.pressure                                               = ones_1col * 0
        self.freestream.temperature                                            = ones_1col * 0
        self.freestream.density                                                = ones_1col * 0
        self.freestream.speed_of_sound                                         = ones_1col * 0
        self.freestream.dynamic_viscosity                                      = ones_1col * 0
        self.freestream.altitude                                               = ones_1col * 0
        self.freestream.gravity                                                = ones_1col * 0
        self.freestream.reynolds_number                                        = ones_1col * 0
        self.freestream.dynamic_pressure                                       = ones_1col * 0
        self.freestream.delta_ISA                                              = ones_1col * 0

        # ----------------------------------------------------------------------------------------------------------------------         
        # Aerodynamics
        # ----------------------------------------------------------------------------------------------------------------------  
        self.aerodynamics                                                      = Conditions() 
                                                                               
        # aerdynamic angles                                                    
        self.aerodynamics.angles                                               = Conditions()
        self.aerodynamics.angles.alpha                                         = ones_1col * 0
        self.aerodynamics.angles.beta                                          = ones_1col * 0
        self.aerodynamics.angles.phi                                           = ones_1col * 0 
                                                                               
        # aerodynamic coefficients                                             
        self.aerodynamics.coefficients                                         = Conditions()
        self.aerodynamics.coefficients.lift                                    = ones_1col * 0
        self.aerodynamics.coefficients.drag                                    = ones_1col * 0     
                                                                               
        # aerodynamic coefficients                                             
        self.aerodynamics.coefficients                                         = Conditions()
        self.aerodynamics.coefficients.surface_pressure                        = None
        self.aerodynamics.coefficients.lift                                    = Conditions()
        self.aerodynamics.coefficients.lift.total                              = None
        self.aerodynamics.coefficients.lift.induced                            = Conditions()
        self.aerodynamics.coefficients.lift.induced.inviscid_wings             = Conditions()
        self.aerodynamics.coefficients.lift.compressible_wings                 = Conditions() 
        self.aerodynamics.coefficients.drag                                    = Conditions()  
        self.aerodynamics.coefficients.drag.total                              = ones_1col * 0   
        self.aerodynamics.coefficients.drag.parasite                           = Conditions()
        self.aerodynamics.coefficients.drag.compressible                       = Conditions()
        self.aerodynamics.coefficients.drag.induced                            = Conditions()
        self.aerodynamics.coefficients.drag.induced.total                      = ones_1col * 0 
        self.aerodynamics.coefficients.drag.induced.inviscid                   = ones_1col * 0 
        self.aerodynamics.coefficients.drag.induced.inviscid_wings             = Conditions()
        self.aerodynamics.coefficients.drag.cooling                            = Conditions()
        self.aerodynamics.coefficients.drag.cooling.total                      = ones_1col * 0
        self.aerodynamics.coefficients.drag.windmilling                        = Conditions()
        self.aerodynamics.coefficients.drag.windmilling.total                  = ones_1col * 0
        self.aerodynamics.coefficients.drag.asymmetry_trim                     = Conditions()
        self.aerodynamics.coefficients.drag.asymmetry_trim.total               = ones_1col * 0 
        
        self.aerodynamics.coefficients.drag.induced.efficiency_factor          = ones_1col * 0 
        self.aerodynamics.oswald_efficiency                                    = ones_1col * 0 
 
        # ----------------------------------------------------------------------------------------------------------------------
        # Control Surfaces 
        # ----------------------------------------------------------------------------------------------------------------------
        self.control_surfaces                                                  = Conditions()

        self.control_surfaces.aileron                                          = Conditions()
        self.control_surfaces.aileron.deflection                               = ones_1col * 0 
        self.control_surfaces.aileron.static_stability                         = Conditions()
        self.control_surfaces.aileron.static_stability.coefficients            = Conditions() 
        self.control_surfaces.aileron.static_stability.coefficients.lift       = ones_1col * 0        
        self.control_surfaces.aileron.static_stability.coefficients.drag       = ones_1col * 0           
        self.control_surfaces.aileron.static_stability.coefficients.X          = ones_1col * 0           
        self.control_surfaces.aileron.static_stability.coefficients.Y          = ones_1col * 0           
        self.control_surfaces.aileron.static_stability.coefficients.Z          = ones_1col * 0         
        self.control_surfaces.aileron.static_stability.coefficients.L          = ones_1col * 0         
        self.control_surfaces.aileron.static_stability.coefficients.M          = ones_1col * 0         
        self.control_surfaces.aileron.static_stability.coefficients.N          = ones_1col * 0           
        self.control_surfaces.aileron.static_stability.coefficients.e          = ones_1col * 0
        
        self.control_surfaces.elevator                                         = Conditions()
        self.control_surfaces.elevator.deflection                              = ones_1col * 0 
        self.control_surfaces.elevator.static_stability                        = Conditions()
        self.control_surfaces.elevator.static_stability.coefficients           = Conditions() 
        self.control_surfaces.elevator.static_stability.coefficients.lift      = ones_1col * 0        
        self.control_surfaces.elevator.static_stability.coefficients.drag      = ones_1col * 0           
        self.control_surfaces.elevator.static_stability.coefficients.X         = ones_1col * 0           
        self.control_surfaces.elevator.static_stability.coefficients.Y         = ones_1col * 0           
        self.control_surfaces.elevator.static_stability.coefficients.Z         = ones_1col * 0         
        self.control_surfaces.elevator.static_stability.coefficients.L         = ones_1col * 0         
        self.control_surfaces.elevator.static_stability.coefficients.M         = ones_1col * 0         
        self.control_surfaces.elevator.static_stability.coefficients.N         = ones_1col * 0           
        self.control_surfaces.elevator.static_stability.coefficients.e         = ones_1col * 0
        
        self.control_surfaces.rudder                                           = Conditions()
        self.control_surfaces.rudder.deflection                                = ones_1col * 0 
        self.control_surfaces.rudder.static_stability                          = Conditions()
        self.control_surfaces.rudder.static_stability.coefficients             = Conditions() 
        self.control_surfaces.rudder.static_stability.coefficients.lift        = ones_1col * 0         
        self.control_surfaces.rudder.static_stability.coefficients.drag        = ones_1col * 0          
        self.control_surfaces.rudder.static_stability.coefficients.X           = ones_1col * 0          
        self.control_surfaces.rudder.static_stability.coefficients.Y           = ones_1col * 0          
        self.control_surfaces.rudder.static_stability.coefficients.Z           = ones_1col * 0         
        self.control_surfaces.rudder.static_stability.coefficients.L           = ones_1col * 0         
        self.control_surfaces.rudder.static_stability.coefficients.M           = ones_1col * 0         
        self.control_surfaces.rudder.static_stability.coefficients.N           = ones_1col * 0           
        self.control_surfaces.rudder.static_stability.coefficients.e           = ones_1col * 0
        
        self.control_surfaces.flap                                             = Conditions()
        self.control_surfaces.flap.deflection                                  = ones_1col * 0 
        self.control_surfaces.flap.static_stability                            = Conditions()
        self.control_surfaces.flap.static_stability.coefficients               = Conditions() 
        self.control_surfaces.flap.static_stability.coefficients.lift          = ones_1col * 0        
        self.control_surfaces.flap.static_stability.coefficients.drag          = ones_1col * 0           
        self.control_surfaces.flap.static_stability.coefficients.X             = ones_1col * 0           
        self.control_surfaces.flap.static_stability.coefficients.Y             = ones_1col * 0           
        self.control_surfaces.flap.static_stability.coefficients.Z             = ones_1col * 0         
        self.control_surfaces.flap.static_stability.coefficients.L             = ones_1col * 0         
        self.control_surfaces.flap.static_stability.coefficients.M             = ones_1col * 0         
        self.control_surfaces.flap.static_stability.coefficients.N             = ones_1col * 0           
        self.control_surfaces.flap.static_stability.coefficients.e             = ones_1col * 0
        
        self.control_surfaces.slat                                             = Conditions()
        self.control_surfaces.slat.deflection                                  = ones_1col * 0 
        self.control_surfaces.slat.static_stability                            = Conditions()
        self.control_surfaces.slat.static_stability.coefficients               = Conditions() 
        self.control_surfaces.slat.static_stability.coefficients.lift          = ones_1col * 0         
        self.control_surfaces.slat.static_stability.coefficients.drag          = ones_1col * 0          
        self.control_surfaces.slat.static_stability.coefficients.X             = ones_1col * 0          
        self.control_surfaces.slat.static_stability.coefficients.Y             = ones_1col * 0          
        self.control_surfaces.slat.static_stability.coefficients.Z             = ones_1col * 0         
        self.control_surfaces.slat.static_stability.coefficients.L             = ones_1col * 0         
        self.control_surfaces.slat.static_stability.coefficients.M             = ones_1col * 0         
        self.control_surfaces.slat.static_stability.coefficients.N             = ones_1col * 0           
        self.control_surfaces.slat.static_stability.coefficients.e             = ones_1col * 0

        # ----------------------------------------------------------------------------------------------------------------------
        # Stability 
        # ----------------------------------------------------------------------------------------------------------------------  
        self.stability                                                         = Conditions()
        self.static_stability                                                  = Conditions()
 
        self.static_stability.forces                                           = Conditions()
        self.static_stability.forces.lift                                      = ones_1col * 0
        self.static_stability.forces.drag                                      = ones_1col * 0
        self.static_stability.forces.X                                         = ones_1col * 0
        self.static_stability.forces.Y                                         = ones_1col * 0
        self.static_stability.forces.Z                                         = ones_1col * 0
                                                                               
        self.static_stability.moments                                          = Conditions()
        self.static_stability.moments.L                                        = ones_1col * 0
        self.static_stability.moments.M                                        = ones_1col * 0
        self.static_stability.moments.N                                        = ones_1col * 0
                                                                               
        self.static_stability.static_margin                                    = ones_1col * 0
        self.static_stability.neutral_point                                    = ones_1col * 0
        self.static_stability.spiral_criteria                                  = ones_1col * 0 
        self.static_stability.pitch_rate                                       = ones_1col * 0
        self.static_stability.roll_rate                                        = ones_1col * 0
        self.static_stability.yaw_rate                                         = ones_1col * 0 
                                                                               
        self.static_stability.coefficients                                     = Conditions()
        self.static_stability.coefficients.lift                                = ones_1col * 0
        self.static_stability.coefficients.drag                                = ones_1col * 0
        self.static_stability.coefficients.X                                   = ones_1col * 0
        self.static_stability.coefficients.Y                                   = ones_1col * 0
        self.static_stability.coefficients.Z                                   = ones_1col * 0
        self.static_stability.coefficients.L                                   = ones_1col * 0
        self.static_stability.coefficients.M                                   = ones_1col * 0
        self.static_stability.coefficients.N                                   = ones_1col * 0 
        self.static_stability.coefficients.roll                                = ones_1col * 0
        self.static_stability.coefficients.pitch                               = ones_1col * 0
        self.static_stability.coefficients.yaw                                 = ones_1col * 0  
                                                                               
        self.static_stability.derivatives                                      = Conditions()
                                                                               
        # stability axis                                                       
        self.static_stability.derivatives.Clift_alpha                          = ones_1col * 0
        self.static_stability.derivatives.Clift_beta                           = ones_1col * 0
        self.static_stability.derivatives.Clift_delta_a                        = ones_1col * 0
        self.static_stability.derivatives.Clift_delta_e                        = ones_1col * 0
        self.static_stability.derivatives.Clift_delta_r                        = ones_1col * 0
        self.static_stability.derivatives.Clift_delta_f                        = ones_1col * 0
        self.static_stability.derivatives.Clift_delta_s                        = ones_1col * 0
        self.static_stability.derivatives.Cdrag_alpha                          = ones_1col * 0
        self.static_stability.derivatives.Cdrag_beta                           = ones_1col * 0
        self.static_stability.derivatives.Cdrag_delta_a                        = ones_1col * 0
        self.static_stability.derivatives.Cdrag_delta_e                        = ones_1col * 0
        self.static_stability.derivatives.Cdrag_delta_r                        = ones_1col * 0
        self.static_stability.derivatives.Cdrag_delta_f                        = ones_1col * 0
        self.static_stability.derivatives.Cdrag_delta_s                        = ones_1col * 0
        self.static_stability.derivatives.CX_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CX_beta                              = ones_1col * 0
        self.static_stability.derivatives.CX_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CX_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CX_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CX_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CX_delta_s                           = ones_1col * 0
        self.static_stability.derivatives.CY_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CY_beta                              = ones_1col * 0
        self.static_stability.derivatives.CY_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CY_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CY_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CY_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CY_delta_s                           = ones_1col * 0
        self.static_stability.derivatives.CZ_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CZ_beta                              = ones_1col * 0
        self.static_stability.derivatives.CZ_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CZ_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CZ_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CZ_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CZ_delta_s                           = ones_1col * 0
        self.static_stability.derivatives.CL_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CL_beta                              = ones_1col * 0
        self.static_stability.derivatives.CL_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CL_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CL_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CL_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CL_delta_s                           = ones_1col * 0
        self.static_stability.derivatives.CM_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CM_beta                              = ones_1col * 0
        self.static_stability.derivatives.CM_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CM_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CM_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CM_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CM_delta_s                           = ones_1col * 0
        self.static_stability.derivatives.CN_alpha                             = ones_1col * 0
        self.static_stability.derivatives.CN_beta                              = ones_1col * 0
        self.static_stability.derivatives.CN_delta_a                           = ones_1col * 0
        self.static_stability.derivatives.CN_delta_e                           = ones_1col * 0
        self.static_stability.derivatives.CN_delta_r                           = ones_1col * 0
        self.static_stability.derivatives.CN_delta_f                           = ones_1col * 0
        self.static_stability.derivatives.CN_delta_s                           = ones_1col * 0
        
        # body axis derivatives
        self.static_stability.derivatives.Clift_u                              = ones_1col * 0
        self.static_stability.derivatives.Clift_v                              = ones_1col * 0
        self.static_stability.derivatives.Clift_w                              = ones_1col * 0 
        self.static_stability.derivatives.Cdrag_u                              = ones_1col * 0
        self.static_stability.derivatives.Cdrag_v                              = ones_1col * 0
        self.static_stability.derivatives.Cdrag_w                              = ones_1col * 0         
        self.static_stability.derivatives.CX_u                                 = ones_1col * 0
        self.static_stability.derivatives.CX_v                                 = ones_1col * 0
        self.static_stability.derivatives.CX_w                                 = ones_1col * 0
        self.static_stability.derivatives.CY_u                                 = ones_1col * 0
        self.static_stability.derivatives.CY_v                                 = ones_1col * 0
        self.static_stability.derivatives.CY_w                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_u                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_v                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_w                                 = ones_1col * 0
        self.static_stability.derivatives.CL_u                                 = ones_1col * 0
        self.static_stability.derivatives.CL_v                                 = ones_1col * 0
        self.static_stability.derivatives.CL_w                                 = ones_1col * 0
        self.static_stability.derivatives.CM_u                                 = ones_1col * 0
        self.static_stability.derivatives.CM_v                                 = ones_1col * 0
        self.static_stability.derivatives.CM_w                                 = ones_1col * 0
        self.static_stability.derivatives.CN_u                                 = ones_1col * 0
        self.static_stability.derivatives.CN_v                                 = ones_1col * 0
        self.static_stability.derivatives.CN_w                                 = ones_1col * 0 
        self.static_stability.derivatives.CZ_alpha_dot                         = ones_1col * 0
        self.static_stability.derivatives.CM_alpha_dot                         = ones_1col * 0 
        self.static_stability.derivatives.Clift_p                              = ones_1col * 0
        self.static_stability.derivatives.Clift_q                              = ones_1col * 0
        self.static_stability.derivatives.Clift_r                              = ones_1col * 0
        self.static_stability.derivatives.Cdrag_p                              = ones_1col * 0
        self.static_stability.derivatives.Cdrag_q                              = ones_1col * 0
        self.static_stability.derivatives.Cdrag_r                              = ones_1col * 0         
        self.static_stability.derivatives.CX_p                                 = ones_1col * 0
        self.static_stability.derivatives.CX_q                                 = ones_1col * 0
        self.static_stability.derivatives.CX_r                                 = ones_1col * 0
        self.static_stability.derivatives.CY_p                                 = ones_1col * 0
        self.static_stability.derivatives.CY_q                                 = ones_1col * 0
        self.static_stability.derivatives.CY_r                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_p                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_q                                 = ones_1col * 0
        self.static_stability.derivatives.CZ_r                                 = ones_1col * 0
        self.static_stability.derivatives.CL_p                                 = ones_1col * 0
        self.static_stability.derivatives.CL_q                                 = ones_1col * 0
        self.static_stability.derivatives.CL_r                                 = ones_1col * 0
        self.static_stability.derivatives.CM_p                                 = ones_1col * 0
        self.static_stability.derivatives.CM_q                                 = ones_1col * 0
        self.static_stability.derivatives.CM_r                                 = ones_1col * 0
        self.static_stability.derivatives.CN_p                                 = ones_1col * 0
        self.static_stability.derivatives.CN_q                                 = ones_1col * 0
        self.static_stability.derivatives.CN_r                                 = ones_1col * 0 
                                                                               
        # dynamic stability                                                    
        self.dynamic_stability                                                 = Conditions()
        self.dynamic_stability.LongModes                                       = Conditions()
        self.dynamic_stability.LatModes                                        = Conditions()
        

        # ----------------------------------------------------------------------------------------------------------------------         
        # Freestream 
        # ----------------------------------------------------------------------------------------------------------------------    
        self.emissions                                       = Conditions()         
        
        # ----------------------------------------------------------------------------------------------------------------------         
        # Noise
        # ----------------------------------------------------------------------------------------------------------------------       
        self.noise                                            = Conditions() 

        # ----------------------------------------------------------------------------------------------------------------------         
        # Energy
        # ---------------------------------------------------------------------------------------------------------------------- 
        self.energy                                           = Conditions()
        self.energy.throttle                                  = ones_1col * 0  
        self.energy.thrust_breakdown                          = Conditions()
        self.energy.thrust_breakdown                          = Conditions()
        self.energy.thrust_force_vector                       = ones_3col * 0
        self.energy.thrust_moment_vector                      = ones_3col * 0
        self.energy.power                                     = ones_1col * 0
        self.energy.vehicle_mass_rate                         = ones_1col * 0
        
        
        # ----------------------------------------------------------------------------------------------------------------------         
        # Weights 
        # ----------------------------------------------------------------------------------------------------------------------     
        self.weights                                          = Conditions() 
        self.weights.total_mass                               = ones_1col * 0
        self.weights.total_moment_of_inertia                  = ones_3col * 0 # 3 total I(I_xx, I_yy, I_zz)? or 9(including I_xz etc)?
        self.weights.weight_breakdown                         = Conditions()
        self.weights.vehicle_mass_rate                        = ones_1col * 0