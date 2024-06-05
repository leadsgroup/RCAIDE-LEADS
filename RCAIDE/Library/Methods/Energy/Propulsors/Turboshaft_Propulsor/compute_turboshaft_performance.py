## @ingroup Methods-Energy-Propulsors-Networks-turboshaft_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Networks/turboshaft_Propulsor/compute_turboshaft_performance.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE imports  
from RCAIDE.Framework.Core import Data    
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Ram                import compute_ram_performance
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Combustor          import compute_combustor_performance
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Compressor         import compute_compressor_performance
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Turbine            import compute_turbine_performance
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Expansion_Nozzle   import compute_expansion_nozzle_performance 
from RCAIDE.Library.Methods.Energy.Propulsors.Converters.Compression_Nozzle import compute_compression_nozzle_performance
from RCAIDE.Library.Methods.Energy.Propulsors.turboshaft_Propulsor            import compute_thrust

# ----------------------------------------------------------------------------------------------------------------------
# compute_turboshaft_performance
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Methods-Energy-Propulsors-Turboshaft_Propulsor
def compute_turboshaft_performance(fuel_line,state):   
    ''' Computes the performance of all turboshaft engines connected to a fuel tank
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:   
    fuel_line            - data structure containing turbofans on distrubution network  [-]  
    assigned_propulsors  - list of propulsors that are powered by energy source         [-]
    state                - operating data structure                                     [-] 
                     
    Outputs:                      
    outputs              - turboshaft operating outputs                                   [-]
    total_thrust         - thrust of turboshafts                                          [N]
    total_power          - power of turboshafts                                           [W]
    
    Properties Used: 
    N.A.        
    '''  
    total_power     = 0*state.ones_row(1) 
    total_thrust    = 0*state.ones_row(3) 
    conditions      = state.conditions
    stored_results_flag = False 
    
    for turboshaft in fuel_line.propulsors:  
        if turboshaft.active == True:  
            if fuel_line.identical_propulsors == False:
                # run analysis  
                total_thrust,total_power ,stored_results_flag,stored_propulsor_tag = compute_performance(conditions,fuel_line,turboshaft,total_thrust,total_power)
            else:             
                if stored_results_flag == False: 
                    # run analysis 
                    total_thrust,total_power ,stored_results_flag,stored_propulsor_tag = compute_performance(conditions,fuel_line,turboshaft,total_thrust,total_power)
                else:
                    # use old results 
                    total_thrust,total_power  = reuse_stored_data(conditions,fuel_line,turboshaft,stored_propulsor_tag,total_thrust,total_power)
                
    return total_thrust,total_power

def compute_performance(conditions,fuel_line,turboshaft,total_thrust,total_power):  
    ''' Computes the perfomrance of one turboshaft
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:  
    conditions           - operating conditions data structure   [-]  
    fuel_line            - fuelline                              [-] 
    turboshaft             - turboshaft data structure               [-] 
    total_thrust         - thrust of turboshaft group              [N]
    total_power          - power of turboshaft group               [W] 

    Outputs:  
    total_thrust         - thrust of turboshaft group              [N]
    total_power          - power of turboshaft group               [W] 
    stored_results_flag  - boolean for stored results            [-]     
    stored_propulsor_tag - name of turboshaft with stored results  [-]
    
    Properties Used: 
    N.A.        
    ''' 
    noise_results             = conditions.noise[fuel_line.tag][turboshaft.tag]  
    turboshaft_results          = conditions.energy[fuel_line.tag][turboshaft.tag]  
    ram                       = turboshaft.ram
    inlet_nozzle              = turboshaft.inlet_nozzle
    low_pressure_compressor   = turboshaft.low_pressure_compressor
    high_pressure_compressor  = turboshaft.high_pressure_compressor
    combustor                 = turboshaft.combustor
    high_pressure_turbine     = turboshaft.high_pressure_turbine
    low_pressure_turbine      = turboshaft.low_pressure_turbine 
    afterburner               = turboshaft.afterburner 
    core_nozzle               = turboshaft.core_nozzle  

    #set the working fluid to determine the fluid properties
    ram.inputs.working_fluid                               = turboshaft.working_fluid

    #Flow through the ram , this computes the necessary flow quantities and stores it into conditions
    compute_ram_performance(ram,conditions)

    #link inlet nozzle to ram 
    inlet_nozzle.inputs.stagnation_temperature             = ram.outputs.stagnation_temperature 
    inlet_nozzle.inputs.stagnation_pressure                = ram.outputs.stagnation_pressure

    #Flow through the inlet nozzle
    compute_compression_nozzle_performance(inlet_nozzle,conditions)

    #--link low pressure compressor to the inlet nozzle
    low_pressure_compressor.inputs.stagnation_temperature  = inlet_nozzle.outputs.stagnation_temperature
    low_pressure_compressor.inputs.stagnation_pressure     = inlet_nozzle.outputs.stagnation_pressure

    #Flow through the low pressure compressor
    compute_compressor_performance(low_pressure_compressor,conditions)

    #link the high pressure compressor to the low pressure compressor
    high_pressure_compressor.inputs.stagnation_temperature = low_pressure_compressor.outputs.stagnation_temperature
    high_pressure_compressor.inputs.stagnation_pressure    = low_pressure_compressor.outputs.stagnation_pressure

    #Flow through the high pressure compressor
    compute_compressor_performance(high_pressure_compressor,conditions)

    #link the combustor to the high pressure compressor
    combustor.inputs.stagnation_temperature                = high_pressure_compressor.outputs.stagnation_temperature
    combustor.inputs.stagnation_pressure                   = high_pressure_compressor.outputs.stagnation_pressure

    #flow through the high pressor comprresor
    compute_combustor_performance(combustor,conditions)

    #link the high pressure turbine to the combustor
    high_pressure_turbine.inputs.stagnation_temperature    = combustor.outputs.stagnation_temperature
    high_pressure_turbine.inputs.stagnation_pressure       = combustor.outputs.stagnation_pressure
    high_pressure_turbine.inputs.fuel_to_air_ratio         = combustor.outputs.fuel_to_air_ratio

    #link the high pressuer turbine to the high pressure compressor
    high_pressure_turbine.inputs.compressor                = high_pressure_compressor.outputs

    #flow through the high pressure turbine
    compute_turbine_performance(high_pressure_turbine,conditions)

    #link the low pressure turbine to the high pressure turbine
    low_pressure_turbine.inputs.stagnation_temperature     = high_pressure_turbine.outputs.stagnation_temperature
    low_pressure_turbine.inputs.stagnation_pressure        = high_pressure_turbine.outputs.stagnation_pressure

    #link the low pressure turbine to the low_pressure_compresor
    low_pressure_turbine.inputs.compressor                 = low_pressure_compressor.outputs

    #link the low pressure turbine to the combustor
    low_pressure_turbine.inputs.fuel_to_air_ratio          = combustor.outputs.fuel_to_air_ratio

    #get the bypass ratio from the thrust component
    low_pressure_turbine.inputs.bypass_ratio               = 0.0

    #flow through the low pressure turbine
    compute_turbine_performance(low_pressure_turbine,conditions)

    if turboshaft.afterburner_active == True:
        #link the core nozzle to the afterburner
        afterburner.inputs.stagnation_temperature              = low_pressure_turbine.outputs.stagnation_temperature
        afterburner.inputs.stagnation_pressure                 = low_pressure_turbine.outputs.stagnation_pressure   
        afterburner.inputs.nondim_ratio                        = 1.0 + combustor.outputs.fuel_to_air_ratio

        #flow through the afterburner
        compute_combustor_performance(afterburner,conditions)  

        #link the core nozzle to the afterburner
        core_nozzle.inputs.stagnation_temperature              = afterburner.outputs.stagnation_temperature
        core_nozzle.inputs.stagnation_pressure                 = afterburner.outputs.stagnation_pressure   

    else:
        #link the core nozzle to the low pressure turbine
        core_nozzle.inputs.stagnation_temperature              = low_pressure_turbine.outputs.stagnation_temperature
        core_nozzle.inputs.stagnation_pressure                 = low_pressure_turbine.outputs.stagnation_pressure

    #flow through the core nozzle
    compute_expansion_nozzle_performance(core_nozzle,conditions)

    # compute the thrust using the thrust component
    #link the thrust component to the core nozzle
    turboshaft.inputs.core_exit_velocity                       = core_nozzle.outputs.velocity
    turboshaft.inputs.core_area_ratio                          = core_nozzle.outputs.area_ratio
    turboshaft.inputs.core_nozzle                              = core_nozzle.outputs

    #link the thrust component to the combustor
    turboshaft.inputs.fuel_to_air_ratio                        = combustor.outputs.fuel_to_air_ratio 
    if turboshaft.afterburner_active == True:
        # previous fuel ratio is neglected when the afterburner fuel ratio is calculated
        turboshaft.inputs.fuel_to_air_ratio += afterburner.outputs.fuel_to_air_ratio

    #link the thrust component to the low pressure compressor 
    turboshaft.inputs.total_temperature_reference              = low_pressure_compressor.outputs.stagnation_temperature
    turboshaft.inputs.total_pressure_reference                 = low_pressure_compressor.outputs.stagnation_pressure 
    turboshaft.inputs.flow_through_core                        =  1.0 #scaled constant to turn on core thrust computation
    turboshaft.inputs.flow_through_fan                         =  0.0 #scaled constant to turn on fan thrust computation        

    #compute the thrust
    compute_thrust(turboshaft,conditions,throttle = turboshaft_results.throttle )

    # getting the network outputs from the thrust outputs  
    turboshaft_results.thrust          = turboshaft.outputs.thrust
    turboshaft_results.power           = turboshaft.outputs.power  
    turboshaft_results.fuel_flow_rate  = turboshaft.outputs.fuel_flow_rate 
    total_power                      += turboshaft_results.power
    total_thrust[:,0]                += turboshaft_results.thrust[:,0]

    # store data
    core_nozzle_res = Data(
                exit_static_temperature             = core_nozzle.outputs.static_temperature,
                exit_static_pressure                = core_nozzle.outputs.static_pressure,
                exit_stagnation_temperature         = core_nozzle.outputs.stagnation_temperature,
                exit_stagnation_pressure            = core_nozzle.outputs.static_pressure,
                exit_velocity                       = core_nozzle.outputs.velocity
            ) 

    noise_results.turboshaft.fan_nozzle    = None 
    noise_results.turboshaft.core_nozzle   = core_nozzle_res
    noise_results.turboshaft.fan           = None   
    stored_results_flag                  = True
    stored_propulsor_tag                 = turboshaft.tag
    
    return total_thrust,total_power ,stored_results_flag,stored_propulsor_tag

def reuse_stored_data(conditions,fuel_line,turboshaft,stored_propulsor_tag,total_thrust,total_power):
    '''Reuses results from one turboshaft for identical propulsors
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:  
    conditions           - operating conditions data structure   [-]  
    fuel_line            - fuelline                              [-] 
    turboshaft            - turboshaft data structure                [-] 
    total_thrust         - thrust of turboshaft group              [N]
    total_power          - power of turboshaft group               [W] 

    Outputs:  
    total_thrust         - thrust of turboshaft group              [N]
    total_power          - power of turboshaft group               [W] 
    
    Properties Used: 
    N.A.        
    ''' 
    turboshaft_results_0                   = conditions.energy[fuel_line.tag][stored_propulsor_tag]
    noise_results_0                      = conditions.noise[fuel_line.tag][stored_propulsor_tag] 
    turboshaft_results                     = conditions.energy[fuel_line.tag][turboshaft.tag]  
    noise_results                        = conditions.noise[fuel_line.tag][turboshaft.tag]  
    turboshaft_results.thrust              = turboshaft_results_0.thrust 
    turboshaft_results.power               = turboshaft_results_0.power   
    noise_results.turboshaft.fan_nozzle    = None  
    noise_results.turboshaft.core_nozzle   = noise_results_0.turboshaft.core_nozzle 
    noise_results.turboshaft.fan           = None   
    total_power                          += turboshaft_results.power
    total_thrust[:,0]                    += turboshaft_results.thrust[:,0]
 
    return total_thrust,total_power