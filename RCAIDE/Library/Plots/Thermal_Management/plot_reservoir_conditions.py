## @ingroup Visualization-Performance-Energy-Thermal_Management
# RCAIDE/Visualization/Performance/Energy/Thermal_Management/plot_reservoir_conditions.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  

from RCAIDE.Framework.Core import Units
from RCAIDE.Library.Plots.Common import set_axes, plot_style
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np 

# ----------------------------------------------------------------------------------------------------------------------
#   plot_heat_exchanger_system_conditions
# ----------------------------------------------------------------------------------------------------------------------   
## @ingroup Visualization-Performance-Energy-Thermal_Management
def plot_reservoir_conditions(results,
                                  save_figure = False,
                                  show_legend = False,
                                  save_filename = "Reservoir_Conditions",
                                  file_type = ".png",
                                  width = 12, height = 7):
    """Plots the cell-level conditions of the battery throughout flight.

    Assumptions:
    None

    Source:
    None

    Inputs:
    results.segments.conditions.
        freestream.altitude
        weights.total_mass
        weights.vehicle_mass_rate
        frames.body.thrust_force_vector

    Outputs: 
    Plots

    Properties Used:
    N/A	
    """ 
    
    # get plotting style 
    ps      = plot_style()  

    parameters = {'axes.labelsize': ps.axis_font_size,
                  'xtick.labelsize': ps.axis_font_size,
                  'ytick.labelsize': ps.axis_font_size,
                  'axes.titlesize': ps.title_font_size}
    plt.rcParams.update(parameters)
     
    # get line colors for plots 
    line_colors   = cm.inferno(np.linspace(0,0.9,len(results.segments)))     

    fig = plt.figure(save_filename)
    fig.set_size_inches(width,height)  
    axis_1 = plt.subplot(1,1,1)
    set_axes(axis_1)     
             
    b_i = 0 
    for network in results.segments[0].analyses.energy.networks: 
        busses  = network.busses
        for bus in busses: 
            for battery in bus.batteries:  
                for i in range(len(results.segments)):  
                    time                  = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min    
                    battery_conditions    = results.segments[i].conditions.energy[bus.tag][battery.tag]   
                    reservoir_temperature =  battery_conditions.thermal_management_system.RES.coolant_temperature[:,0]
                    
                    segment_tag  = results.segments[i].tag
                    segment_name = segment_tag.replace('_', ' ')  
                    if b_i == 0:                     
                        axis_1.plot(time, reservoir_temperature, color = line_colors[i], marker = ps.markers[b_i], linewidth = ps.line_width, label = segment_name)
                    else:
                        axis_1.plot(time, reservoir_temperature, color = line_colors[i], marker = ps.markers[b_i], linewidth = ps.line_width)
                    axis_1.set_ylabel(r'Coolant Temp. (K)')  
                b_i += 1     
            
    if show_legend:      
        h, l = axis_1.get_legend_handles_labels()
        axis_1.legend(h, l)    
        leg =  fig.legend(bbox_to_anchor=(0.5, 0.95), loc='upper center', ncol = 5) 
        leg.set_title('Flight Segment', prop={'size': ps.legend_font_size, 'weight': 'heavy'})
                    
    # Adjusting the sub-plots for legend 
    fig.subplots_adjust(top=0.8) 
    
    # set title of plot 
    title_text   = 'Reservoir Temperature'       
    fig.suptitle(title_text) 
    
    if save_figure:
        plt.savefig(save_filename + battery.tag + file_type)    
    return fig 