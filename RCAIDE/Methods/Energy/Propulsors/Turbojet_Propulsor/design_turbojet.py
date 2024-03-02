## @ingroup Methods-Energy-Propulsors-Turbojet_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Turbojet_Propulsor/design_turbojet.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  

# RCAIDE Imports     
import RCAIDE
from RCAIDE.Core import Data
from RCAIDE.Methods.Energy.Propulsors.Converters.Ram                import compute_ram_performance
from RCAIDE.Methods.Energy.Propulsors.Converters.Combustor          import compute_combustor_performance
from RCAIDE.Methods.Energy.Propulsors.Converters.Compressor         import compute_compressor_performance
from RCAIDE.Methods.Energy.Propulsors.Converters.Turbine            import compute_turbine_performance
from RCAIDE.Methods.Energy.Propulsors.Converters.Expansion_Nozzle   import compute_expansion_nozzle_performance 
from RCAIDE.Methods.Energy.Propulsors.Converters.Compression_Nozzle import compute_compression_nozzle_performance
from RCAIDE.Methods.Energy.Propulsors.Turbojet_Propulsor            import size_core, compute_thrust

# Python package imports   
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------  
#  Design Turbojet
# ----------------------------------------------------------------------------------------------------------------------   
## @ingroup Methods-Energy-Propulsors-Turbojet_Propulsor
def design_turbojet(turbojet):  
    #check if mach number and temperature are passed
    if(turbojet.design_mach_number==None or turbojet.design_altitude==None):
        
        #raise an error
        raise NameError('The sizing conditions require an altitude and a Mach number')
    
    else:
        #call the atmospheric model to get the conditions at the specified altitude
        atmosphere = RCAIDE.Analyses.Atmospheric.US_Standard_1976()
        atmo_data  = atmosphere.compute_values(turbojet.design_altitude,turbojet.design_isa_deviation)
        planet     = RCAIDE.Attributes.Planets.Earth()
        
        p   = atmo_data.pressure          
        T   = atmo_data.temperature       
        rho = atmo_data.density          
        a   = atmo_data.speed_of_sound    
        mu  = atmo_data.dynamic_viscosity   
    
        # setup conditions
        conditions = RCAIDE.Analyses.Mission.Common.Results()
    
        # freestream conditions    
        conditions.freestream.altitude                    = np.atleast_1d(turbojet.design_altitude)
        conditions.freestream.mach_number                 = np.atleast_1d(turbojet.design_mach_number)
        conditions.freestream.pressure                    = np.atleast_1d(p)
        conditions.freestream.temperature                 = np.atleast_1d(T)
        conditions.freestream.density                     = np.atleast_1d(rho)
        conditions.freestream.dynamic_viscosity           = np.atleast_1d(mu)
        conditions.freestream.gravity                     = np.atleast_1d(planet.compute_gravity(turbojet.design_altitude))
        conditions.freestream.isentropic_expansion_factor = np.atleast_1d(turbojet.working_fluid.compute_gamma(T,p))
        conditions.freestream.Cp                          = np.atleast_1d(turbojet.working_fluid.compute_cp(T,p))
        conditions.freestream.R                           = np.atleast_1d(turbojet.working_fluid.gas_specific_constant)
        conditions.freestream.speed_of_sound              = np.atleast_1d(a)
        conditions.freestream.velocity                    = np.atleast_1d(a*turbojet.design_mach_number)
         
    ram                       = turbojet.ram
    inlet_nozzle              = turbojet.inlet_nozzle
    low_pressure_compressor   = turbojet.low_pressure_compressor
    high_pressure_compressor  = turbojet.high_pressure_compressor
    combustor                 = turbojet.combustor
    high_pressure_turbine     = turbojet.high_pressure_turbine
    low_pressure_turbine      = turbojet.low_pressure_turbine
    core_nozzle               = turbojet.core_nozzle  
    
    # Creating the network by manually linking the different components
    
    # set the working fluid to determine the fluid properties
    ram.inputs.working_fluid                             = turbojet.working_fluid
    
     #Flow through the ram , this computes the necessary flow quantities and stores it into conditions
    compute_ram_performance(ram,conditions)
    
    # link inlet nozzle to ram 
    inlet_nozzle.inputs.stagnation_temperature             = ram.outputs.stagnation_temperature #conditions.freestream.stagnation_temperature
    inlet_nozzle.inputs.stagnation_pressure                = ram.outputs.stagnation_pressure #conditions.freestream.stagnation_pressure
    
    # Flow through the inlet nozzle
    compute_compression_nozzle_performance(inlet_nozzle,conditions)
                    
    # link low pressure compressor to the inlet nozzle
    low_pressure_compressor.inputs.stagnation_temperature  = inlet_nozzle.outputs.stagnation_temperature
    low_pressure_compressor.inputs.stagnation_pressure     = inlet_nozzle.outputs.stagnation_pressure
    
    # Flow through the low pressure compressor
    compute_compressor_performance(low_pressure_compressor,conditions)

    # link the high pressure compressor to the low pressure compressor
    high_pressure_compressor.inputs.stagnation_temperature = low_pressure_compressor.outputs.stagnation_temperature
    high_pressure_compressor.inputs.stagnation_pressure    = low_pressure_compressor.outputs.stagnation_pressure
    
    # Flow through the high pressure compressor
    compute_compressor_performance(high_pressure_compressor,conditions)

    # link the combustor to the high pressure compressor
    combustor.inputs.stagnation_temperature                = high_pressure_compressor.outputs.stagnation_temperature
    combustor.inputs.stagnation_pressure                   = high_pressure_compressor.outputs.stagnation_pressure
    
    # flow through the high pressor comprresor
    compute_combustor_performance(combustor,conditions)

    #link the high pressure turbione to the combustor
    high_pressure_turbine.inputs.stagnation_temperature    = combustor.outputs.stagnation_temperature
    high_pressure_turbine.inputs.stagnation_pressure       = combustor.outputs.stagnation_pressure
    high_pressure_turbine.inputs.fuel_to_air_ratio         = combustor.outputs.fuel_to_air_ratio 
    high_pressure_turbine.inputs.compressor                = high_pressure_compressor.outputs 
    high_pressure_turbine.inputs.bypass_ratio              = 0.0
    high_pressure_turbine.inputs.fan                       = Data()
    high_pressure_turbine.inputs.fan.work_done             = 0.0
    compute_turbine_performance(high_pressure_turbine,conditions)
            
    #link the low pressure turbine to the high pressure turbine
    low_pressure_turbine.inputs.stagnation_temperature     = high_pressure_turbine.outputs.stagnation_temperature
    low_pressure_turbine.inputs.stagnation_pressure        = high_pressure_turbine.outputs.stagnation_pressure
    
    #link the low pressure turbine to the low_pressure_compresor
    low_pressure_turbine.inputs.compressor                 = low_pressure_compressor.outputs
    
    #link the low pressure turbine to the combustor
    low_pressure_turbine.inputs.fuel_to_air_ratio          = combustor.outputs.fuel_to_air_ratio
    
    #flow through the low pressure turbine
    low_pressure_turbine.inputs.bypass_ratio               = 0.0
    low_pressure_turbine.inputs.fan                        = Data()
    low_pressure_turbine.inputs.fan.work_done              = 0.0    
    compute_turbine_performance(low_pressure_turbine,conditions)
    
    #link the core nozzle to the low pressure turbine
    core_nozzle.inputs.stagnation_temperature              = low_pressure_turbine.outputs.stagnation_temperature
    core_nozzle.inputs.stagnation_pressure                 = low_pressure_turbine.outputs.stagnation_pressure
    
    #flow through the core nozzle
    compute_expansion_nozzle_performance(core_nozzle,conditions)

    # compute the thrust using the thrust component
    #link the thrust component to the core nozzle
    turbojet.inputs.core_exit_velocity                       = core_nozzle.outputs.velocity
    turbojet.inputs.core_area_ratio                          = core_nozzle.outputs.area_ratio
    turbojet.inputs.core_nozzle                              = core_nozzle.outputs
    
    #link the thrust component to the combustor
    turbojet.inputs.fuel_to_air_ratio                        = combustor.outputs.fuel_to_air_ratio
    
    #link the thrust component to the low pressure compressor 
    turbojet.inputs.stag_temp_lpt_exit                       = low_pressure_compressor.outputs.stagnation_temperature
    turbojet.inputs.stag_press_lpt_exit                      = low_pressure_compressor.outputs.stagnation_pressure 
    turbojet.inputs.total_temperature_reference              = low_pressure_compressor.outputs.stagnation_temperature
    turbojet.inputs.total_pressure_reference                 = low_pressure_compressor.outputs.stagnation_pressure  

    #compute the thrust
    turbojet.inputs.fan_nozzle                               = Data()
    turbojet.inputs.fan_nozzle.velocity                      = 0.0
    turbojet.inputs.fan_nozzle.area_ratio                    = 0.0
    turbojet.inputs.fan_nozzle.static_pressure               = 0.0
    turbojet.inputs.bypass_ratio                             = 0.0
    turbojet.inputs.flow_through_core                        =  1.0 #scaled constant to turn on core thrust computation
    turbojet.inputs.flow_through_fan                         =  0.0 #scaled constant to turn on fan thrust computation      
    
    # compute the thrust
    size_core(turbojet,conditions) 
    
    # Static Sea Level Thrust  
    atmosphere_sls = RCAIDE.Analyses.Atmospheric.US_Standard_1976()
    atmo_data = atmosphere_sls.compute_values(0.0,0.0)
    
    p   = atmo_data.pressure          
    T   = atmo_data.temperature       
    rho = atmo_data.density          
    a   = atmo_data.speed_of_sound    
    mu  = atmo_data.dynamic_viscosity      


    # setup conditions
    conditions_sls = RCAIDE.Analyses.Mission.Common.Results()

    # freestream conditions    
    conditions_sls.freestream.altitude                    = np.atleast_1d(0)
    conditions_sls.freestream.mach_number                 = np.atleast_1d(0.01)
    conditions_sls.freestream.pressure                    = np.atleast_1d(p)
    conditions_sls.freestream.temperature                 = np.atleast_1d(T)
    conditions_sls.freestream.density                     = np.atleast_1d(rho)
    conditions_sls.freestream.dynamic_viscosity           = np.atleast_1d(mu)
    conditions_sls.freestream.gravity                     = np.atleast_2d(planet.sea_level_gravity)
    conditions_sls.freestream.isentropic_expansion_factor = np.atleast_1d(turbojet.working_fluid.compute_gamma(T,p))
    conditions_sls.freestream.Cp                          = np.atleast_1d(turbojet.working_fluid.compute_cp(T,p))
    conditions_sls.freestream.R                           = np.atleast_1d(turbojet.working_fluid.gas_specific_constant)
    conditions_sls.freestream.speed_of_sound              = np.atleast_1d(a)
    conditions_sls.freestream.velocity                    = np.atleast_1d(a*0.01)   
     
    compute_thrust(turbojet,conditions_sls,throttle = 1.0) 
    turbojet.sealevel_static_thrust = turbojet.outputs.thrust
        
    
    return      
  