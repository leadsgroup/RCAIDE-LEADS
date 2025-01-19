# RCAIDE/Library/Mission/Common/Update/stability.py
# 
# 
# Created:  Jul 2023, M. Clarke 

import numpy as np
import RCAIDE
# ----------------------------------------------------------------------------------------------------------------------
#  Stability
# ---------------------------------------------------------------------------------------------------------------------- 
def stability(segment):
    """
    Updates vehicle stability characteristics and forces

    Parameters
    ----------
    segment : Segment
        The mission segment being analyzed

    Notes
    -----
    This function evaluates the stability model if one is defined and
    updates aerodynamic forces and moments accordingly. It handles both
    VLM and AVL stability analyses.

    **Required Segment Components**

    segment:
        analyses:
            stability : Model
                Stability analysis model
                vehicle:
                    - reference_area : float
                        Wing reference area [m²]
                    - wings.main_wing:
                        - chords.mean_aerodynamic : float
                            Mean aerodynamic chord [m]
                        - spans.projected : float
                            Projected wingspan [m]
        state.conditions:
            aerodynamics:
                coefficients:
                    - lift.total : array
                        Total lift coefficient [-]
                    - drag.total : array
                        Total drag coefficient [-]
            static_stability:
                coefficients:
                    - Y : array
                        Side force coefficient [-]
                    - L : array
                        Rolling moment coefficient [-]
                    - M : array
                        Pitching moment coefficient [-]
                    - N : array
                        Yawing moment coefficient [-]

    **Major Assumptions**
    * Valid stability model
    * Linear aerodynamics
    * Small angle approximations
    * Quasi-steady flow

    Returns
    -------
    None
        Updates segment conditions directly:
        - conditions.frames.wind.force_vector [N]
        - conditions.frames.wind.moment_vector [N·m]

    
    """   
    # unpack
    stability_model    = segment.analyses.stability
    conditions         = segment.state.conditions
     
    if stability_model != None:
        
        # check to see if results have already been calculated using the Aero analyses
        if ((type(segment.analyses.stability) == RCAIDE.Framework.Analyses.Stability.Vortex_Lattice_Method) and (type(segment.analyses.aerodynamics) == RCAIDE.Framework.Analyses.Aerodynamics.Vortex_Lattice_Method)) or \
            ((type(segment.analyses.stability) == RCAIDE.Framework.Analyses.Stability.Athena_Vortex_Lattice) and (type(segment.analyses.aerodynamics) == RCAIDE.Framework.Analyses.Aerodynamics.Athena_Vortex_Lattice)):
            pass
        else:
            Sref               = stability_model.vehicle.reference_area
            MAC                = stability_model.vehicle.wings.main_wing.chords.mean_aerodynamic
            span               = stability_model.vehicle.wings.main_wing.spans.projected
            q                  = segment.state.conditions.freestream.dynamic_pressure
            CLmax              = stability_model.settings.maximum_lift_coefficient
    
            _ = stability_model(segment)
     
            # Forces 
            CL = conditions.aerodynamics.coefficients.lift.total
            CD = conditions.aerodynamics.coefficients.drag.total
            CY = conditions.static_stability.coefficients.Y
    
            CL[q<=0.0] = 0.0
            CD[q<=0.0] = 0.0
            CL[CL>CLmax] = CLmax
            CL[CL< -CLmax] = -CLmax
    
            # dimensionalize
            F      = segment.state.ones_row(3) * 0.0
            F[:,2] = ( -CL * q * Sref )[:,0]
            F[:,1] = ( -CY * q * Sref )[:,0]
            F[:,0] = ( -CD * q * Sref )[:,0]
    
            # rewrite aerodynamic CL and CD
            conditions.aerodynamics.coefficients.lift.total  = CL
            conditions.aerodynamics.coefficients.drag.total  = CD
            conditions.frames.wind.force_vector[:,:]   = F[:,:]
    
            # -----------------------------------------------------------------
            # Moments
            # -----------------------------------------------------------------
            CM = conditions.static_stability.coefficients.M
            CL = conditions.static_stability.coefficients.L
            CN = conditions.static_stability.coefficients.N
    
            CM[q<=0.0] = 0.0
    
            # dimensionalize
            M      = segment.state.ones_row(3) * 0.0
            M[:,0] = (CL[:,0] * q[:,0] * Sref * span)
            M[:,1] = (CM[:,0] * q[:,0] * Sref * MAC)
            M[:,2] = (CN[:,0] * q[:,0] * Sref * span)
    
            # pack conditions
            conditions.frames.wind.moment_vector[:,:] = M[:,:]

    return