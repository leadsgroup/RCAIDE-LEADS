# RCAIDE/Framework/External_Interfaces/OpenVSP/get_vsp_measurements.py
# 
# Created:  --- 2016, T. MacDonald
# Modified: Aug 2017, T. MacDonald
#           Mar 2018, T. MacDonald
#           Jan 2020, T. MacDonald
#           Feb 2021, T. MacDonald

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
# RCAIDE imports 
try:
    import vsp as vsp
except ImportError:
    try:
        import openvsp as vsp
    except ImportError:
        # This allows RCAIDE to build without OpenVSP
        pass
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  Get VSP Measurements
# ---------------------------------------------------------------------------------------------------------------------- 
def get_vsp_measurements(filename='Unnamed_CompGeom.csv', measurement_type='wetted_area'):
    """
    Computes wetted areas or volumes of a vehicle using OpenVSP
    
    Parameters
    ----------
    filename : str, optional
        Name of output CSV file
        Default: 'Unnamed_CompGeom.csv'
    measurement_type : {'wetted_area', 'wetted_volume'}, optional
        Type of measurement to compute
        Default: 'wetted_area'
        
    Returns
    -------
    measurements : dict
        Dictionary containing measurements for each component
        
        - Keys are component tags
        - Values are areas [m^2] or volumes [m^3] depending on measurement_type

    Notes
    -----
    This function calls OpenVSP to compute geometric measurements of a previously 
    written vehicle. The measurements are extracted from a CSV file generated by
    OpenVSP's computation.

    **Major Assumptions**
    * Vehicle must be open in OpenVSP (via recently used vsp_write)
    * All components have different tags
    * Repeated tags are added together (assumed to represent multiple engines etc)
    * Values from repeated tags may need to be divided by number of entities before assignment
    
    **Extra modules required**
    * OpenVSP (vsp or openvsp module)

    """        
    
    if measurement_type == 'wetted_area':
        output_ind = 2
    elif measurement_type == 'wetted_volume':
        output_ind = 4
    else:
        raise NotImplementedError
    
    half_mesh = False # Note that this does not affect the Gmsh/SU2 meshing process
    # it only affects how much area of a component is included in the output
    try:
        file_type = vsp.COMP_GEOM_CSV_TYPE
    except NameError:
        print('VSP import failed')
        return -1

    vsp.SetComputationFileName(file_type, filename)
    vsp.ComputeCompGeom(vsp.SET_ALL, half_mesh, file_type)
    
    f = open(filename)
    
    measurements = dict()
    
    # Extract wetted areas for each component
    for ii, line in enumerate(f):
        if ii == 0:
            pass
        elif line == '\n':
            break
        else:
            vals = line.split(',')
            item_tag = vals[0][:]
            item_w_area = float(vals[output_ind])
            if item_tag in measurements:
                item_w_area = measurements[item_tag] + item_w_area
            measurements[item_tag] = item_w_area
            
    f.close()
    
    return measurements