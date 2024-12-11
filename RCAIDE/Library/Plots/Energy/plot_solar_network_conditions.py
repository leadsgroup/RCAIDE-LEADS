# RCAIDE/Library/Plots/Energy/plot_solar_network_conditions.py
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
#  PLOTS
# ----------------------------------------------------------------------------------------------------------------------   
def plot_solar_network_conditions(results,
                    save_figure   = False,
                    show_legend   = True,
                    save_filename = "Solar_Flux",
                    file_type     = ".png",
                    width = 11, height = 7):
    """This plots the solar flux and power train performance of an solar powered aircraft

    Assumptions:
    None
     
    Source:
    None
    
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
    # get line colors for plots 
    line_colors   = cm.inferno(np.linspace(0,0.9,len(results.segments)))      
    axis_1 = plt.subplot(3,2,1)
    axis_2 = plt.subplot(3,2,2) 
    axis_3 = plt.subplot(3,2,3) 
    axis_4 = plt.subplot(3,2,4) 

    for network in results.segments[0].analyses.energy.vehicle.networks: 
        busses  = network.busses 
        for bus in busses:
            for b_i, battery in enumerate(bus.battery_modules):
                if b_i == 0 or bus.identical_battery_modules == False:
                    for i in range(len(results.segments)):  
                        bus_results         = results.segments[i].conditions.energy[bus.tag] 
                        time                = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min 
                        flux                = results.segments[i].conditions.energy.solar_flux[:,0]
                        charge              = bus_results.power_draw[:,0]
                        current             = bus_results.current_draw[:,0]
                        energy              = bus_results.energy[:,0] / Units.MJ 
                        axis_1 = plt.subplot(2,2,1)
                        if b_i == 0 and i ==0:              
                            axis_1.plot(time, flux, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width, label = battery.tag)
                        else:
                            axis_1.plot(time, flux, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width)
                        axis_1.set_ylabel(r'Solar Flux (W/m^2)')
                        set_axes(axis_1)    
                    
                        axis_2 = plt.subplot(2,2,2)
                        axis_2.plot(time, charge, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width) 
                        axis_2.set_ylabel(r'Charging Power (W)')
                        set_axes(axis_2) 
                    
                        axis_3 = plt.subplot(2,2,3)
                        axis_3.plot(time, current, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width)
                        axis_3.set_xlabel('Time (mins)')
                        axis_3.set_ylabel(r'Battery Current (A)')
                        set_axes(axis_3) 
                    
                        axis_4 = plt.subplot(2,2,4)
                        axis_4.plot(time, energy, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width)
                        axis_4.set_xlabel('Time (mins)')
                        axis_4.set_ylabel(r'Battery Energy (MJ)')
                        set_axes(axis_4)   
                            
    if show_legend:        
        leg =  fig.legend(bbox_to_anchor=(0.5, 0.95), loc='upper center', ncol = 4)  
    
    # Adjusting the sub-plots for legend 
    fig.tight_layout()
    fig.subplots_adjust(top=0.8)
    
    # set title of plot 
    title_text    = 'Solar Flux Conditions: ' + battery.tag  
    fig.suptitle(title_text)
    
    if save_figure:
        plt.savefig(save_filename + file_type)    
           
    return fig 