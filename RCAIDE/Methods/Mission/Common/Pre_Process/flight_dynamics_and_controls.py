## @ingroup Methods-Missions-Segments-Common-Pre_Process
# RCAIDE/Methods/Missions/Common/Pre_Process/flight_dynamics_and_controls.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 

# ----------------------------------------------------------------------------------------------------------------------
#  flight_dynamics_and_controls
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Methods-Missions-Segments-Common-Pre_Process
def flight_dynamics_and_controls(mission):
    """ Sets the flight dynamics residuals and fligth controls of the aircraft   

        Assumptions:
        N/A

        Inputs: 
            mission     - data structure of mission  [-]
 
        Outputs:  

        Properties Used:
        N/A

    """     
    for segment in mission.segments:  
        ones_row = segment.state.ones_row 
        ctrls    = segment.flight_controls
        dynamics = segment.flight_dynamics
        
        # assign force and moment residuals i.e. degrees of freedom 
        num_DOF  = 0      
        if dynamics.force_x == True:
            segment.state.residuals.force_x = ones_row(1) *0 
            num_DOF += 1 
        if dynamics.force_y == True:
            segment.state.residuals.force_y = ones_row(1) *0
            num_DOF += 1  
        if dynamics.force_z == True:
            segment.state.residuals.force_z = ones_row(1) *0
            num_DOF += 1  
        if dynamics.moment_x == True:
            segment.state.residuals.moment_x = ones_row(1) *0
            num_DOF += 1  
        if dynamics.moment_y == True:
            segment.state.residuals.moment_y = ones_row(1) *0 
            num_DOF += 1 
        if dynamics.moment_z == True:
            segment.state.residuals.moment_z = ones_row(1) *0
            num_DOF += 1  
        
        # assign control variables   
        ones_row     = segment.state.ones_row 
        num_ctrls    = 0 
        # Body Angle Control
        if ctrls.body_angle.active:
            segment.state.unknowns.body_angle = ones_row(1) * ctrls.body_angle.initial_values[0][0]       
            num_ctrls += 1 
                
        # Wing Angle Control
        if ctrls.wind_angle.active:
            segment.state.unknowns.wind_angle = ones_row(1) * ctrls.wind_angle.initial_values[0][0] 
            num_ctrls += 1           
            
        # Throttle Control
        if ctrls.throttle.active: 
            for i in range(len(ctrls.throttle.assigned_propulsors)):   
                segment.state.unknowns["throttle_" + str(i)] = ones_row(1) * ctrls.throttle.initial_values[i][0] 
                num_ctrls += 1      
                     
        # Elevator Control
        if ctrls.elevator_deflection.active:  
            for i in range(len(ctrls.elevator_deflection.assigned_propulsors)):   
                segment.state.unknowns["elevator_" + str(i)] = ones_row(1) * ctrls.elevator_deflection.initial_values[i][0]
                num_ctrls += 1   
                    
        # Flap Control
        if ctrls.flap_deflection.active:  
            for i in range(len(ctrls.flap_deflection.assigned_propulsors)):   
                segment.state.unknowns["flap_" + str(i)] = ones_row(1) * ctrls.flap_deflection.initial_values[i][0]
                num_ctrls += 1    
                
        # Aileron Control
        if ctrls.aileron_deflection.active:  
            for i in range(len(ctrls.aileron_deflection.assigned_propulsors)):   
                segment.state.unknowns["aileron_" + str(i)] = ones_row(1) * ctrls.aileron_deflection.initial_values[i][0]  
                num_ctrls += 1       
            
        # Thrust Control
        if ctrls.thrust_vector_angle.active:  
            for i in range(len(ctrls.thrust_vector_angle.assigned_propulsors)):   
                segment.state.unknowns["thrust_" + str(i)] = ones_row(1) * ctrls.thrust_vector_angle.initial_values[i][0]
                num_ctrls += 1       
            
        # Blade Pitch Control
        if ctrls.blade_pitch_angle.active:  
            for i in range(ctrls.blade_pitch_angle.assigned_propulsors):   
                segment.state.unknowns["blade_pitch_angle_" + str(i)] = ones_row(1) * ctrls.blade_pitch_angle.initial_values[i][0]
                num_ctrls += 1      
                                                                                      
        # RPM Control
        if ctrls.RPM.active:  
            for i in range(len(ctrls.RPM.assigned_propulsors) ):   
                segment.state.unknowns["rpm_" + str(i)] = ones_row(1) * ctrls.RPM.initial_values[i][0]
                num_ctrls += 1
                
                
        # if the degrees of freedom are greater than the number of control inputs, post problem at optimization  # TO DO
                                                                                                                                                                