## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Lift
#  generate_propeller_wake_distribution.py
# 
# Created:  Sep 2020, M. Clarke 
# Modified: May 2021, R. Erhard
#           Jul 2021, E. Botero
#           Jul 2021, R. Erhard

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# package imports
import numpy as np
from SUAVE.Core import Data 
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.compute_wake_contraction_matrix import compute_wake_contraction_matrix
from SUAVE.Methods.Geometry.Two_Dimensional.Cross_Section.Airfoil.import_airfoil_geometry import import_airfoil_geometry   

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Lift   
def generate_propeller_wake_distribution(props,identical,m,VD,init_timestep_offset, time, number_of_wake_timesteps,conditions ): 
    """ This generates the propeller wake control points used to compute the 
    influence of the wake

    Assumptions: 
    None

    Source:   
    None

    Inputs:  
    identical                - if all props are identical        [Bool]
    m                        - control point                     [Unitless] 
    VD                       - vortex distribution               
    prop                     - propeller/rotor data structure         
    init_timestep_offset     - intial time step                  [Unitless] 
    time                     - time                              [s]
    number_of_wake_timesteps - number of wake timesteps          [Unitless]
    conditions.
       noise.sources.propellers   -  propeller noise sources data structure
       
    Properties Used:
    N/A
    """    
    num_prop = len(props) 
    
    if identical:
        # All props are identical in geometry, so only the first one is unpacked
        prop_keys    = list(props.keys())
        prop_key     = prop_keys[0]
        prop         = props[prop_key]
        prop_outputs = conditions.noise.sources.propellers[prop_key]
        
        Bmax = int(prop.number_of_blades)
        nmax = int(prop_outputs.number_radial_stations - 1)
        
    else:
        # Props are unique, must find required matrix sizes to fit all vortex distributions
        prop_keys   = list(props.keys())
        B_list      = np.ones(len(prop_keys))
        Nr_list     = np.ones(len(prop_keys))
    
        for i in range(len(prop_keys)):
            p_key      = list(props.keys())[i]
            p          = props[p_key]
            p_out      = conditions.noise.sources.propellers[p_key]
            
            B_list[i]  = p.number_of_blades
            Nr_list[i] = p_out.number_radial_stations
            
        # Identify max indices for pre-allocating vortex wake distribution matrices
        Bmax = int(max(B_list))
        nmax = int(max(Nr_list)-1)
        
    # Initialize empty arrays with required sizes
    VD, WD, Wmid = initialize_distributions(nmax, Bmax, number_of_wake_timesteps, num_prop, m,VD)
    
    # for each propeller, unpack and compute 
    for i, propi in enumerate(props):
        propi_key        = list(props.keys())[i]
        if identical:
            propi_outputs = prop_outputs
        else:
            propi_outputs = conditions.noise.sources.propellers[propi_key]
        
        # Unpack
        R                = propi.tip_radius
        r                = propi.radius_distribution 
        c                = propi.chord_distribution 
        MCA              = propi.mid_chord_alignment 
        B                = propi.number_of_blades    
        
        Na               = propi_outputs.number_azimuthal_stations
        Nr               = propi_outputs.number_radial_stations
        omega            = propi_outputs.omega                               
        va               = propi_outputs.disc_axial_induced_velocity 
        V_inf            = propi_outputs.velocity
        gamma            = propi_outputs.disc_circulation
        
        blade_angles     = np.linspace(0,2*np.pi,B+1)[:-1]   
        dt               = time/number_of_wake_timesteps
        ts               = np.linspace(0,time,number_of_wake_timesteps) 
        
        t0                = dt*init_timestep_offset
        start_angle       = omega[0]*t0 
        propi.start_angle = start_angle[0]

        # define points ( control point, time step , blade number , location on blade )
        # compute lambda and mu 
        mean_induced_velocity  = np.mean( np.mean(va,axis = 1),axis = 1)   
    
        lambda_tot   =  np.atleast_2d((V_inf[:,0]  + mean_induced_velocity)).T /(omega*R)   # inflow advance ratio (page 30 Leishman)
        mu_prop      =  np.atleast_2d(V_inf[:,2]).T /(omega*R)                              # rotor advance ratio  (page 30 Leishman) 
        V_prop       =  np.atleast_2d(np.sqrt((V_inf[:,0]  + mean_induced_velocity)**2 + (V_inf[:,2])**2)).T
    
        # wake skew angle 
        wake_skew_angle = np.arctan(mu_prop/lambda_tot)
    
        # reshape gamma to find the average between stations 
        gamma_new = np.zeros((m,Na,(Nr-1))) #[control points, azimuth  , radial stations -1 ] one less because ring
        gamma_new = (gamma[:,:,:-1] + gamma[:,:,1:])*0.5 #  not sure if correct 


        num       = int(Na/B)  
        time_idx  = np.arange(number_of_wake_timesteps)#-1) 
        t_idx     = np.atleast_2d(time_idx).T 
        B_idx     = np.arange(B) 
        B_loc     = (B_idx*num + t_idx)%Na  
        Gamma     = gamma_new[:,B_loc,:]  
    
        #( control point, time step , blade number , location on blade )
        sx_inf0            = np.multiply(V_prop*np.cos(wake_skew_angle), np.atleast_2d(ts))
        sx_inf             = np.repeat(np.repeat(sx_inf0[:, :,  np.newaxis], Nr, axis = 2)[:,  : ,np.newaxis,  :], B, axis = 2)  
                          
        sy_inf0            = np.multiply(np.atleast_2d(V_inf[:,1]).T,np.atleast_2d(ts)) # = zero since no crosswind
        sy_inf             = np.repeat(np.repeat(sy_inf0[:, :,  np.newaxis], Nr, axis = 2)[:,  : ,np.newaxis,  :], B, axis = 2)   
                          
        sz_inf0            = np.multiply(V_prop*np.sin(wake_skew_angle),np.atleast_2d(ts))
        sz_inf             = np.repeat(np.repeat(sz_inf0[:, :,  np.newaxis], Nr, axis = 2)[:,  : ,np.newaxis,  :], B, axis = 2)           
    
        angle_offset       = np.repeat(np.repeat(np.multiply(omega,np.atleast_2d(ts))[:, :,  np.newaxis],B, axis = 2)[:, :,:, np.newaxis],Nr, axis = 3) 
        blade_angle_loc    = np.repeat(np.repeat(np.tile(np.atleast_2d(blade_angles),(m,1))[:,  np.newaxis, :],number_of_wake_timesteps, axis = 1) [:, :,:, np.newaxis],Nr, axis = 3) 
        start_angle_offset = np.repeat(np.repeat(np.atleast_2d(start_angle)[:, :, np.newaxis],B, axis = 2)[:, :,:, np.newaxis],Nr, axis = 3) 
        
        total_angle_offset = angle_offset - start_angle_offset
        
        if (propi.rotation != None) and (propi.rotation == 1):        
            total_angle_offset = -total_angle_offset

        azi_y   = np.sin(blade_angle_loc + total_angle_offset)  
        azi_z   = np.cos(blade_angle_loc + total_angle_offset)
        

        # extract airfoil trailing edge coordinates for initial location of vortex wake
        a_sec        = propi.airfoil_geometry   
        a_secl       = propi.airfoil_polar_stations
        airfoil_data = import_airfoil_geometry(a_sec,npoints=100)  
       
        # trailing edge points in airfoil coordinates
        xupper         = np.take(airfoil_data.x_upper_surface,a_secl,axis=0)   
        yupper         = np.take(airfoil_data.y_upper_surface,a_secl,axis=0)   
        xte_airfoils = xupper[:,-1]*c
        yte_airfoils = yupper[:,-1]*c
        
        xle_airfoils = xupper[:,0]*c
        yle_airfoils = yupper[:,0]*c        
        
        x_c_4_airfoils = (xle_airfoils - xte_airfoils)/4
        y_c_4_airfoils = (yle_airfoils - yte_airfoils)/4
        x_3c_4_airfoils = 3*(xle_airfoils - xte_airfoils)/4
        y_3c_4_airfoils = 3*(yle_airfoils - yte_airfoils)/4
        
        # apply blade twist rotation along rotor radius
        beta = propi.twist_distribution
        xte_twisted = np.cos(beta)*xte_airfoils - np.sin(beta)*yte_airfoils        
        yte_twisted = np.sin(beta)*xte_airfoils + np.cos(beta)*yte_airfoils    
        
        x_c_4_twisted = np.cos(beta)*x_c_4_airfoils - np.sin(beta)*y_c_4_airfoils 
        y_c_4_twisted = np.sin(beta)*x_c_4_airfoils + np.cos(beta)*y_c_4_airfoils  
        x_3c_4_twisted = np.cos(beta)*x_3c_4_airfoils - np.sin(beta)*y_3c_4_airfoils 
        y_3c_4_twisted = np.sin(beta)*x_3c_4_airfoils + np.cos(beta)*y_3c_4_airfoils  
        
        # transform coordinates from airfoil frame to rotor frame
        xte_rotor = np.tile(np.atleast_2d(yte_twisted), (B,1))
        yte_rotor = -xte_twisted*np.cos(blade_angle_loc+total_angle_offset)
        zte_rotor = xte_twisted*np.sin(blade_angle_loc+total_angle_offset)
        
        
        x0 = 0
        y0 = r*azi_y
        z0 = r*azi_z
        
        x_pts0 = x0 + xte_rotor
        y_pts0 = y0 + yte_rotor
        z_pts0 = z0 + zte_rotor
        
        x_c_4_rotor = x0 - np.tile(np.atleast_2d(y_c_4_twisted), (B,1))
        y_c_4_rotor = y0[0,0,:,:] + x_c_4_twisted*np.cos(blade_angle_loc[0,0,:,:]+total_angle_offset[0,0,:,:])
        z_c_4_rotor = z0[0,0,:,:] - x_c_4_twisted*np.sin(blade_angle_loc[0,0,:,:]+total_angle_offset[0,0,:,:])   
        x_3c_4_rotor = x0 - np.tile(np.atleast_2d(y_3c_4_twisted), (B,1))
        y_3c_4_rotor = y0[0,0,:,:] + x_3c_4_twisted*np.cos(blade_angle_loc[0,0,:,:]+total_angle_offset[0,0,:,:])
        z_3c_4_rotor = z0[0,0,:,:] - x_3c_4_twisted*np.sin(blade_angle_loc[0,0,:,:]+total_angle_offset[0,0,:,:])        
        
        x_pts  = np.repeat(np.repeat(x_pts0[np.newaxis,:,  :], number_of_wake_timesteps, axis=0)[ np.newaxis, : ,:, :,], m, axis=0) 
        X_pts0 = x_pts + sx_inf

        # compute wake contraction, apply to y-z plane
        wake_contraction = compute_wake_contraction_matrix(i,propi,Nr,m,number_of_wake_timesteps,X_pts0,propi_outputs)          
        Y_pts0           = y_pts0*wake_contraction + sy_inf
        Z_pts0           = z_pts0*wake_contraction + sz_inf
 
        # Rotate wake by thrust angle
        rot_mat = propi.prop_vel_to_body()
        
        # append propeller wake to each of its repeated origins  
        X_pts   = propi.origin[0][0] + X_pts0*rot_mat[0,0] - Z_pts0*rot_mat[0,2]   
        Y_pts   = propi.origin[0][1] + Y_pts0*rot_mat[1,1]                       
        Z_pts   = propi.origin[0][2] + X_pts0*rot_mat[2,0] + Z_pts0*rot_mat[2,2] 
        
        # prepend points at quarter chord to account for rotor lifting line
        x_c_4 = np.repeat(x_c_4_rotor[None,:,:], m,axis=0)
        y_c_4 = np.repeat(y_c_4_rotor[None,:,:], m,axis=0)
        z_c_4 = np.repeat(z_c_4_rotor[None,:,:], m,axis=0)
        
        X_pts = np.append(x_c_4[:,None,:,:], X_pts, axis=1)
        Y_pts = np.append(y_c_4[:,None,:,:], Y_pts, axis=1)
        Z_pts = np.append(z_c_4[:,None,:,:], Z_pts, axis=1)
        

        # Store points  
        # ( control point,  prop ,  time step , blade number , location on blade )
        if (propi.rotation != None) and (propi.rotation == -1):  
            Wmid.WD_XA1[:,i,:,0:B,:] = X_pts[: , :-1 , : , :-1 ]
            Wmid.WD_YA1[:,i,:,0:B,:] = Y_pts[: , :-1 , : , :-1 ]
            Wmid.WD_ZA1[:,i,:,0:B,:] = Z_pts[: , :-1 , : , :-1 ]
            Wmid.WD_XA2[:,i,:,0:B,:] = X_pts[: ,  1: , : , :-1 ]
            Wmid.WD_YA2[:,i,:,0:B,:] = Y_pts[: ,  1: , : , :-1 ]
            Wmid.WD_ZA2[:,i,:,0:B,:] = Z_pts[: ,  1: , : , :-1 ]
            Wmid.WD_XB1[:,i,:,0:B,:] = X_pts[: , :-1 , : , 1:  ]
            Wmid.WD_YB1[:,i,:,0:B,:] = Y_pts[: , :-1 , : , 1:  ]
            Wmid.WD_ZB1[:,i,:,0:B,:] = Z_pts[: , :-1 , : , 1:  ]
            Wmid.WD_XB2[:,i,:,0:B,:] = X_pts[: ,  1: , : , 1:  ]
            Wmid.WD_YB2[:,i,:,0:B,:] = Y_pts[: ,  1: , : , 1:  ]
            Wmid.WD_ZB2[:,i,:,0:B,:] = Z_pts[: ,  1: , : , 1:  ] 
        else: 
            Wmid.WD_XA1[:,i,:,0:B,:] = X_pts[: , :-1 , : , 1:  ]
            Wmid.WD_YA1[:,i,:,0:B,:] = Y_pts[: , :-1 , : , 1:  ]
            Wmid.WD_ZA1[:,i,:,0:B,:] = Z_pts[: , :-1 , : , 1:  ]
            Wmid.WD_XA2[:,i,:,0:B,:] = X_pts[: ,  1: , : , 1:  ]
            Wmid.WD_YA2[:,i,:,0:B,:] = Y_pts[: ,  1: , : , 1:  ]
            Wmid.WD_ZA2[:,i,:,0:B,:] = Z_pts[: ,  1: , : , 1:  ] 
            Wmid.WD_XB1[:,i,:,0:B,:] = X_pts[: , :-1 , : , :-1 ]
            Wmid.WD_YB1[:,i,:,0:B,:] = Y_pts[: , :-1 , : , :-1 ]
            Wmid.WD_ZB1[:,i,:,0:B,:] = Z_pts[: , :-1 , : , :-1 ]
            Wmid.WD_XB2[:,i,:,0:B,:] = X_pts[: ,  1: , : , :-1 ]
            Wmid.WD_YB2[:,i,:,0:B,:] = Y_pts[: ,  1: , : , :-1 ]
            Wmid.WD_ZB2[:,i,:,0:B,:] = Z_pts[: ,  1: , : , :-1 ]

        Wmid.WD_GAMMA[:,i,:,0:B,:] = Gamma 

        # store points for plotting 
        VD.Wake.XA1[i,:,0:B,:] =  X_pts[0 , :-1 , : , :-1 ]
        VD.Wake.YA1[i,:,0:B,:] =  Y_pts[0 , :-1 , : , :-1 ]
        VD.Wake.ZA1[i,:,0:B,:] =  Z_pts[0 , :-1 , : , :-1 ]
        VD.Wake.XA2[i,:,0:B,:] =  X_pts[0 ,  1: , : , :-1 ]
        VD.Wake.YA2[i,:,0:B,:] =  Y_pts[0 ,  1: , : , :-1 ]
        VD.Wake.ZA2[i,:,0:B,:] =  Z_pts[0 ,  1: , : , :-1 ]
        VD.Wake.XB1[i,:,0:B,:] =  X_pts[0 , :-1 , : , 1:  ]
        VD.Wake.YB1[i,:,0:B,:] =  Y_pts[0 , :-1 , : , 1:  ]
        VD.Wake.ZB1[i,:,0:B,:] =  Z_pts[0 , :-1 , : , 1:  ]
        VD.Wake.XB2[i,:,0:B,:] =  X_pts[0 ,  1: , : , 1:  ]
        VD.Wake.YB2[i,:,0:B,:] =  Y_pts[0 ,  1: , : , 1:  ]
        VD.Wake.ZB2[i,:,0:B,:] =  Z_pts[0 ,  1: , : , 1:  ]  
        
        # Append wake geometry and vortex strengths to each individual propeller
        propi.Wake_VD.XA1   = VD.Wake.XA1[i,:,0:B,:]
        propi.Wake_VD.YA1   = VD.Wake.YA1[i,:,0:B,:]
        propi.Wake_VD.ZA1   = VD.Wake.ZA1[i,:,0:B,:]
        propi.Wake_VD.XA2   = VD.Wake.XA2[i,:,0:B,:]
        propi.Wake_VD.YA2   = VD.Wake.YA2[i,:,0:B,:]
        propi.Wake_VD.ZA2   = VD.Wake.ZA2[i,:,0:B,:]
        propi.Wake_VD.XB1   = VD.Wake.XB1[i,:,0:B,:]
        propi.Wake_VD.YB1   = VD.Wake.YB1[i,:,0:B,:]
        propi.Wake_VD.ZB1   = VD.Wake.ZB1[i,:,0:B,:]
        propi.Wake_VD.XB2   = VD.Wake.XB2[i,:,0:B,:]
        propi.Wake_VD.YB2   = VD.Wake.YB2[i,:,0:B,:]
        propi.Wake_VD.ZB2   = VD.Wake.ZB2[i,:,0:B,:]
        propi.Wake_VD.GAMMA = Wmid.WD_GAMMA[:,i,:,0:B,:]
        
        # append trailing edge locations
        propi.Wake_VD.Xblades_te = X_pts[0,0,:,:]
        propi.Wake_VD.Yblades_te = Y_pts[0,0,:,:]
        propi.Wake_VD.Zblades_te = Z_pts[0,0,:,:]

        # append quarter chord lifting line point locations        
        propi.Wake_VD.Xblades_c_4 = x_c_4_rotor 
        propi.Wake_VD.Yblades_c_4 = y_c_4_rotor#[0,0,:,:] 
        propi.Wake_VD.Zblades_c_4 = z_c_4_rotor#[0,0,:,:]  
        
        # append three-quarter chord evaluation point locations        
        propi.Wake_VD.Xblades_cp = x_3c_4_rotor  
        propi.Wake_VD.Yblades_cp = y_3c_4_rotor#[0,0,:,:] 
        propi.Wake_VD.Zblades_cp = z_3c_4_rotor#[0,0,:,:]         
        

    # Compress Data into 1D Arrays  
    mat4_size = (m,num_prop,(number_of_wake_timesteps),Bmax*nmax)
    mat5_size = (m,num_prop,(number_of_wake_timesteps)*Bmax*nmax)
    mat6_size = (m,num_prop*(number_of_wake_timesteps)*Bmax*nmax) 

    WD.XA1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_XA1,mat4_size),mat5_size),mat6_size)
    WD.YA1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_YA1,mat4_size),mat5_size),mat6_size)
    WD.ZA1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_ZA1,mat4_size),mat5_size),mat6_size)
    WD.XA2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_XA2,mat4_size),mat5_size),mat6_size)
    WD.YA2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_YA2,mat4_size),mat5_size),mat6_size)
    WD.ZA2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_ZA2,mat4_size),mat5_size),mat6_size)
    WD.XB1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_XB1,mat4_size),mat5_size),mat6_size)
    WD.YB1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_YB1,mat4_size),mat5_size),mat6_size)
    WD.ZB1    =  np.reshape(np.reshape(np.reshape(Wmid.WD_ZB1,mat4_size),mat5_size),mat6_size)
    WD.XB2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_XB2,mat4_size),mat5_size),mat6_size)
    WD.YB2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_YB2,mat4_size),mat5_size),mat6_size)
    WD.ZB2    =  np.reshape(np.reshape(np.reshape(Wmid.WD_ZB2,mat4_size),mat5_size),mat6_size)
    WD.GAMMA  =  np.reshape(np.reshape(np.reshape(Wmid.WD_GAMMA,mat4_size),mat5_size),mat6_size)

    return WD, dt, ts, B, Nr 


def initialize_distributions(nmax, Bmax, n_wts, n_props, m,VD):
    
    Wmid        = Data()
    mat1_size = (m,n_props,n_wts,Bmax,nmax)
    Wmid.WD_XA1    = np.zeros(mat1_size)  
    Wmid.WD_YA1    = np.zeros(mat1_size)  
    Wmid.WD_ZA1    = np.zeros(mat1_size)  
    Wmid.WD_XA2    = np.zeros(mat1_size)  
    Wmid.WD_YA2    = np.zeros(mat1_size)  
    Wmid.WD_ZA2    = np.zeros(mat1_size)      
    Wmid.WD_XB1    = np.zeros(mat1_size)  
    Wmid.WD_YB1    = np.zeros(mat1_size)  
    Wmid.WD_ZB1    = np.zeros(mat1_size)  
    Wmid.WD_XB2    = np.zeros(mat1_size)   
    Wmid.WD_YB2    = np.zeros(mat1_size)   
    Wmid.WD_ZB2    = np.zeros(mat1_size)     
    Wmid.WD_GAMMA  = np.zeros(mat1_size)     

    WD        = Data()
    mat2_size = (m,n_props*(n_wts-1)*Bmax*nmax)
    WD.XA1    = np.zeros(mat2_size)
    WD.YA1    = np.zeros(mat2_size)
    WD.ZA1    = np.zeros(mat2_size)
    WD.XA2    = np.zeros(mat2_size)
    WD.YA2    = np.zeros(mat2_size)
    WD.ZA2    = np.zeros(mat2_size)   
    WD.XB1    = np.zeros(mat2_size)
    WD.YB1    = np.zeros(mat2_size)
    WD.ZB1    = np.zeros(mat2_size)
    WD.XB2    = np.zeros(mat2_size)
    WD.YB2    = np.zeros(mat2_size)
    WD.ZB2    = np.zeros(mat2_size) 

    VD.Wake       = Data()
    mat3_size     = (n_props,(n_wts),Bmax,nmax)
    VD.Wake.XA1   = np.zeros(mat3_size) 
    VD.Wake.YA1   = np.zeros(mat3_size) 
    VD.Wake.ZA1   = np.zeros(mat3_size) 
    VD.Wake.XA2   = np.zeros(mat3_size) 
    VD.Wake.YA2   = np.zeros(mat3_size) 
    VD.Wake.ZA2   = np.zeros(mat3_size)    
    VD.Wake.XB1   = np.zeros(mat3_size) 
    VD.Wake.YB1   = np.zeros(mat3_size) 
    VD.Wake.ZB1   = np.zeros(mat3_size) 
    VD.Wake.XB2   = np.zeros(mat3_size) 
    VD.Wake.YB2   = np.zeros(mat3_size) 
    VD.Wake.ZB2   = np.zeros(mat3_size) 
    
    return VD, WD, Wmid