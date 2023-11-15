# Regression/scripts/Vehicles/Concorde.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
# RCAIDE imports 
import RCAIDE
from RCAIDE.Core                                           import Units , Data    
from RCAIDE.Methods.Propulsion.Design                      import design_turbojet
from RCAIDE.Methods.Geometry.Two_Dimensional.Planform      import wing_planform, segment_properties,wing_segmented_planform
from RCAIDE.Visualization                 import *     

# python imports 
import numpy as np  
from copy import deepcopy


def vehicle_setup():

    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------    
    
    vehicle = RCAIDE.Vehicle()
    vehicle.tag = 'Concorde'    
    
    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

    # mass properties
    vehicle.mass_properties.max_takeoff               = 185000.   # kg
    vehicle.mass_properties.operating_empty           = 78700.   # kg
    vehicle.mass_properties.takeoff                   = 183000.   # kg, adjusted due to significant fuel burn on runway
    vehicle.mass_properties.cargo                     = 1000.  * Units.kilogram   
    vehicle.mass_properties.max_zero_fuel             = 92000.
        
    # envelope properties
    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5

    # basic parameters
    vehicle.reference_area               = 358.25      
    vehicle.passengers                   = 100
    vehicle.systems.control              = "fully powered" 
    vehicle.systems.accessories          = "sst"
    vehicle.maximum_cross_sectional_area = 13.9
    vehicle.total_length                 = 61.66
    vehicle.design_mach_number           = 2.02
    vehicle.design_range                 = 4505 * Units.miles
    vehicle.design_cruise_alt            = 60000.0 * Units.ft
    
    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    wing = RCAIDE.Components.Wings.Main_Wing()
    wing.tag = 'main_wing'
    
    wing.aspect_ratio            = 1.83
    wing.sweeps.quarter_chord    = 59.5 * Units.deg
    wing.sweeps.leading_edge     = 66.5 * Units.deg
    wing.thickness_to_chord      = 0.03
    wing.taper                   = 0.
    
    wing.spans.projected           = 25.6    
    
    wing.chords.root               = 33.8
    wing.total_length              = 33.8
    wing.chords.tip                = 1.1
    wing.chords.mean_aerodynamic   = 18.4
    
    wing.areas.reference           = 358.25 
    wing.areas.wetted              = 601.
    wing.areas.exposed             = 326.5
    wing.areas.affected            = .6*wing.areas.reference
    
    wing.twists.root               = 0.0 * Units.degrees
    wing.twists.tip                = 0.0 * Units.degrees
    
    wing.origin                    = [[14,0,-.8]]
    wing.aerodynamic_center        = [35,0,0] 
    
    wing.vertical                  = False
    wing.symmetric                 = True
    wing.high_lift                 = True
    wing.vortex_lift               = True
    wing.high_mach                 = True 
    wing.dynamic_pressure_ratio    = 1.0
     
    wing_airfoil                   = RCAIDE.Components.Airfoils.Airfoil() 
    wing_airfoil.coordinate_file   = '../../Vehicles/Airfoils/NACA65-203.txt'  
    wing.append_airfoil(wing_airfoil)  
    
    # set root sweep with inner section
    segment = RCAIDE.Components.Wings.Segment()
    segment.tag                   = 'section_1'
    segment.percent_span_location = 0.
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 33.8/33.8
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 67. * Units.deg
    segment.thickness_to_chord    = 0.03
    segment.append_airfoil(wing_airfoil)
    wing.Segments.append(segment)
    
    # set section 2 start point
    segment = RCAIDE.Components.Wings.Segment()
    segment.tag                   = 'section_2'
    segment.percent_span_location = 6.15/(25.6/2) + wing.Segments['section_1'].percent_span_location
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 13.8/33.8
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 48. * Units.deg
    segment.thickness_to_chord    = 0.03
    segment.append_airfoil(wing_airfoil)
    wing.Segments.append(segment)
    
    
    # set section 3 start point
    segment = RCAIDE.Components.Wings.Segment() 
    segment.tag                   = 'section_3'
    segment.percent_span_location = 5.95/(25.6/2) + wing.Segments['section_2'].percent_span_location
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 4.4/33.8
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 71. * Units.deg 
    segment.thickness_to_chord    = 0.03
    segment.append_airfoil(wing_airfoil)
    wing.Segments.append(segment)  
    
    # set tip
    segment = RCAIDE.Components.Wings.Segment() 
    segment.tag                   = 'tip'
    segment.percent_span_location = 1.
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 1.1/33.8
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 0.
    segment.thickness_to_chord    = 0.03
    segment.append_airfoil(wing_airfoil)
    wing.Segments.append(segment)      
    
    # Fill out more segment properties automatically
    wing = wing_segmented_planform(wing)        
    
    
    # add to vehicle
    vehicle.append_component(wing)
    
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
    wing = RCAIDE.Components.Wings.Vertical_Tail()
    wing.tag = 'vertical_stabilizer'    
    
    wing.aspect_ratio            = 0.74     
    wing.sweeps.quarter_chord    = 60 * Units.deg
    wing.thickness_to_chord      = 0.04
    wing.taper                   = 0.14 
    wing.spans.projected         = 6.0     
    wing.chords.root             = 14.5
    wing.total_length            = 14.5
    wing.chords.tip              = 2.7
    wing.chords.mean_aerodynamic = 8.66 
    wing.areas.reference         = 33.91     
    wing.areas.wetted            = 76. 
    wing.areas.exposed           = 38.
    wing.areas.affected          = 33.91 
    wing.twists.root             = 0.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees   
    wing.origin                  = [[42.,0,1.]]
    wing.aerodynamic_center      = [50,0,0]     
    wing.vertical                = True 
    wing.symmetric               = False
    wing.t_tail                  = False
    wing.high_mach               = True     
    
    wing.dynamic_pressure_ratio  = 1.0
    
    tail_airfoil = RCAIDE.Components.Airfoils.Airfoil()
    # This airfoil is not a true Concorde airfoil
    tail_airfoil.coordinate_file = '../../Vehicles/Airfoils/supersonic_tail.txt' 
    
    wing.append_airfoil(tail_airfoil)  

    # set root sweep with inner section
    segment = RCAIDE.Components.Wings.Segment()
    segment.tag                   = 'section_1'
    segment.percent_span_location = 0.0
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 14.5/14.5
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 63. * Units.deg
    segment.thickness_to_chord    = 0.04
    segment.append_airfoil(tail_airfoil)
    wing.Segments.append(segment)
    
    # set mid section start point
    segment = RCAIDE.Components.Wings.Segment()
    segment.tag                   = 'section_2'
    segment.percent_span_location = 2.4/(6.0) + wing.Segments['section_1'].percent_span_location
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 7.5/14.5
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 40. * Units.deg
    segment.thickness_to_chord    = 0.04
    segment.append_airfoil(tail_airfoil)
    wing.Segments.append(segment)
    
    # set tip
    segment = RCAIDE.Components.Wings.Segment()
    segment.tag                   = 'tip'
    segment.percent_span_location = 1.
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 2.7/14.5
    segment.dihedral_outboard     = 0.
    segment.sweeps.quarter_chord  = 0.
    segment.thickness_to_chord    = 0.04
    segment.append_airfoil(tail_airfoil)
    wing.Segments.append(segment)    
    
    # Fill out more segment properties automatically
    wing = wing_segmented_planform(wing)        
    
    # add to vehicle
    vehicle.append_component(wing)    


    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    
    fuselage                                        = RCAIDE.Components.Fuselages.Fuselage()
    fuselage.tag                                    = 'fuselage' 
    fuselage.seats_abreast                          = 4
    fuselage.seat_pitch                             = 38. * Units.inches 
    fuselage.fineness.nose                          = 4.3
    fuselage.fineness.tail                          = 6.4 
    fuselage.lengths.total                          = 61.66   
    fuselage.width                                  = 2.88 
    fuselage.heights.maximum                        = 3.32    
    fuselage.heights.maximum                        = 3.32    
    fuselage.heights.at_quarter_length              = 3.32    
    fuselage.heights.at_wing_root_quarter_chord     = 3.32    
    fuselage.heights.at_three_quarters_length       = 3.32    
    fuselage.areas.wetted                           = 442.
    fuselage.areas.front_projected                  = 11.9 
    fuselage.effective_diameter                     = 3.1 
    fuselage.differential_pressure                  = 7.4e4 * Units.pascal    # Maximum differential pressure 
    
    fuselage.OpenVSP_values = Data() # VSP uses degrees directly
    
    fuselage.OpenVSP_values.nose = Data()
    fuselage.OpenVSP_values.nose.top = Data()
    fuselage.OpenVSP_values.nose.side = Data()
    fuselage.OpenVSP_values.nose.top.angle = 20.0
    fuselage.OpenVSP_values.nose.top.strength = 0.75
    fuselage.OpenVSP_values.nose.side.angle = 20.0
    fuselage.OpenVSP_values.nose.side.strength = 0.75  
    fuselage.OpenVSP_values.nose.TB_Sym = True
    fuselage.OpenVSP_values.nose.z_pos = -.01
    
    fuselage.OpenVSP_values.tail = Data()
    fuselage.OpenVSP_values.tail.top = Data()
    fuselage.OpenVSP_values.tail.side = Data()    
    fuselage.OpenVSP_values.tail.bottom = Data()
    fuselage.OpenVSP_values.tail.top.angle = 0.0
    fuselage.OpenVSP_values.tail.top.strength = 0.0 
    
    vehicle.append_component(fuselage)
    

    # ------------------------------------------------------------------        
    # the nacelle 
    # ------------------------------------------------------------------    
    nacelle                  = RCAIDE.Components.Nacelles.Nacelle()
    nacelle.diameter         = 1.3
    nacelle.tag              = 'nacelle_1'
    nacelle.origin           = [[36.56, 22, -1.9]] 
    nacelle.length           = 12.0 
    nacelle.inlet_diameter   = 1.1 
    nacelle.areas.wetted     = 30.
    vehicle.append_component(nacelle)       

    nacelle_2               = deepcopy(nacelle)
    nacelle_2.tag           = 'nacelle_2'
    nacelle_2.origin        = [[37.,5.3,-1.3]]
    vehicle.append_component(nacelle_2)     

    nacelle_3               = deepcopy(nacelle)
    nacelle_3.tag           = 'nacelle_3'
    nacelle_3.origin        = [[37.,-5.3,-1.3]]
    vehicle.append_component(nacelle_3)   

    nacelle_4              = deepcopy(nacelle)
    nacelle_4.tag          = 'nacelle_4'
    nacelle_4.origin       = [[37.,-6.,-1.3]]
    vehicle.append_component(nacelle_4)       
        
        

    #------------------------------------------------------------------------------------------------------------------------------------  
    #  Turbofan Network
    #------------------------------------------------------------------------------------------------------------------------------------  
    net                                            = RCAIDE.Energy.Networks.Turbojet_Engine() 
    
    #------------------------------------------------------------------------------------------------------------------------------------  
    # Fuel Distrubition Line 
    #------------------------------------------------------------------------------------------------------------------------------------  
    fuel_line                                     = RCAIDE.Energy.Distributors.Fuel_Line() 
       
    #------------------------------------------------------------------------------------------------------------------------------------  
    #   Fuel
    #------------------------------------------------------------------------------------------------------------------------------------  
    # fuel tank 
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_9'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[26.5,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 11096
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_10'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[28.7,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 11943
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_1_and_4'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[31.0,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 4198+4198
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_5_and_8'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[32.9,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 7200+12838
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_6_and_7'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[37.4,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 11587+7405
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_5A_and_7A'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[40.2,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 2225+2225
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank) 
    
    fuel_tank                                      = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_2_and_3'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[40.2,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 4570+4570
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank)  
 
    fuel_tank = RCAIDE.Energy.Storages.Fuel_Tanks.Fuel_Tank()
    fuel_tank.tag                                  = 'tank_11'
    fuel_tank.mass_properties.center_of_gravity    = np.array([[49.8,0,0]])
    fuel_tank.mass_properties.fuel_mass_when_full  = 10415
    fuel_tank.fuel_selector_ratio                  = 1/8
    fuel_tank.fuel_type                            = RCAIDE.Attributes.Propellants.Jet_A()
    fuel_line.fuel_tanks.append(fuel_tank)      
    
    # ------------------------------------------------------------------
    #   Turbojet Network
    # ------------------------------------------------------------------    
    
    # instantiate the gas turbine network
    turbojet                    = RCAIDE.Energy.Converters.Turbojet()
    turbojet.tag                = 'turbojet_1'  
    turbojet.engine_length      = 4.039
    turbojet.nacelle_diameter   = 1.3
    turbojet.inlet_diameter     = 1.212 
    turbojet.areas.wetted       = 30
    turbojet.design_altitude    = 60000.0*Units.ft
    turbojet.design_mach_number = 2.02
    turbojet.design_thrust      = 40000. * Units.lbf  
    turbojet.origin             = [[37.,6.,-1.3]] 
    turbojet.working_fluid      = RCAIDE.Attributes.Gases.Air()
    
    # Ram  
    ram     = RCAIDE.Energy.Converters.Ram()
    ram.tag = 'ram' 
    turbojet.append(ram) 
 
    # Inlet Nozzle 
    inlet_nozzle                          = RCAIDE.Energy.Converters.Compression_Nozzle()
    inlet_nozzle.tag                      = 'inlet_nozzle' 
    inlet_nozzle.polytropic_efficiency    = 1.0
    inlet_nozzle.pressure_ratio           = 1.0
    inlet_nozzle.pressure_recovery        = 0.94 
    turbojet.append(inlet_nozzle)     
          
    #  Low Pressure Compressor      
    compressor                            = RCAIDE.Energy.Converters.Compressor()    
    compressor.tag                        = 'low_pressure_compressor' 
    compressor.polytropic_efficiency      = 0.88
    compressor.pressure_ratio             = 3.1     
    turbojet.append(compressor)       
        
    # High Pressure Compressor        
    compressor                            = RCAIDE.Energy.Converters.Compressor()    
    compressor.tag                        = 'high_pressure_compressor' 
    compressor.polytropic_efficiency      = 0.88
    compressor.pressure_ratio             = 5.0  
    turbojet.append(compressor)
 
    # Low Pressure Turbine 
    turbine                               = RCAIDE.Energy.Converters.Turbine()   
    turbine.tag                           ='low_pressure_turbine' 
    turbine.mechanical_efficiency         = 0.99
    turbine.polytropic_efficiency         = 0.89 
    turbojet.append(turbine)        
             
    # High Pressure Turbine         
    turbine                               = RCAIDE.Energy.Converters.Turbine()   
    turbine.tag                           ='high_pressure_turbine' 
    turbine.mechanical_efficiency         = 0.99
    turbine.polytropic_efficiency         = 0.87 
    turbojet.append(turbine)  
          
    # Combustor   
    combustor                             = RCAIDE.Energy.Converters.Combustor()   
    combustor.tag                         = 'combustor' 
    combustor.efficiency                  = 0.94
    combustor.alphac                      = 1.0     
    combustor.turbine_inlet_temperature   = 1440.
    combustor.pressure_ratio              = 0.92
    combustor.fuel_data                   = RCAIDE.Attributes.Propellants.Jet_A()     
    turbojet.append(combustor)
     
    #  Afterburner  
    afterburner                           = RCAIDE.Energy.Converters.Combustor()   
    afterburner.tag                       = 'afterburner' 
    afterburner.efficiency                = 0.9
    afterburner.alphac                    = 1.0     
    afterburner.turbine_inlet_temperature = 1500
    afterburner.pressure_ratio            = 1.0
    afterburner.fuel_data                 = RCAIDE.Attributes.Propellants.Jet_A()     
    turbojet.append(afterburner)    
 
    # Core Nozzle 
    nozzle                                = RCAIDE.Energy.Converters.Supersonic_Nozzle()   
    nozzle.tag                            = 'core_nozzle' 
    nozzle.pressure_recovery              = 0.95
    nozzle.pressure_ratio                 = 1.    
    turbojet.append(nozzle) 
    
    # design turbojet 
    design_turbojet(turbojet)  
    
    # append turbojet 
    fuel_line.turbojets.append(turbojet) 
    

    # append turbojet     
    turbojet_2                      = deepcopy(turbojet)
    turbojet_2.tag                  = 'turbojet_2' 
    turbojet_2.origin               = [[37.,5.3,-1.3]] 
    fuel_line.turbojets.append(turbojet_2)    

    # append turbojet    
    turbojet_3                      = deepcopy(turbojet)
    turbojet_3.tag                  = 'turbojet_3' 
    turbojet_3.origin               = [[37.,-5.3,-1.3]] 
    fuel_line.turbojets.append(turbojet_3)    
    
    # append turbojet 
    turbojet_4                      = deepcopy(turbojet)
    turbojet_4.tag                  = 'turbojet_4' 
    turbojet_4.origin               = [[37.,-6.,-1.3]] 
    fuel_line.turbojets.append(turbojet_4)      

    net.fuel_lines.append(fuel_line)    
    vehicle.append_energy_network(net)     
    
    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------ 

    return vehicle


# ----------------------------------------------------------------------
#   Define the Configurations
# ---------------------------------------------------------------------

def configs_setup(vehicle):
    
    # ------------------------------------------------------------------
    #   Initialize Configurations
    # ------------------------------------------------------------------ 
    configs         = RCAIDE.Components.Configs.Config.Container() 
    base_config     = RCAIDE.Components.Configs.Config(vehicle)
    base_config.tag = 'base'
    configs.append(base_config)
    
    # ------------------------------------------------------------------
    #   Cruise Configuration
    # ------------------------------------------------------------------ 
    config     = RCAIDE.Components.Configs.Config(base_config)
    config.tag = 'cruise' 
    configs.append(config)
    
    # ------------------------------------------------------------------
    #   Afterburner Climb Configuration
    # ------------------------------------------------------------------ 
    config                                      = RCAIDE.Components.Configs.Config(base_config)
    config.tag                                  = 'climb' 
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_1.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_2.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_3.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_4.afterburner_active = True 
    configs.append(config)    
    
    
    # ------------------------------------------------------------------
    #   Takeoff Configuration
    # ------------------------------------------------------------------  
    config                                      = RCAIDE.Components.Configs.Config(base_config)
    config.tag                                  = 'takeoff' 
    config.V2_VS_ratio                          = 1.21
    config.maximum_lift_coefficient             = 2.  
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_1.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_2.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_3.afterburner_active = True
    config.networks.turbojet_engine.fuel_lines.fuel_line.turbojets.turbojet_4.afterburner_active = True 
    configs.append(config)
    
    
    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------

    config                                = RCAIDE.Components.Configs.Config(base_config)
    config.tag                            = 'landing' 
    config.wings['main_wing'].flaps_angle = 0. * Units.deg
    config.wings['main_wing'].slats_angle = 0. * Units.deg 
    config.Vref_VS_ratio                  = 1.23
    config.maximum_lift_coefficient       = 2.
    
    configs.append(config)
    
    # done!
    return configs
