# RCAIDE/Library/Missions/Segments/Cruise/Constant_Speed_Constant_Altitude.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
# Package imports 
import numpy as np
 
# ----------------------------------------------------------------------------------------------------------------------
#  Initialize Conditions
# ----------------------------------------------------------------------------------------------------------------------
def initialize_conditions(segment):
    """Sets the specified conditions which are given for the segment type.

    Assumptions:
    Constant speed and constant altitude

    Source:
    N/A

    Inputs:
    segment.altitude                [meters]
    segment.distance                [meters]
    segment.speed                   [meters/second]

    Outputs:
    conditions.frames.inertial.velocity_vector  [meters/second]
    conditions.frames.inertial.position_vector  [meters]
    conditions.freestream.altitude              [meters]
    conditions.frames.inertial.time             [seconds]

    Properties Used:
    N/A
    """        
    
    # unpack 
    alt        = segment.altitude
    xf         = segment.distance
    air_speed  = segment.air_speed       
    beta       = segment.sideslip_angle
    conditions = segment.state.conditions 

    # check for initial velocity
    if air_speed is None: 
        if not segment.state.initials: raise AttributeError('airspeed not set')
        air_speed = np.linalg.norm(segment.state.initials.conditions.frames.inertial.velocity_vector[-1])
        
    # check for initial altitude
    if alt is None:
        if not segment.state.initials: raise AttributeError('altitude not set')
        alt = -1.0 * segment.state.initials.conditions.frames.inertial.position_vector[-1,2]
    
    # dimensionalize time
    v_x         = np.cos(beta)*air_speed 
    v_y         = np.sin(beta)*air_speed 
    t_initial   = conditions.frames.inertial.time[0,0]
    t_final     = xf /air_speed + t_initial
    t_nondim    = segment.state.numerics.dimensionless.control_points
    time        = t_nondim * (t_final-t_initial) + t_initial
    
    # pack
    segment.state.conditions.freestream.altitude[:,0]             = alt
    segment.state.conditions.frames.inertial.position_vector[:,2] = -alt # z points down
    segment.state.conditions.frames.inertial.velocity_vector[:,0] = v_x
    segment.state.conditions.frames.inertial.velocity_vector[:,1] = v_y
    segment.state.conditions.frames.inertial.time[:,0]            = time[:,0]