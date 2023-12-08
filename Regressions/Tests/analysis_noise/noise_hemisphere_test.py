# digital_elevation_and_noise_hemispheres_test.py
#
# Created: Apr 2021, M. Clarke  
 
# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------
import RCAIDE
from RCAIDE.Core import Units , Data 
from RCAIDE.Visualization import *     
from RCAIDE.Methods.Noise.Metrics import * 
from RCAIDE.Methods.Performance.estimate_stall_speed                          import estimate_stall_speed  

# python import
import matplotlib.pyplot as plt  
import sys 
import numpy as np     

# local imports 
sys.path.append('../../Vehicles')
from NASA_X57    import vehicle_setup, configs_setup     

# ----------------------------------------------------------------------
#   Main
# ---------------------------------------------------------------------- 
def main():     
    vehicle  = vehicle_setup()  
    configs  = configs_setup(vehicle) 
    analyses = analyses_setup(configs)  
    mission  = mission_setup(analyses,vehicle)
    missions = missions_setup(mission)  
    results  = missions.base_mission.evaluate()   
    regression_plotting_flag = False 
    plot_results(results,regression_plotting_flag)    
    return     
 

def base_analysis(vehicle):

    # ------------------------------------------------------------------
    #   Initialize the Analyses
    # ------------------------------------------------------------------     
    analyses = RCAIDE.Analyses.Vehicle() 
 
    # ------------------------------------------------------------------
    #  Weights
    weights         = RCAIDE.Analyses.Weights.Weights_eVTOL()
    weights.vehicle = vehicle
    analyses.append(weights)

    # ------------------------------------------------------------------
    #  Aerodynamics Analysis
    aerodynamics          = RCAIDE.Analyses.Aerodynamics.Subsonic_VLM() 
    aerodynamics.geometry = vehicle
    aerodynamics.settings.drag_coefficient_increment = 0.0000
    analyses.append(aerodynamics)   
    

    # ------------------------------------------------------------------
    #  Noise Analysis 
    # ------------------------------------------------------------------   
    noise = RCAIDE.Analyses.Noise.Frequency_Domain_Buildup()   
    noise.geometry = vehicle
    noise.settings.noise_hemisphere                       = True 
    noise.settings.noise_hemisphere_radius                = 20          
    noise.settings.noise_hemisphere_microphone_resolution = 20
    noise.settings.noise_hemisphere_phi_angle_bounds      = np.array([0,np.pi]) 
    noise.settings.noise_hemisphere_theta_angle_bounds    = np.array([np.pi/2,-np.pi/2])
    analyses.append(noise)                                                           

    # ------------------------------------------------------------------
    #  Energy
    energy          = RCAIDE.Analyses.Energy.Energy()
    energy.networks = vehicle.networks 
    analyses.append(energy)

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = RCAIDE.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = RCAIDE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)   

    # done!
    return analyses    

# ----------------------------------------------------------------------
#   Define the Vehicle Analyses
# ---------------------------------------------------------------------- 
def analyses_setup(configs):

    analyses = RCAIDE.Analyses.Analysis.Container()

    # build a base analysis for each config
    for tag,config in configs.items():
        analysis = base_analysis(config) 
        analyses[tag] = analysis

    return analyses  
  

# ----------------------------------------------------------------------
#  Set Up Mission 
# ---------------------------------------------------------------------- 
def mission_setup(analyses,vehicle):  

    # Determine Stall Speed 
    vehicle_mass   = vehicle.mass_properties.max_takeoff
    reference_area = vehicle.reference_area
    altitude       = 0.0 
    CL_max         = 1.2  
    Vstall         = estimate_stall_speed(vehicle_mass,reference_area,altitude,CL_max)       
    
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------
    mission       = RCAIDE.Analyses.Mission.Sequential_Segments()
    mission.tag   = 'mission' 
    Segments      = RCAIDE.Analyses.Mission.Segments  
    base_segment  = Segments.Segment()   
    base_segment.state.numerics.number_control_points  = 5 
     
    # ------------------------------------------------------------------
    #   Constant Altitude Cruises 
    # ------------------------------------------------------------------   
    segment                                          = Segments.Cruise.Constant_Speed_Constant_Altitude(base_segment)
    segment.tag                                      = "Cruise" 
    segment.analyses.extend( analyses.base)            
    segment.initial_battery_state_of_charge          = 0.89         
    segment.altitude                                 = 1000. * Units.ft 
    segment.air_speed                                = Vstall*1.2       
    segment.distance                                 = 1000       
    segment = analyses.base.energy.networks.all_electric.add_unknowns_and_residuals_to_segment(segment)      
    mission.append_segment(segment)  
     
    return mission

# ----------------------------------------------------------------------
#  Set Up Missions 
# ---------------------------------------------------------------------- 
def missions_setup(mission): 
 
    missions     = RCAIDE.Analyses.Mission.Missions() 
    mission.tag  = 'base_mission'
    missions.append(mission)
 
    return missions  


# ----------------------------------------------------------------------
#  Plot Resuls 
# ---------------------------------------------------------------------- 
def plot_results(results,regression_plotting_flag): 
    
    noise_data   = post_process_noise_data(results)  
    
    # Plot noise hemisphere
    plot_noise_hemisphere(noise_data,
                          noise_level      = noise_data.SPL_dBA[1], 
                          min_noise_level  = 35,  
                          max_noise_level  = 90, 
                          noise_scale_label= 'SPL [dBA]',
                          show_figure      = regression_plotting_flag)     
    

    # Plot noise hemisphere with vehicle 
    plot_noise_hemisphere(noise_data,
                          noise_level      = noise_data.SPL_dBA[1], 
                          min_noise_level  = 35,  
                          max_noise_level  = 90, 
                          noise_scale_label= 'SPL [dBA]',
                          save_filename    = "Noise_Hemisphere_With_Aircraft", 
                          vehicle          = results.segments.cruise.analyses.aerodynamics.geometry,
                          show_figure      = regression_plotting_flag)      
    
     
    return  

if __name__ == '__main__': 
    main()    
    plt.show()