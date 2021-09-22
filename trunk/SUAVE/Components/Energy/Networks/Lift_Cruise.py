## @ingroup Components-Energy-Networks
# Lift_Cruise.py
# 
# Created:  Jan 2016, E. Botero
# Modified: Mar 2020, M. Clarke
#           Apr 2021, M. Clarke
#           Jul 2021, E. Botero
#           Jul 2021, R. Erhard
#           Aug 2021, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
from SUAVE.Core import Units, Data
from .Network import Network
from SUAVE.Components.Physical_Component import Container
from SUAVE.Methods.Power.Battery.Cell_Cycle_Models.LiNCA_cell_cycle_model      import compute_NCA_cell_state_variables 
from SUAVE.Methods.Power.Battery.Cell_Cycle_Models.LiNiMnCoO2_cell_cycle_model import compute_NMC_cell_state_variables
# ----------------------------------------------------------------------
#  Lift_Forward
# ----------------------------------------------------------------------

## @ingroup Components-Energy-Networks
class Lift_Cruise(Network):
    """ This is a complex version of battery_propeller with a battery powering propellers through
        electric motors. In this case we have 2 sets of motors at different motors that can be controlled seperately
        
        This network adds 2 extra unknowns to the mission. The first is
        a voltage, to calculate the thevenin voltage drop in the pack.
        The second is torque matching between motor and propeller.
        
        We have two inputs, the forward throttle and the lift throttle setting
        Since this is an airplane first and foremost, the "throttle" will be for forward thrust
        The new unknown will be for lift throttle, because of the assumption on throttle something needs to be done...
        Want only 1 residual on voltage
    
        Assumptions:
        For any segment using this, body angle can't be an unknown.
        
        Source:
        None
    """        
    def __defaults__(self):
        """ This sets the default values for the network to function.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            N/A
        """             
        self.lift_rotor_motors            = Container()
        self.propeller_motors             = Container()
        self.lift_rotors                  = Container()
        self.propellers                   = Container()
        self.lift_rotor_esc               = None
        self.propeller_esc                = None
        self.avionics                     = None
        self.payload                      = None
        self.battery                      = None
        self.lift_rotor_nacelle_diameter  = None
        self.propeller_nacelle_diameter   = None
        self.lift_rotor_engine_length     = None
        self.propeller_engine_length      = None
        self.number_of_lift_rotor_engines = 0
        self.number_of_propeller_engines  = 0
        self.voltage                      = None
        self.propeller_pitch_command      = 0.0
        self.lift_rotor_pitch_command     = 0.0   
        self.tag                          = 'Lift_Cruise'
        self.generative_design_minimum    = 0
        self.identical_propellers         = True
        self.identical_lift_rotors        = True
        pass
        
    def evaluate_thrust(self,state):
        """ Calculate thrust given the current state of the vehicle
    
            Assumptions:
            Caps the throttle at 110% and linearly interpolates thrust off that
    
            Source:
            N/A
    
            Inputs:
            state [state()]
    
            Outputs:
            results.thrust_force_vector       [Newtons]
            results.vehicle_mass_rate         [kg/s]
            conditions.propulsion:
                lift_rotor_rpm                [radians/sec]
                rpm _forward                  [radians/sec]
                lift_rotor_current_draw       [amps]
                propeller_current_draw        [amps]
                battery_draw                  [watts]
                battery_energy                [joules]
                voltage_open_circuit          [volts]
                voltage_under_load            [volts]
                lift_rotor_motor_torque       [N-M]
                propeller_motor_torque        [N-M]
                lift_rotor_torque             [N-M]
                propeller_torque              [N-M]
    
            Properties Used:
            Defaulted values
        """          
        
        # unpack
        conditions        = state.conditions
        numerics          = state.numerics
        lift_rotor_motors = self.lift_rotor_motors
        propeller_motors  = self.propeller_motors
        lift_rotors       = self.lift_rotors
        propellers        = self.propellers
        lift_rotor_esc    = self.lift_rotor_esc
        propeller_esc     = self.propeller_esc        
        avionics          = self.avionics
        payload           = self.payload
        battery           = self.battery
        num_lift          = self.number_of_lift_rotor_engines
        num_forward       = self.number_of_propeller_engines
        D                 = numerics.time.differentiate      
        battery_data      = battery.discharge_performance_map   
        
        #-----------------------------------------------------------------
        # SETUP BATTERIES AND ESC's
        #-----------------------------------------------------------------
        # Set battery energy
        battery.current_energy      = conditions.propulsion.battery_energy
        battery.pack_temperature    = conditions.propulsion.battery_pack_temperature
        battery.charge_throughput   = conditions.propulsion.battery_charge_throughput     
        battery.age_in_days         = conditions.propulsion.battery_age_in_days 
        discharge_flag              = conditions.propulsion.battery_discharge    
        battery.R_growth_factor     = conditions.propulsion.battery_resistance_growth_factor
        battery.E_growth_factor     = conditions.propulsion.battery_capacity_fade_factor 
        battery.max_energy          = conditions.propulsion.battery_max_aged_energy
        V_th0                       = conditions.propulsion.battery_initial_thevenin_voltage
        n_series                    = battery.pack_config.series  
        n_parallel                  = battery.pack_config.parallel
        n_total                     = n_series*n_parallel
        
        # update ambient temperature based on altitude
        battery.ambient_temperature                   = conditions.freestream.temperature   
        battery.cooling_fluid.thermal_conductivity    = conditions.freestream.thermal_conductivity
        battery.cooling_fluid.kinematic_viscosity     = conditions.freestream.kinematic_viscosity
        battery.cooling_fluid.density                 = conditions.freestream.density  
        battery.ambient_pressure                      = conditions.freestream.pressure  
        a                                             = conditions.freestream.speed_of_sound
        
        # Set battery energy
        battery.current_energy = conditions.propulsion.battery_energy  


        # --------------------------------------------------------------------------------
        # Predict Voltage and Battery Properties Depending on Battery Chemistry
        # --------------------------------------------------------------------------------  
        if type(battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            volts                            = state.unknowns.battery_voltage_under_load
            battery.battery_thevenin_voltage = 0             
            battery.temperature              = conditions.propulsion.battery_pack_temperature
            
        elif type(battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:  
            SOC       = state.unknowns.battery_state_of_charge
            T_cell    = state.unknowns.battery_cell_temperature
            V_Th_cell = state.unknowns.battery_thevenin_voltage/n_series
            
            # link temperature 
            battery.cell_temperature = T_cell     
            
            # Compute State Variables
            V_oc_cell,C_Th_cell,R_Th_cell,R_0_cell = compute_NCA_cell_state_variables(battery_data,SOC,T_cell) 
            
            dV_TH_dt =  np.dot(D,V_Th_cell)
            I_cell   = V_Th_cell/(R_Th_cell * battery.R_growth_factor)  + C_Th_cell*dV_TH_dt
            R_0_cell = R_0_cell * battery.R_growth_factor
             
            # Voltage under load
            volts =  n_series*(V_oc_cell - V_Th_cell - (I_cell  * R_0_cell)) 

        elif type(battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650: 
            SOC        = state.unknowns.battery_state_of_charge 
            T_cell     = state.unknowns.battery_cell_temperature
            I_cell     = state.unknowns.battery_current/n_parallel 
            
            # Link Temperature 
            battery.cell_temperature         = T_cell  
            battery.initial_thevenin_voltage = V_th0  
            
            # Compute State Variables
            V_ul_cell = compute_NMC_cell_state_variables(battery_data,SOC,T_cell,I_cell) 
            
            # Voltage under load
            volts     = n_series*V_ul_cell    
        
        # --------------------------------------------------------------------------------
        # Run Motor, Avionics and Systems (Discharge Model)
        # --------------------------------------------------------------------------------    
        if discharge_flag:    
                
            # ESC Voltage
            lift_rotor_esc.inputs.voltagein = volts      
            propeller_esc.inputs.voltagein  = volts 
            
            #---------------------------------------------------------------
            # EVALUATE THRUST FROM FORWARD PROPULSORS 
            #---------------------------------------------------------------
            # Throttle the voltage
            propeller_esc.voltageout(conditions) 
            
            # How many evaluations to do
            if self.identical_propellers:
                n_evals = 1
                factor  = num_forward*1
            else:
                n_evals = int(num_forward)
                factor  = 1.
            
            # Setup numbers for iteration
            total_prop_motor_current = 0.
            total_prop_thrust        = 0. * state.ones_row(3)
            total_prop_power         = 0.
            
            # Iterate over motor/props
            for ii in range(n_evals):    
                
                # Unpack the motor and props
                motor_key = list(propeller_motors.keys())[ii]
                prop_key  = list(propellers.keys())[ii]
                motor     = self.propeller_motors[motor_key]
                prop      = self.propellers[prop_key]            
            
                # link
                motor.inputs.voltage = propeller_esc.outputs.voltageout
                motor.inputs.propeller_CP = np.atleast_2d(conditions.propulsion.propeller_power_coefficient[:,ii]).T
                
                # Run the motor
                motor.omega(conditions)
                
                # link
                prop.inputs.omega         = motor.outputs.omega
                prop.inputs.pitch_command = self.propeller_pitch_command 
                
                # Run the propeller
                F_forward, Q_forward, P_forward, Cp_forward, outputs_forward, etap_forward = prop.spin(conditions)
                    
                # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
                eta                       = conditions.propulsion.throttle[:,0,None]
                P_forward[eta>1.0]        = P_forward[eta>1.0]*eta[eta>1.0]
                F_forward[eta[:,0]>1.0,:] = F_forward[eta[:,0]>1.0,:]*eta[eta[:,0]>1.0,:]  
                
                # Run the motor for current
                _, etam_prop = motor.current(conditions)
                
                # Conditions specific to this instantation of motor and propellers
                R                        = prop.tip_radius
                rpm                      = motor.outputs.omega / Units.rpm
                F_mag                    = np.atleast_2d(np.linalg.norm(F_forward, axis=1)).T
                total_prop_thrust        = total_prop_thrust + F_forward * factor
                total_prop_power         = total_prop_power  + P_forward * factor
                total_prop_motor_current = total_prop_motor_current + factor*motor.outputs.current
    
                # Pack specific outputs
                conditions.propulsion.propeller_motor_torque[:,ii]     = motor.outputs.torque[:,0]
                conditions.propulsion.propeller_torque[:,ii]           = Q_forward[:,0]
                conditions.propulsion.propeller_rpm[:,ii]              = rpm[:,0]
                conditions.propulsion.propeller_tip_mach[:,ii]         = (R*rpm[:,0]*Units.rpm)/a[:,0]
                conditions.propulsion.propeller_disc_loading[:,ii]     = (F_mag[:,0])/(np.pi*(R**2))    # N/m^2                  
                conditions.propulsion.propeller_power_loading[:,ii]    = (F_mag[:,0])/(P_forward[:,0])  # N/W  
                conditions.propulsion.propeller_efficiency[:,ii]       = etap_forward[:,0]
                conditions.propulsion.propeller_motor_efficiency[:,ii] = etam_prop[:,0]
                
                
                if n_evals==1:
                    # Append outputs to each identical propeller
                    for i,p in enumerate(propellers):
                        conditions.noise.sources.propellers[p.tag]      = outputs_forward
                else:
                    conditions.noise.sources.propellers[prop.tag]      = outputs_forward            
                
            
            # link
            propeller_esc.inputs.currentout = total_prop_motor_current
            
            # Run the esc
            propeller_esc.currentin(conditions)        
           
            #-------------------------------------------------------------------
            # EVALUATE THRUST FROM LIFT PROPULSORS 
            #-------------------------------------------------------------------
            
            # Make a new set of konditions, since there are differences for the esc and motor
            konditions                                        = SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()
            konditions._size                                  = conditions._size
            konditions.propulsion                             = Data()
            konditions.freestream                             = Data()
            konditions.frames                                 = Data()
            konditions.frames.inertial                        = Data()
            konditions.frames.body                            = Data()
            konditions.propulsion.throttle                    = conditions.propulsion.throttle_lift* 1.
            konditions.propulsion.propeller_power_coefficient = conditions.propulsion.lift_rotor_power_coefficient * 1.
            konditions.freestream.density                     = conditions.freestream.density * 1.
            konditions.freestream.velocity                    = conditions.freestream.velocity * 1.
            konditions.freestream.dynamic_viscosity           = conditions.freestream.dynamic_viscosity * 1.
            konditions.freestream.speed_of_sound              = conditions.freestream.speed_of_sound *1.
            konditions.freestream.temperature                 = conditions.freestream.temperature * 1.
            konditions.freestream.altitude                    = conditions.freestream.altitude * 1.
            konditions.frames.inertial.velocity_vector        = conditions.frames.inertial.velocity_vector *1.
            konditions.frames.body.transform_to_inertial      = conditions.frames.body.transform_to_inertial
    
            # Throttle the voltage
            lift_rotor_esc.voltageout(konditions)      
            
            # How many evaluations to do
            if self.identical_lift_rotors:
                n_evals = 1
                factor  = num_lift*1
            else:
                n_evals = int(num_lift)
                factor  = 1.
            
            # Setup numbers for iteration
            total_lift_rotor_motor_current = 0.
            total_lift_rotor_thrust        = 0. * state.ones_row(3)
            total_lift_rotor_power         = 0.        
            
            # Iterate over motor/lift_rotors
            for ii in range(n_evals):          
                
                # Unpack the motor and props
                motor_key   = list(lift_rotor_motors.keys())[ii]
                lift_rotor_key   = list(lift_rotors.keys())[ii]
                lift_rotor_motor = self.lift_rotor_motors[motor_key]
                lift_rotor       = self.lift_rotors[lift_rotor_key]            
                        
                # link
                lift_rotor_motor.inputs.voltage = lift_rotor_esc.outputs.voltageout
                lift_rotor_motor.inputs.propeller_CP = np.atleast_2d(conditions.propulsion.lift_rotor_power_coefficient[:,ii]).T
                
                # Run the motor
                lift_rotor_motor.omega(konditions)
                
                # link
                lift_rotor.inputs.omega         = lift_rotor_motor.outputs.omega
                lift_rotor.inputs.pitch_command = self.lift_rotor_pitch_command 
                lift_rotor.VTOL_flag            = state.VTOL_flag   
                
                # Run the propeller
                F_lift, Q_lift, P_lift, Cp_lift, outputs_lift, etap_lift = lift_rotor.spin(konditions)
                
                # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
                eta                       = conditions.propulsion.throttle_lift[:,0,None]
                P_lift[eta>1.0]           = P_lift[eta>1.0]*eta[eta>1.0]
                F_forward[eta[:,0]>1.0,:] = F_lift[eta[:,0]>1.0,:]*eta[eta[:,0]>1.0,:]  
                    
                
                # Run the motor for current
                _, etam_lift_rotor =lift_rotor_motor.current(konditions)  
                
                # Conditions specific to this instantation of motor and propellers
                R                              = lift_rotor.tip_radius
                rpm                            = lift_rotor_motor.outputs.omega / Units.rpm
                F_mag                          = np.atleast_2d(np.linalg.norm(F_lift, axis=1)).T
                total_lift_rotor_thrust        = total_lift_rotor_thrust + F_lift * factor
                total_lift_rotor_power         = total_lift_rotor_power  + P_lift * factor
                total_lift_rotor_motor_current = total_lift_rotor_motor_current + factor*lift_rotor_motor.outputs.current
                
                
                # Pack specific outputs
                conditions.propulsion.lift_rotor_motor_torque[:,ii]     = lift_rotor_motor.outputs.torque[:,0]
                conditions.propulsion.lift_rotor_torque[:,ii]           = Q_lift[:,0]
                conditions.propulsion.lift_rotor_rpm[:,ii]              = rpm[:,0]
                conditions.propulsion.lift_rotor_tip_mach[:,ii]         = (R*rpm[:,0]*Units.rpm)/a[:,0]
                conditions.propulsion.lift_rotor_disc_loading[:,ii]     = (F_mag[:,0])/(np.pi*(R**2))    # N/m^2                  
                conditions.propulsion.lift_rotor_power_loading[:,ii]    = (F_mag[:,0])/(P_lift[:,0])  # N/W      
                conditions.propulsion.lift_rotor_efficiency[:,ii]       = etap_lift[:,0]
                conditions.propulsion.lift_rotor_motor_efficiency[:,ii] = etam_lift_rotor[:,0]
                
                if n_evals==1:
                    # Append outputs to each identical propeller
                    for i,p in enumerate(lift_rotors):
                        conditions.noise.sources.lift_rotors[p.tag]      = outputs_lift
                else:
                    conditions.noise.sources.lift_rotors[prop.tag]      = outputs_lift            
                
                
            # link
            lift_rotor_esc.inputs.currentout =  lift_rotor_motor.outputs.current     
            
            # Run the lift_rotor esc
            lift_rotor_esc.currentin(konditions)          
            
            # Run the avionics
            avionics.power()
        
            # Run the payload
            payload.power()
            
            # Calculate avionics and payload power
            avionics_payload_power = avionics.outputs.power + payload.outputs.power
        
            # Calculate avionics and payload current
            i_avionics_payload = avionics_payload_power/volts   
            
            # Add up the power usages
            i_lift    = lift_rotor_esc.outputs.currentin
            i_forward = propeller_esc.outputs.currentin
            
            current_total = i_lift + i_forward + i_avionics_payload
            power_total   = current_total * volts   
            
            battery.inputs.current  = current_total
            battery.inputs.power_in = - power_total
            
            # Run the battery
            battery.energy_cycle_model(numerics,discharge_flag)   
    
            
        # --------------------------------------------------------------------------------
        # Run Charge Model 
        # --------------------------------------------------------------------------------               
        else:  
            # link 
            battery.inputs.current  = -battery.cell.charging_current*n_parallel * np.ones_like(volts)
            battery.inputs.voltage  =  battery.cell.charging_voltage*n_series * np.ones_like(volts)
            battery.inputs.power_in =  -battery.inputs.current * battery.inputs.voltage             
            battery.energy_cycle_model(numerics,discharge_flag)        
             
            total_prop_thrust       = np.zeros((len(volts),3))  
            total_lift_rotor_thrust = np.zeros((len(volts),3))  
            P_forward               = np.zeros((len(volts),1))  
            P_lift                  = np.zeros((len(volts),1))  
            current_total           = battery.cell.charging_current*n_parallel * np.ones_like(volts)
        
            
        # Pack the conditions for outputs 
        battery_draw = battery.inputs.power_in    
        conditions.propulsion.battery_energy                       = battery.current_energy
        conditions.propulsion.battery_voltage_open_circuit         = battery.voltage_open_circuit
        conditions.propulsion.battery_voltage_under_load           = battery.voltage_under_load 
        conditions.propulsion.battery_efficiency                   = (battery_draw+battery.resistive_losses)/battery_draw
        conditions.propulsion.payload_efficiency                   = (battery_draw+(avionics.outputs.power + payload.outputs.power))/battery_draw            
        conditions.propulsion.battery_specfic_power                = -battery_draw/battery.mass_properties.mass    # kWh/kg  
        conditions.propulsion.electronics_efficiency               = -(P_forward + P_lift)/battery_draw  
        conditions.propulsion.battery_current                      = current_total
        conditions.propulsion.battery_power_draw                   = battery.inputs.power_in 
        conditions.propulsion.battery_max_aged_energy              = battery.max_energy 
        conditions.propulsion.battery_charge_throughput            = battery.charge_throughput 
        conditions.propulsion.battery_internal_resistance          = battery.internal_resistance
        conditions.propulsion.battery_state_of_charge              = battery.state_of_charge 
        conditions.propulsion.battery_pack_temperature             = battery.pack_temperature 
        conditions.propulsion.battery_thevenin_voltage             = battery.thevenin_voltage           
        conditions.propulsion.battery_age_in_days                  = battery.age_in_days  

        conditions.propulsion.battery_cell_power_draw              = battery.inputs.power_in /n_series
        conditions.propulsion.battery_cell_energy                  = battery.current_energy/n_total   
        conditions.propulsion.battery_cell_voltage_under_load      = battery.cell_voltage_under_load    
        conditions.propulsion.battery_cell_voltage_open_circuit    = battery.cell_voltage_open_circuit  
        conditions.propulsion.battery_cell_current                 = abs(battery.cell_current)        
        conditions.propulsion.battery_cell_temperature             = battery.cell_temperature
        conditions.propulsion.battery_cell_charge_throughput       = battery.cell_charge_throughput
        conditions.propulsion.battery_cell_heat_energy_generated   = battery.heat_energy_generated
        conditions.propulsion.battery_cell_joule_heat_fraction     = battery.cell_joule_heat_fraction   
        conditions.propulsion.battery_cell_entropy_heat_fraction   = battery.cell_entropy_heat_fraction   

        F_total = total_prop_thrust + total_lift_rotor_thrust

        results = Data()
        results.thrust_force_vector = F_total
        results.vehicle_mass_rate   = state.ones_row(1)*0.0 
        return results
    
    def unpack_unknowns_transition(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses all the motors.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.lift_rotor_power_coefficient [None]
            state.unknowns.propeller_power_coefficient  [None]
            state.unknowns.battery_voltage_under_load   [volts]
            state.unknowns.throttle_lift                [0-1]
            state.unknowns.throttle                     [0-1]
    
            Outputs:
            state.conditions.propulsion.lift_rotor_power_coefficient [None]
            state.conditions.propulsion.propeller_power_coefficient  [None]
            state.conditions.propulsion.battery_voltage_under_load   [volts]
            state.conditions.propulsion.throttle_lift                [0-1]
            state.conditions.propulsion.throttle                     [0-1]
    
            Properties Used:
            N/A
        """          
        
        # unpack the ones function
        ones_row = segment.state.ones_row
        
        # Here we are going to unpack the unknowns provided for this network
        ss = segment.state
        if segment.battery_discharge: 
            ss.conditions.propulsion.lift_rotor_power_coefficient = segment.state.unknowns.lift_rotor_power_coefficient
            ss.conditions.propulsion.propeller_power_coefficient  = segment.state.unknowns.propeller_power_coefficient   
            ss.conditions.propulsion.throttle_lift                = segment.state.unknowns.throttle_lift        
            ss.conditions.propulsion.throttle                     = segment.state.unknowns.throttle  
        else:
            ss.conditions.propulsion.propeller_power_coefficientb = 0. * ones_row(1)
            
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            ss.conditions.propulsion.battery_voltage_under_load  = ss.unknowns.battery_voltage_under_load
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_current             = ss.unknowns.battery_current   
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_thevenin_voltage    = ss.unknowns.battery_thevenin_voltage   
        
        return
    
    
    def unpack_unknowns_cruise(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the forward motors and turns the rest off.
    
            Assumptions:
            Only the forward motors and turns the rest off.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift               [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift               [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """             
        
        ones_row = segment.state.ones_row 
        
        # Here we are going to unpack the unknowns provided for this network
        ss = segment.state
        if segment.battery_discharge:   
            ss.conditions.propulsion.throttle_lift                       = 0.0 * ones_row(1)
            ss.conditions.propulsion.lift_rotor_power_coefficient        = 0.0 * ones_row(1) 
            ss.conditions.propulsion.propeller_power_coefficient         = segment.state.unknowns.propeller_power_coefficient
            ss.conditions.propulsion.throttle                            = segment.state.unknowns.throttle            
        else:
            ss.conditions.propulsion.propeller_power_coefficient = 0. * ones_row(1)
            
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            ss.conditions.propulsion.battery_voltage_under_load  = ss.unknowns.battery_voltage_under_load
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_current             = ss.unknowns.battery_current   
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_thevenin_voltage    = ss.unknowns.battery_thevenin_voltage   

        
        return    
    
    def unpack_unknowns_lift(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the lift motors.
    
            Assumptions:
            Only the lift motors.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift               [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift               [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """         
        
        # unpack the ones function
        ones_row = segment.state.ones_row
        
        # Here we are going to unpack the unknowns (Cp) provided for this network
        ss = segment.state
        if segment.battery_discharge: 
            # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
            ss.conditions.propulsion.throttle_lift                = segment.state.unknowns.throttle_lift 
            ss.conditions.propulsion.lift_rotor_power_coefficient = segment.state.unknowns.lift_rotor_power_coefficient
            ss.conditions.propulsion.propeller_power_coefficient  = 0.0 * ones_row(1)
            ss.conditions.propulsion.throttle                     = 0.0 * ones_row(1)
        else:
            ss.conditions.propulsion.propeller_power_coefficient  = 0.0 * ones_row(1) 
            ss.conditions.propulsion.throttle_lift                = 0.0 * ones_row(1) 
            ss.conditions.propulsion.lift_rotor_power_coefficient = 0.0 * ones_row(1)  
            ss.conditions.propulsion.throttle                     = 0.0 * ones_row(1)
            
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            ss.conditions.propulsion.battery_voltage_under_load  = ss.unknowns.battery_voltage_under_load
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_current             = ss.unknowns.battery_current   
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            ss.conditions.propulsion.battery_cell_temperature    = ss.unknowns.battery_cell_temperature 
            ss.conditions.propulsion.battery_state_of_charge     = ss.unknowns.battery_state_of_charge
            ss.conditions.propulsion.battery_thevenin_voltage    = ss.unknowns.battery_thevenin_voltage   
                
        return    
    
    def residuals_transition(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if all motors are operational
    
            Assumptions:
            All motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                lift_rotor_motor_torque               [N-m]
                propeller_torque                      [N-m]
                lift_rotor_torque                     [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """              


        if segment.battery_discharge:  
            q_propeller_motor  = segment.state.conditions.propulsion.propeller_motor_torque
            q_prop_forward     = segment.state.conditions.propulsion.propeller_torque
            q_lift_rotor_motor = segment.state.conditions.propulsion.lift_rotor_motor_torque
            q_prop_lift        = segment.state.conditions.propulsion.lift_rotor_torque  
            segment.state.residuals.network.propellers  = (q_propeller_motor - q_prop_forward)/q_propeller_motor
            segment.state.residuals.network.lift_rotors = (q_lift_rotor_motor - q_prop_lift)/q_lift_rotor_motor 
            
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            v_actual  = segment.state.conditions.propulsion.battery_voltage_under_load
            v_predict = segment.state.unknowns.battery_voltage_under_load
            v_max     = self.voltage 
            segment.state.residuals.network.voltage  = (v_predict - v_actual)/v_max        
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:       
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            i_actual     = segment.state.conditions.propulsion.battery_current
            i_predict    = segment.state.unknowns.battery_current 
        
            # Return the residuals  
            segment.state.residuals.network.current      =  i_predict - i_actual 
            segment.state.residuals.network.SOC          =  SOC_predict - SOC_actual 
            segment.state.residuals.network.temperature  =  Temp_predict - Temp_actual 
            
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650: 
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            v_th_actual  = segment.state.conditions.propulsion.battery_thevenin_voltage
            v_th_predict = segment.state.unknowns.battery_thevenin_voltage       
        
            # Return the residuals   
            segment.state.residuals.thevenin_voltage  = v_th_predict - v_th_actual    
            segment.state.residuals.SOC               = SOC_predict - SOC_actual
            segment.state.residuals.temperature       = Temp_predict - Temp_actual
                  
        return
    
    
    def residuals_cruise(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if only the forward motors are operational
    
            Assumptions:
            Only the forward motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                lift_rotor_motor_torque               [N-m]
                propeller_torque                      [N-m]
                lift_rotor_torque                     [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
            
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """          
        
        if segment.battery_discharge:   
            q_propeller_motor = segment.state.conditions.propulsion.propeller_motor_torque
            q_prop_forward    = segment.state.conditions.propulsion.propeller_torque    
            segment.state.residuals.network.propellers = (q_propeller_motor - q_prop_forward)/q_propeller_motor 


        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            v_actual  = segment.state.conditions.propulsion.battery_voltage_under_load
            v_predict = segment.state.unknowns.battery_voltage_under_load
            v_max     = self.voltage 
            segment.state.residuals.network.voltage  = (v_predict - v_actual)/v_max        
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:       
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            i_actual     = segment.state.conditions.propulsion.battery_current
            i_predict    = segment.state.unknowns.battery_current 
        
            # Return the residuals  
            segment.state.residuals.network.current      =  i_predict - i_actual 
            segment.state.residuals.network.SOC          =  SOC_predict - SOC_actual 
            segment.state.residuals.network.temperature  =  Temp_predict - Temp_actual 
            
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650: 
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            v_th_actual  = segment.state.conditions.propulsion.battery_thevenin_voltage
            v_th_predict = segment.state.unknowns.battery_thevenin_voltage       
        
            # Return the residuals   
            segment.state.residuals.thevenin_voltage  = v_th_predict - v_th_actual    
            segment.state.residuals.SOC               = SOC_predict - SOC_actual
            segment.state.residuals.temperature       = Temp_predict - Temp_actual

        return    
    
    def residuals_lift(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Only the lift motors are operational
    
            Assumptions:
            The lift motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                lift_rotor_motor_torque               [N-m]
                propeller_torque                      [N-m]
                lift_rotor_torque                     [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """            
          
        if segment.battery_discharge:   
            q_lift_rotor_motor   = segment.state.conditions.propulsion.lift_rotor_motor_torque
            q_lift_rotor_lift    = segment.state.conditions.propulsion.lift_rotor_torque        
            segment.state.residuals.network.lift_rotors  = (q_lift_rotor_motor - q_lift_rotor_lift)/q_lift_rotor_motor


        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650:
            v_actual  = segment.state.conditions.propulsion.battery_voltage_under_load
            v_predict = segment.state.unknowns.battery_voltage_under_load
            v_max     = self.voltage 
            segment.state.residuals.network.voltage  = (v_predict - v_actual)/v_max        
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:       
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            i_actual     = segment.state.conditions.propulsion.battery_current
            i_predict    = segment.state.unknowns.battery_current 
        
            # Return the residuals  
            segment.state.residuals.network.current      =  i_predict - i_actual 
            segment.state.residuals.network.SOC          =  SOC_predict - SOC_actual 
            segment.state.residuals.network.temperature  =  Temp_predict - Temp_actual 
            
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650: 
            SOC_actual   = segment.state.conditions.propulsion.battery_state_of_charge
            SOC_predict  = segment.state.unknowns.battery_state_of_charge 
        
            Temp_actual  = segment.state.conditions.propulsion.battery_cell_temperature 
            Temp_predict = segment.state.unknowns.battery_cell_temperature   
        
            v_th_actual  = segment.state.conditions.propulsion.battery_thevenin_voltage
            v_th_predict = segment.state.unknowns.battery_thevenin_voltage       
        
            # Return the residuals   
            segment.state.residuals.thevenin_voltage  = v_th_predict - v_th_actual    
            segment.state.residuals.SOC               = SOC_predict - SOC_actual
            segment.state.residuals.temperature       = Temp_predict - Temp_actual
            
        return
    
    
    def add_transition_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None, 
                                                         initial_prop_power_coefficient = 0.005,
                                                         initial_lift_rotor_power_coefficient = 0.005,
                                                         initial_throttle_lift = 0.9,
                                                         initial_battery_cell_temperature = 283. ,
                                                         initial_battery_state_of_charge = 0.5,
                                                         initial_battery_cell_current = 5. ,
                                                         initial_battery_cell_thevenin_voltage= 0.1):
        """ This function sets up the information that the mission needs to run a mission segment using this network
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s
            
            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   
    
            Properties Used:
            N/A
        """           
        
        # unpack the ones function
        ones_row = segment.state.ones_row 
        
        # Count how many unknowns and residuals based on p
        n_props       = len(self.propellers)
        n_lift_rotors = len(self.lift_rotors)
        n_motors_p    = len(self.propeller_motors)
        n_motors_r    = len(self.lift_rotor_motors)
        n_eng_p       = self.number_of_propeller_engines
        n_eng_r       = self.number_of_lift_rotor_engines

        
        if n_props!=n_motors_p!=n_eng_p:
            assert('The number of propellers is not the same as the number of motors')
            
        if n_lift_rotors!=n_motors_r!=n_eng_r:
            assert('The number of lift_rotors is not the same as the number of motors')
            
        # Now check if the props/lift_rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)
            
        if self.identical_lift_rotors:
            n_lift_rotors = 1
        else:
            self.number_of_lift_rotor_engines = int(self.number_of_lift_rotor_engines)
        
        # Setup the residuals
        segment.state.residuals.network = Data()        
        
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650: 
            if initial_voltage==None:
                initial_voltage = self.battery.max_voltage
                
            segment.state.residuals.network.voltage             = 0. * ones_row(1)
            segment.state.unknowns.battery_voltage_under_load   = initial_voltage * ones_row(1)
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:  
            parallel                                           = self.battery.pack_config.parallel            
            segment.state.unknowns.battery_state_of_charge     = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature    = initial_battery_cell_temperature  * ones_row(n_props) 
            segment.state.unknowns.battery_current             = initial_battery_cell_current*parallel * ones_row(n_props) 
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            series                                              = self.battery.pack_config.series       
            segment.state.unknowns.battery_state_of_charge      = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature     = initial_battery_cell_temperature  * ones_row(n_props)       
            segment.state.unknowns.battery_thevenin_voltage     = initial_battery_cell_thevenin_voltage*series  * ones_row(n_props)
    
        if segment.battery_discharge:  
            segment.state.residuals.network.propellers          = 0. * ones_row(n_props)
            segment.state.residuals.network.lift_rotors         = 0. * ones_row(n_lift_rotors)
            segment.state.unknowns.throttle_lift                = initial_throttle_lift           * ones_row(1)   
            segment.state.unknowns.propeller_power_coefficient  = initial_prop_power_coefficient  * ones_row(n_props)
            segment.state.unknowns.lift_rotor_power_coefficient = initial_lift_rotor_power_coefficient * ones_row(n_lift_rotors)
        
        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque     = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque           = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm              = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading     = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading    = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach         = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_efficiency       = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_motor_efficiency = 0. * ones_row(n_props)

        # Setup the conditions for the lift_rotors
        segment.state.conditions.propulsion.lift_rotor_motor_torque      = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_torque            = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_rpm               = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_disc_loading      = 0. * ones_row(n_lift_rotors)                 
        segment.state.conditions.propulsion.lift_rotor_power_loading     = 0. * ones_row(n_lift_rotors)        
        segment.state.conditions.propulsion.lift_rotor_tip_mach          = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_efficiency        = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_motor_efficiency  = 0. * ones_row(n_lift_rotors)
        
        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_transition
        segment.process.iterate.residuals.network = self.residuals_transition      

        return segment
    
    
    def add_cruise_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None, 
                                                         initial_prop_power_coefficient = 0.005,
                                                         initial_battery_cell_temperature = 283.,
                                                         initial_battery_state_of_charge = 0.5,
                                                         initial_battery_cell_current = 5. ,
                                                         initial_battery_cell_thevenin_voltage= 0.1):
        """ This function sets up the information that the mission needs to run a mission segment using this network
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s
            
            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   
    
            Properties Used:
            N/A
        """           
        
        # unpack the ones function
        ones_row = segment.state.ones_row 
        
        # Count how many unknowns and residuals based on p
        n_props    = len(self.propellers)
        n_motors_p = len(self.propeller_motors)
        n_eng_p    = self.number_of_propeller_engines
        
        if n_props!=n_motors_p!=n_eng_p:
            assert('The number of propellers is not the same as the number of motors')
            
        # Now check if the props/lift_rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)
            
        if self.identical_lift_rotors:
            n_lift_rotors = 1
        else:
            self.number_of_lift_rotor_engines = int(self.number_of_lift_rotor_engines)
        
        # Setup the residuals
        segment.state.residuals.network            = Data() 
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650: 
            if initial_voltage==None:
                initial_voltage = self.battery.max_voltage
                
            segment.state.residuals.network.voltage             = 0. * ones_row(1)
            segment.state.unknowns.battery_voltage_under_load   = initial_voltage * ones_row(1)
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:  
            parallel                                           = self.battery.pack_config.parallel            
            segment.state.unknowns.battery_state_of_charge     = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature    = initial_battery_cell_temperature  * ones_row(n_props) 
            segment.state.unknowns.battery_current             = initial_battery_cell_current*parallel * ones_row(n_props) 
            
        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            series                                              = self.battery.pack_config.series       
            segment.state.unknowns.battery_state_of_charge      = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature     = initial_battery_cell_temperature  * ones_row(n_props)       
            segment.state.unknowns.battery_thevenin_voltage     = initial_battery_cell_thevenin_voltage*series  * ones_row(n_props)
        
        if segment.battery_discharge:    
            segment.state.residuals.network.propellers         = 0. * ones_row(n_props)
            segment.state.unknowns.propeller_power_coefficient = initial_prop_power_coefficient * ones_row(n_props)
        
        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque     = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque           = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm              = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading     = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading    = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach         = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_efficiency       = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_motor_efficiency = 0. * ones_row(n_props)
        
        # Setup the conditions for the lift_rotors
        segment.state.conditions.propulsion.lift_rotor_motor_torque      = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_torque            = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_rpm               = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_disc_loading      = 0. * ones_row(n_lift_rotors)                 
        segment.state.conditions.propulsion.lift_rotor_power_loading     = 0. * ones_row(n_lift_rotors)        
        segment.state.conditions.propulsion.lift_rotor_tip_mach          = 0. * ones_row(n_lift_rotors)       
        segment.state.conditions.propulsion.lift_rotor_efficiency        = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_motor_efficiency  = 0. * ones_row(n_lift_rotors)

        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_cruise
        segment.process.iterate.residuals.network = self.residuals_cruise     

        return segment
    
    
    def add_lift_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None,
                                                   initial_lift_rotor_power_coefficient = 0.005,
                                                         initial_throttle_lift = 0.9,
                                                         initial_battery_cell_temperature = 283.,
                                                         initial_battery_state_of_charge = 0.5,
                                                         initial_battery_cell_current = 5. ,
                                                         initial_battery_cell_thevenin_voltage= 0.1):
        """ This function sets up the information that the mission needs to run a mission segment using this network

            Assumptions:
            None

            Source:
            N/A

            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s

            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   

            Properties Used:
            N/A
        """           

        # unpack the ones function
        ones_row = segment.state.ones_row

        # unpack the initial values if the user doesn't specify
        if initial_voltage==None:
            initial_voltage = self.battery.max_voltage

        # Count how many unknowns and residuals based on p
        n_lift_rotors   = len(self.lift_rotors)
        n_motors_r = len(self.lift_rotor_motors)
        n_eng_r    = self.number_of_lift_rotor_engines

        if n_lift_rotors!=n_motors_r!=n_eng_r:
            assert('The number of lift_rotors is not the same as the number of motors')

        # Now check if the props/lift_rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)

        if self.identical_lift_rotors:
            n_lift_rotors = 1
        else:
            self.number_of_lift_rotor_engines = int(self.number_of_lift_rotor_engines)

        # Setup the residuals
        segment.state.residuals.network  = Data()    
        if type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiFePO4_18650: 
            if initial_voltage==None:
                initial_voltage = self.battery.max_voltage

            segment.state.residuals.network.voltage             = 0. * ones_row(1)
            segment.state.unknowns.battery_voltage_under_load   = initial_voltage * ones_row(1)

        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNiMnCoO2_18650:  
            parallel                                           = self.battery.pack_config.parallel            
            segment.state.unknowns.battery_state_of_charge     = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature    = initial_battery_cell_temperature  * ones_row(n_props) 
            segment.state.unknowns.battery_current             = initial_battery_cell_current*parallel * ones_row(n_props) 

        elif type(self.battery) == SUAVE.Components.Energy.Storages.Batteries.Constant_Mass.Lithium_Ion_LiNCA_18650:   
            series                                              = self.battery.pack_config.series       
            segment.state.unknowns.battery_state_of_charge      = initial_battery_state_of_charge   * ones_row(n_props)  
            segment.state.unknowns.battery_cell_temperature     = initial_battery_cell_temperature  * ones_row(n_props)       
            segment.state.unknowns.battery_thevenin_voltage     = initial_battery_cell_thevenin_voltage*series  * ones_row(n_props)

        if segment.battery_discharge:        
            segment.state.residuals.network.lift_rotors = 0. * ones_row(n_lift_rotors) 
            segment.state.unknowns.__delitem__('throttle')
            segment.state.unknowns.throttle_lift                = initial_throttle_lift           * ones_row(1) 
            segment.state.unknowns.lift_rotor_power_coefficient = initial_lift_rotor_power_coefficient * ones_row(n_lift_rotors)

        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque     = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque           = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm              = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading     = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading    = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach         = 0. * ones_row(n_props)   
        segment.state.conditions.propulsion.propeller_efficiency       = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_motor_efficiency = 0. * ones_row(n_props)

        # Setup the conditions for the lift_rotors
        segment.state.conditions.propulsion.lift_rotor_motor_torque      = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_torque            = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_rpm               = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_disc_loading      = 0. * ones_row(n_lift_rotors)                 
        segment.state.conditions.propulsion.lift_rotor_power_loading     = 0. * ones_row(n_lift_rotors)        
        segment.state.conditions.propulsion.lift_rotor_tip_mach          = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_efficiency        = 0. * ones_row(n_lift_rotors)
        segment.state.conditions.propulsion.lift_rotor_motor_efficiency  = 0. * ones_row(n_lift_rotors)

        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_lift
        segment.process.iterate.residuals.network = self.residuals_lift 

        return segment      