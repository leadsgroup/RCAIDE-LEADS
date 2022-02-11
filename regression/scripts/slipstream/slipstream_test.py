# Slipstream_Test.py
#
# Created:  Mar 2019, M. Clarke
# Modified: Jun 2021, R. Erhard
#           Feb 2022, R. Erhard

""" setup file for a cruise segment of the NASA X-57 Maxwell (Twin Engine Variant) Electric Aircraft
"""
# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Core import Units, Data

import numpy as np
import pylab as plt
import sys

from SUAVE.Plots.Performance.Mission_Plots import *
from SUAVE.Plots.Geometry.plot_vehicle import plot_vehicle
from SUAVE.Plots.Geometry.plot_vehicle_vlm_panelization  import plot_vehicle_vlm_panelization

from SUAVE.Analyses.Propulsion.Rotor_Wake_Fidelity_One import Rotor_Wake_Fidelity_One
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.VLM import  VLM  
from SUAVE.Analyses.Aerodynamics import Vortex_Lattice


sys.path.append('../Vehicles')
from X57_Maxwell_Mod2 import vehicle_setup, configs_setup
from Stopped_Rotor import vehicle_setup as V2
from Stopped_Rotor import configs_setup as configs2

import time

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    # fidelity zero wakes
    t0=time.time()
    Propeller_Slipstream(wake_fidelity=0,identical_props=True)
    print((time.time()-t0)/60)
    
    # fidelity one wakes
    t0=time.time()
    Propeller_Slipstream(wake_fidelity=1,identical_props=True)  
    print((time.time()-t0)/60)
    
    t0=time.time()
    Propeller_Slipstream(wake_fidelity=1,identical_props=False)  
    print((time.time()-t0)/60)
    
    # include slipstream
    Lift_Rotor_Slipstream(wake_fidelity=0)
    
    return


def Propeller_Slipstream(wake_fidelity,identical_props):
    # setup configs, analyses
    configs, analyses  = X57_setup(wake_fidelity=wake_fidelity, identical_props=identical_props)
    
    # finalize configs
    configs.finalize()
    analyses.finalize()

    # mission analysis
    mission = analyses.missions.base
    results = mission.evaluate()
    
    # check regression values
    if wake_fidelity==0:
        regress_1a(results,configs)
    elif wake_fidelity==1:
        regress_1b(results, configs)
    
    return

def regress_1a(results, configs):
    # Regression for Stopped Rotor Test (using Fidelity Zero wake model)
    lift_coefficient            = results.segments.cruise.conditions.aerodynamics.lift_coefficient[1][0]
    sectional_lift_coeff        = results.segments.cruise.conditions.aerodynamics.lift_breakdown.inviscid_wings_sectional[0]
    
    # lift coefficient and sectional lift coefficient check
    lift_coefficient_true       = 0.43768245404502637    
    sectional_lift_coeff_true   = np.array([ 4.57933495e-01,  3.31030791e-01,  3.72322963e-01,  3.25750054e-01,
                                             6.30279073e-02,  4.57933511e-01,  3.31030802e-01,  3.72323014e-01,
                                             3.25750268e-01,  6.30279328e-02, -5.76708908e-02, -5.54647407e-02,
                                            -4.78313483e-02, -3.37720002e-02, -1.91780281e-02, -5.76709064e-02,
                                            -5.54647633e-02, -4.78313797e-02, -3.37720401e-02, -1.91780399e-02,
                                            -2.12104101e-15, -8.27709312e-16, -6.08914689e-16, -4.63674304e-16,
                                            -2.94742692e-16])

    diff_CL = np.abs(lift_coefficient  - lift_coefficient_true)
    print('CL difference')
    print(diff_CL)

    diff_Cl   = np.abs(sectional_lift_coeff - sectional_lift_coeff_true)
    print('Cl difference')
    print(diff_Cl)
    
    assert np.abs(lift_coefficient  - lift_coefficient_true) < 1e-6
    assert  np.max(np.abs(sectional_lift_coeff - sectional_lift_coeff_true)) < 1e-6

    # plot results, vehicle, and vortex distribution
    plot_mission(results,configs.base)
    plot_vehicle(configs.base, save_figure = False, plot_control_points = False)
    plot_vehicle_vlm_panelization(configs.base, save_figure=False, plot_control_points=True)
              
    return

def regress_1b(results, configs):
    # Regression for Stopped Rotor Test (using Fidelity Zero wake model)
    lift_coefficient            = results.segments.cruise.conditions.aerodynamics.lift_coefficient[1][0]
    sectional_lift_coeff        = results.segments.cruise.conditions.aerodynamics.lift_breakdown.inviscid_wings_sectional[0]
    
    # lift coefficient and sectional lift coefficient check
    lift_coefficient_true       = 0.43813579110326617   
    sectional_lift_coeff_true   = np.array([ 4.17980236e-01,  6.35637114e-01,  3.48935801e-01,  2.65231869e-01,
                                             5.06858059e-02,  3.89937920e-01,  4.10040539e-01,  2.94170309e-01,
                                             2.40561453e-01,  4.58450189e-02, -1.14517416e-01, -1.10479319e-01,
                                            -9.96857377e-02, -8.28741704e-02, -5.29456123e-02, -9.38371057e-02,
                                            -8.94528128e-02, -8.26897370e-02, -6.62645031e-02, -4.09864507e-02,
                                            -6.88346466e-07, -8.74875456e-10, -1.47356558e-08, -2.68471271e-08,
                                            -1.54810930e-08])

    diff_CL = np.abs(lift_coefficient  - lift_coefficient_true)
    print('CL difference')
    print(diff_CL)

    diff_Cl   = np.abs(sectional_lift_coeff - sectional_lift_coeff_true)
    print('Cl difference')
    print(diff_Cl)
    
    assert np.abs(lift_coefficient  - lift_coefficient_true) < 1e-6
    assert  np.max(np.abs(sectional_lift_coeff - sectional_lift_coeff_true)) < 1e-6

    # plot results, vehicle, and vortex distribution
    plot_mission(results,configs.base)
    plot_vehicle(configs.base, save_figure = False, plot_control_points = False)
    plot_vehicle_vlm_panelization(configs.base, save_figure=False, plot_control_points=True)
              
    return


def Lift_Rotor_Slipstream(wake_fidelity):
    # setup configs, analyses
    vehicle = Stopped_Rotor_vehicle(wake_fidelity=wake_fidelity, identical_props=True)
    
    # evaluate single point
    state = SUAVE.Analyses.Mission.Segments.Conditions.State()
    state.conditions = SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()    
    AoA                                                 = 4 * Units.deg*np.ones((1,1))  
    state.conditions.freestream.mach_number             = 0.15      * np.ones_like(AoA) 
    state.conditions.freestream.density                 = 1.21      * np.ones_like(AoA) 
    state.conditions.freestream.dynamic_viscosity       = 1.79      * np.ones_like(AoA) 
    state.conditions.freestream.temperature             = 288.      * np.ones_like(AoA) 
    state.conditions.freestream.pressure                = 99915.9   * np.ones_like(AoA) 
    state.conditions.freestream.reynolds_number         = 3453930.8 * np.ones_like(AoA)
    state.conditions.freestream.velocity                = 51.1      * np.ones_like(AoA) 
    state.conditions.aerodynamics.angle_of_attack       = AoA  
    state.conditions.frames                             = Data()  
    state.conditions.frames.inertial                    = Data()  
    state.conditions.frames.body                        = Data()  
    state.conditions.use_Blade_Element_Theory           = False
    state.conditions.frames.body.transform_to_inertial  = np.array([[[1., 0., 0],[0., 1., 0.],[0., 0., 1.]]]) 
    state.conditions.propulsion.throttle                = np.ones((1,1))
    velocity_vector                                     = np.array([[51.1, 0. ,0.]])
    state.conditions.frames.inertial.velocity_vector    = np.tile(velocity_vector,(1,1)) 
    
    
    settings = simulation_settings()
    
    # run propeller and rotor

    prop = vehicle.networks.lift_cruise.propellers.propeller
    prop.inputs.omega = np.ones((1,1)) * 1200.
    F, Q, P, Cp ,  outputs , etap = prop.spin(state.conditions) 
    prop.outputs = outputs
    
    rot = vehicle.networks.lift_cruise.lift_rotors.lift_rotor
    rot.inputs.omega  = np.ones((1,1)) * 250.
   
    # =========================================================================================================
    # Run Propeller model 
    # =========================================================================================================
    F, Q, P, Cp ,  outputs , etap = rot.spin(state.conditions) 
    
    # append outputs for identical rotors
    for r in vehicle.networks.lift_cruise.lift_rotors:
        r.outputs = outputs 

    # =========================================================================================================
    # Run VLM with slipstream
    # =========================================================================================================    
    results =  VLM(state.conditions,settings,vehicle)
    
    # check regression values
    regress_2(results)

    plot_vehicle(vehicle, save_figure = False, plot_control_points = False)    
    
    return


def regress_2(results):

    CL_truth = 0.51255101
    CM_truth = 0.40329122
    
    CL = results.CL
    CM = results.CM
    
    assert(np.abs(CL_truth  - CL) < 1e-6)
    assert(np.abs(CM_truth  - CM) < 1e-6)
    
    return

def plot_mission(results,vehicle):

    # Plot surface pressure coefficient
    plot_surface_pressure_contours(results,vehicle)

    # Plot lift distribution
    plot_lift_distribution(results,vehicle)

    # Create Video Frames
    create_video_frames(results,vehicle, save_figure = False)

    return


# ----------------------------------------------------------------------
#   Analysis Setup
# ----------------------------------------------------------------------

def X57_setup(wake_fidelity, identical_props):

    # vehicle data
    vehicle  = vehicle_setup()
    # update wake method and rotation direction of rotors:
    props = vehicle.networks.battery_propeller.propellers
    for p in props:
        p.rotation = -1
        if wake_fidelity==1:
            p.Wake = Rotor_Wake_Fidelity_One()   
            p.Wake.wake_settings.number_rotor_rotations = 1  # reduced for regression speed
            p.Wake.wake_settings.number_steps_per_rotation = 24  # reduced for regression speed
            

    # test for non-identical propellers
    if not identical_props:
        vehicle.networks.battery_propeller.identical_propellers = False
    configs  = configs_setup(vehicle)

    # vehicle analyses
    configs_analyses = analyses_setup(configs)

    # mission analyses
    mission  = X57_mission_setup(configs_analyses,vehicle)
    missions_analyses = missions_setup(mission)

    analyses = SUAVE.Analyses.Analysis.Container()
    analyses.configs  = configs_analyses
    analyses.missions = missions_analyses

    return configs, analyses

# ----------------------------------------------------------------------
#   Define the Vehicle Analyses
# ----------------------------------------------------------------------

def analyses_setup(configs):

    analyses = SUAVE.Analyses.Analysis.Container()

    # build a base analysis for each config
    for tag,config in configs.items():
        analysis = base_analysis(config)
        analyses[tag] = analysis

    return analyses

def base_analysis(vehicle):

    # ------------------------------------------------------------------
    #   Initialize the Analyses
    # ------------------------------------------------------------------
    analyses = SUAVE.Analyses.Vehicle()

    # ------------------------------------------------------------------
    #  Basic Geometry Relations
    sizing = SUAVE.Analyses.Sizing.Sizing()
    sizing.features.vehicle = vehicle
    analyses.append(sizing)

    # ------------------------------------------------------------------
    #  Weights
    weights = SUAVE.Analyses.Weights.Weights_Transport()
    weights.vehicle = vehicle
    analyses.append(weights)

    # ------------------------------------------------------------------
    #  Aerodynamics Analysis
    aerodynamics = SUAVE.Analyses.Aerodynamics.Fidelity_Zero()
    aerodynamics.settings.use_surrogate              = False
    aerodynamics.settings.propeller_wake_model       = True

    aerodynamics.settings.number_spanwise_vortices   = 5
    aerodynamics.settings.number_chordwise_vortices  = 2
    aerodynamics.geometry                            = vehicle
    aerodynamics.settings.drag_coefficient_increment = 0.0000
    analyses.append(aerodynamics)

    # ------------------------------------------------------------------
    #  Stability Analysis
    stability = SUAVE.Analyses.Stability.Fidelity_Zero()
    stability.geometry = vehicle
    analyses.append(stability)

    # ------------------------------------------------------------------
    #  Energy
    energy= SUAVE.Analyses.Energy.Energy()
    energy.network = vehicle.networks
    analyses.append(energy)

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = SUAVE.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)

    # done!
    return analyses


# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------

def X57_mission_setup(analyses,vehicle):
    net_tag = list(vehicle.networks.keys())[0]
    
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------
    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'mission'

    # airport
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0. * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()

    mission.airport = airport

    # unpack Segments module
    Segments = SUAVE.Analyses.Mission.Segments

    # base segment
    base_segment = Segments.Segment()
    ones_row     = base_segment.state.ones_row
    base_segment.process.iterate.initials.initialize_battery = SUAVE.Methods.Missions.Segments.Common.Energy.initialize_battery
    base_segment.process.iterate.conditions.planet_position  = SUAVE.Methods.skip
    base_segment.state.numerics.number_control_points        = 2

    # ------------------------------------------------------------------
    #   Cruise Segment: constant Speed, constant altitude
    # ------------------------------------------------------------------
    segment = Segments.Cruise.Constant_Speed_Constant_Altitude(base_segment)
    segment.tag = "cruise"
    segment.analyses.extend(analyses.base)
    segment.battery_energy            = vehicle.networks[net_tag].battery.max_energy* 0.7
    segment.altitude                  = 8012 * Units.feet
    segment.air_speed                 = 135. * Units['mph']
    segment.distance                  = 20.  * Units.nautical_mile
    segment.state.unknowns.throttle   = 0.85 * ones_row(1)

    # post-process aerodynamic derivatives in cruise
    segment.process.finalize.post_process.aero_derivatives = SUAVE.Methods.Flight_Dynamics.Static_Stability.compute_aero_derivatives
    segment = vehicle.networks[net_tag].add_unknowns_and_residuals_to_segment(segment)

    # add to misison
    mission.append_segment(segment)

    return mission


def missions_setup(base_mission):

    # the mission container
    missions = SUAVE.Analyses.Mission.Mission.Container()

    # ------------------------------------------------------------------
    #   Base Mission
    # ------------------------------------------------------------------

    missions.base = base_mission

    # done!
    return missions


def Stopped_Rotor_vehicle(wake_fidelity, identical_props):

    # vehicle data
    vehicle  = V2()
    # update wake method and rotation direction of rotors:
    props = vehicle.networks.lift_cruise.propellers
    lift_rots = vehicle.networks.lift_cruise.lift_rotors
    for p in props:
        p.rotation = -1
        if wake_fidelity==1:
            p.Wake = Rotor_Wake_Fidelity_One()   
            p.Wake.wake_settings.number_rotor_rotations = 1  # reduced for regression speed
    for r in lift_rots:
        r.rotation = -1
        if wake_fidelity==1:
            r.Wake = Rotor_Wake_Fidelity_One()   
            r.Wake.wake_settings.number_rotor_rotations = 1  # reduced for regression speed      

    # test for non-identical propellers
    if not identical_props:
        vehicle.networks.lift_cruise.identical_propellers = False
        vehicle.networks.lift_cruise.identical_lift_rotors = False

    return vehicle


def simulation_settings():
    settings = Vortex_Lattice().settings  
    settings.number_spanwise_vortices                 = 15
    settings.number_chordwise_vortices                = 1
    settings.use_surrogate                            = False    
    settings.propeller_wake_model                     = True 
    settings.spanwise_cosine_spacing                  = True 
    settings.model_fuselage                           = True   
    settings.leading_edge_suction_multiplier          = 1.0    
    settings.oswald_efficiency_factor                 = None
    settings.span_efficiency                          = None
    settings.viscous_lift_dependent_drag_factor       = 0.38
    settings.drag_coefficient_increment               = 0.0000
    settings.spoiler_drag_increment                   = 0.00 
    settings.maximum_lift_coefficient                 = np.inf 
    
    return settings


if __name__ == '__main__':
    main()
    plt.show()
