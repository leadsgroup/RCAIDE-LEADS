## @ingroup Methods-Noise-Frequency_Domain_Buildup-Rotor
# RCAIDE/Methods/Noise/Frequency_Domain_Buildup/Rotor/broadband_noise.py
# 
# 
# Created:  Sep 2024, Niranjan Nanjappa  

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE 
from RCAIDE.Framework.Core import Units 
from RCAIDE.Library.Methods.Noise.Common.decibel_arithmetic                                    import SPL_arithmetic 
from RCAIDE.Library.Methods.Noise.Common.decibel_arithmetic                                    import SPL_average  
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.BPM_boundary_layer_properties import BPM_boundary_layer_properties
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.LBL_VS_broadband_noise        import LBL_VS_broadband_noise
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.TBL_TE_broadband_noise        import TBL_TE_broadband_noise
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.TIP_broadband_noise           import TIP_broadband_noise 
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.noise_directivities           import noise_directivities

# Python Package imports 
import numpy as np  
 
# ----------------------------------------------------------------------------------------------------------------------
# Compute Broadband Noise 
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Methods-Noise-Frequency_Domain_Buildup-Rotor
def broadband_noise_unsteady(freestream,angle_of_attack,coordinates,
                            velocity_vector,rotor,aeroacoustic_data,settings,res):
    '''This computes the trailing edge noise compoment of broadband noise of a propeller or 
    lift-rotor in the frequency domain. Boundary layer properties are computed using RCAIDE's 
    panel method.
    
    Assumptions:
        Boundary layer thickness (delta) appear to be an order of magnitude off at the trailing edge and 
        correction factor of 0.1 is used. See lines 255 and 256 
        
    Source: 
        Li, Sicheng Kevin, and Seongkyu Lee. "Prediction of Urban Air Mobility Multirotor VTOL Broadband Noise
        Using UCD-QuietFly." Journal of the American Helicopter Society (2021).
    
    Inputs:  
        freestream                                   - freestream data structure                                                          [m/s]
        angle_of_attack                              - aircraft angle of attack                                                           [rad]
        bspv                                         - rotor blade section trailing position edge vectors                                 [m]
        velocity_vector                              - velocity vector of aircraft                                                        [m/s]
        rotors                                       - data structure of rotors                                                           [None] 
        aeroacoustic_data                            - data structure of acoustic data                                                    [None] 
        settings                                     - accoustic settings                                                                 [None] 
        res                                          - results data structure                                                             [None] 
    
    Outputs 
       res.                                           *acoustic data is stored and passed in data structures*                                          
           SPL_prop_broadband_spectrum               - broadband noise in blade passing frequency spectrum                                [dB]
           SPL_prop_broadband_spectrum_dBA           - dBA-Weighted broadband noise in blade passing frequency spectrum                   [dbA]     
           SPL_prop_broadband_1_3_spectrum           - broadband noise in 1/3 octave spectrum                                             [dB]
           SPL_prop_broadband_1_3_spectrum_dBA       - dBA-Weighted broadband noise in 1/3 octave spectrum                                [dBA]                               
           p_pref_azimuthal_broadband                - azimuthal varying pressure ratio of broadband noise                                [Unitless]       
           p_pref_azimuthal_broadband_dBA            - azimuthal varying pressure ratio of dBA-weighted broadband noise                   [Unitless]     
           SPL_prop_azimuthal_broadband_spectrum     - azimuthal varying broadband noise in blade passing frequency spectrum              [dB]      
           SPL_prop_azimuthal_broadband_spectrum_dBA - azimuthal varying dBA-Weighted broadband noise in blade passing frequency spectrum [dbA]   
        
    Properties Used:
        N/A   
    '''     

    num_cpt       = len(coordinates.X[:,0,0,0,0,0])
    num_mic       = len(coordinates.X[0,:,0,0,0,0])  
    num_rot       = len(coordinates.X[0,0,:,0,0,0])
    num_blades    = len(coordinates.X[0,0,0,:,0,0])
    num_sec       = len(coordinates.X[0,0,0,0,:,0]) 
    frequency     = settings.center_frequencies
    num_cf        = len(frequency)
    num_az        = len(aeroacoustic_data.disc_azimuthal_distribution[0,0,:])
    
    # ----------------------------------------------------------------------------------
    # Trailing Edge Noise
    # ---------------------------------------------------------------------------------- 
    speed_of_sound     = freestream.speed_of_sound          # speed of sound
    density            = freestream.density                 # air density 
    dyna_visc          = freestream.dynamic_viscosity  
    alpha              = aeroacoustic_data.blade_effective_angle_of_attack/Units.degrees 
    alpha_tip          = aeroacoustic_data.blade_effective_angle_of_attack[:,-1]/Units.degrees  
    blade_Re           = aeroacoustic_data.blade_reynolds_number
    blade_speed        = aeroacoustic_data.blade_velocity
    blade_Ma           = aeroacoustic_data.blade_Mach_number
    Vt                 = aeroacoustic_data.blade_tangential_velocity  
    Va                 = aeroacoustic_data.blade_axial_velocity                
    blade_chords       = rotor.chord_distribution           # blade chord    
    r                  = rotor.radius_distribution          # radial location   
    Omega              = aeroacoustic_data.omega            # angular velocity    
    L                  = np.zeros_like(r)
    del_r              = r[1:] - r[:-1]
    L[0]               = del_r[0]
    L[-1]              = del_r[-1]
    L[1:-1]            = (del_r[:-1]+ del_r[1:])/2

    if np.all(Omega == 0):
        res.p_pref_broadband                          = np.zeros((num_cpt,num_mic,num_rot,num_cf)) 
        res.SPL_prop_broadband_spectrum               = np.zeros_like(res.p_pref_broadband)
        res.SPL_prop_broadband_spectrum_dBA           = np.zeros_like(res.p_pref_broadband)
        res.SPL_prop_broadband_1_3_spectrum           = np.zeros((num_cpt,num_mic,num_rot,num_cf))
        res.SPL_prop_broadband_1_3_spectrum_dBA       = np.zeros((num_cpt,num_mic,num_rot,num_cf))
        res.p_pref_azimuthal_broadband                = np.zeros((num_cpt,num_mic,num_rot,num_cf))
        res.p_pref_azimuthal_broadband_dBA            = np.zeros_like(res.p_pref_azimuthal_broadband)
        res.SPL_prop_azimuthal_broadband_spectrum     = np.zeros_like(res.p_pref_azimuthal_broadband)
        res.SPL_prop_azimuthal_broadband_spectrum_dBA = np.zeros_like(res.p_pref_azimuthal_broadband)
    else: 
        # dimension of matrices [control pt, microphone, num rotors, num of blades, num of sections, num center frequencies, num azimuthal stations] 
        c                 = np.tile(blade_chords[None,None,None,None,:,None,None],(num_cpt,num_mic,num_rot,num_blades,1,num_cf,num_az))
        L                 = np.tile(L[None,None,None,None,:,None,None],(num_cpt,num_mic,num_rot,num_blades,1,num_cf,num_az))
        f                 = np.tile(frequency[None,None,None,None,None,:,None],(num_cpt,num_mic,num_rot,num_blades,num_sec,1,num_az))
            
        SPLb_sum_3 = np.zeros((num_cpt,num_mic,num_rot,num_blades,num_cf,num_az))
        
        alpha_blade       = np.tile(alpha[:,None,None,None,:,None,:],(1,num_mic,num_rot,num_blades,1,num_cf,1))
        V                 = np.zeros((num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az,3))
        V[:,:,:,:,:,:,:,0]  = -np.tile(Vt[:,None,None,None,:,None,None],(1,num_mic,num_rot,num_blades,1,num_cf,num_az)) 
        V[:,:,:,:,:,:,:,2]  = np.tile(Va[:,None,None,None,:,None,None],(1,num_mic,num_rot,num_blades,1,num_cf,num_az))  
        V_tot             = np.linalg.norm(V, axis=7)
        alpha_tip         = np.tile(alpha_tip[:,None,None,None,None,None,:],(1,num_mic,num_rot,num_blades,num_sec,num_cf,1))  
        c_0               = np.tile(speed_of_sound[:,:,None,None,None,None,None],(1,num_mic,num_rot,num_blades,num_sec,num_cf,num_az))
        rho               = np.tile(density[:,:,None,None,None,None,None],(1,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)) 
        mu                = np.tile(dyna_visc[:,:,None,None,None,None,None],(1,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)) 
        R_c               = np.tile(blade_Re[:,None,None,None,:,None,:],(1,num_mic,num_rot,num_blades,1,num_cf,1))
        U                 = np.tile(blade_speed[:,None,None,None,:,None,:],(1,num_mic,num_rot,num_blades,1,num_cf,1))
        M                 = np.tile(blade_Ma[:,None,None,None,:,None,:],(1,num_mic,num_rot,num_blades,1,num_cf,1)) # U/c_0 
        M_tot             = V_tot/c_0   
          
        X_prime_r         = np.tile(coordinates.X_prime_r[:,:,:,:,:,None,None,:],(1,1,1,1,1,num_cf,num_az,1))
        cos_zeta_r        = np.sum(X_prime_r*V, axis = 7)/(np.linalg.norm(X_prime_r, axis = 7)*V_tot) 
        r_er              = np.tile(np.linalg.norm(coordinates.X_e_r, axis = 5)[:,:,:,:,:,None,None],(1,1,1,1,1,num_cf,num_az))           
        Phi_er            = np.tile(coordinates.phi_e_r[:,:,:,:,:,None,None],(1,1,1,1,1,num_cf,num_az))
        Theta_er          = np.tile(coordinates.theta_e_r[:,:,:,:,:,None,None],(1,1,1,1,1,num_cf,num_az))    
        
        # flatten matrices 
        R_c        = flatten_matrix(R_c,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        c          = flatten_matrix(c,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        alpha_star = flatten_matrix(alpha_blade,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        alpha_tip  = flatten_matrix(alpha_tip,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        U          = flatten_matrix(U,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        cos_zeta_r = flatten_matrix(cos_zeta_r,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        M_tot      = flatten_matrix(M_tot,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        f          = flatten_matrix(f,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        c_0        = flatten_matrix(c_0,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        rho        = flatten_matrix(rho,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        r_er       = flatten_matrix(r_er,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        mu         = flatten_matrix(mu,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        L          = flatten_matrix(L,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        M          = flatten_matrix(M,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        Phi_er     = flatten_matrix(Phi_er,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        Theta_er   = flatten_matrix(Theta_er,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        
        
        # calculation of boundary layer properties, eqns 2 - 16   
        # boundary layer properies of tripped and untripped at 0 angle of attack   
        boundary_layer_data  = BPM_boundary_layer_properties(R_c,c,alpha_star)  
    
        # define simulation variables/constants   
        Re_delta_star_p_untripped = boundary_layer_data.delta_star_p_untripped*U*rho/mu
        Re_delta_star_p_tripped   = boundary_layer_data.delta_star_p_tripped*U*rho/mu  
    
        # calculation of directivitiy terms , eqns 24 - 50 
        Dbar_h, Dbar_l = noise_directivities(Theta_er,Phi_er,cos_zeta_r,M_tot) 
          
        # calculation of turbulent boundary layer - trailing edge noise,  eqns 24 - 50 
        SPL_TBL_TE_tripped   = TBL_TE_broadband_noise(f,r_er,L,U,M,R_c,Dbar_h,Dbar_l,Re_delta_star_p_tripped,
                                                  boundary_layer_data.delta_star_p_tripped,
                                                  boundary_layer_data.delta_star_s_tripped,
                                                  alpha_star) 
        
        SPL_TBL_TE_untripped = TBL_TE_broadband_noise(f,r_er,L,U,M,R_c,Dbar_h,Dbar_l,Re_delta_star_p_untripped,
                                                  boundary_layer_data.delta_star_p_untripped,
                                                  boundary_layer_data.delta_star_s_untripped,
                                                  alpha_star)  
      
        # calculation of laminar boundary layer - vortex shedding, eqns 53 - 60 
        SPL_LBL_VS = LBL_VS_broadband_noise(R_c,alpha_star,boundary_layer_data.delta_star_p_untripped,r_er,L,M,Dbar_h,f,U)
       
        # calculation of tip vortex noise, eqns 61 - 67 
        alpha_TIP = abs(alpha_tip)
        SPL_TIP   = TIP_broadband_noise(alpha_TIP,M,c,c_0,f,Dbar_h,r_er)  
         
        # TO DO : Compute BWI  
         
        # TO DO : Compute BVI 
        
        # Unflatten Matices 
        SPL_TBL_TE_tripped   = unflatten_matrix(SPL_TBL_TE_tripped,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az) 
        SPL_TBL_TE_untripped = unflatten_matrix(SPL_TBL_TE_untripped,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        SPL_LBL_VS           = unflatten_matrix(SPL_LBL_VS,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)
        
        # why are we considering the 0th element to be the tip when in the radial distribution array, the tip is the last element
        SPL_TIP              = unflatten_matrix(SPL_TIP,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az)[:,:,:,:,0,:,:]     
        
        # Sum broadband compoments along blade sections and blades to get noise per rotor 
        broadband_SPLs    = np.zeros((2,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az))
        broadband_SPLs[0] = SPL_TBL_TE_tripped 
        broadband_SPLs[1] = SPL_LBL_VS  
        SPLb_sum_1        = SPL_arithmetic(broadband_SPLs, sum_axis=0) 
        SPLb_sum_2        = SPL_arithmetic(SPLb_sum_1, sum_axis=4) 
        SPLb_sum_3        = 10*np.log10( 10**(SPLb_sum_2/10) + 10**(SPL_TIP/10) ) 
        
        # store results 
        res.SPL_prop_broadband_spectrum                   = SPL_arithmetic(SPLb_sum_3, sum_axis=3)
        res.SPL_prop_broadband_spectrum_avg               = SPL_average(res.SPL_prop_broadband_spectrum, avg_axis=4)
        res.SPL_prop_broadband_1_3_spectrum               = res.SPL_prop_broadband_spectrum     # already in 1/3 octave spectrum
        res.SPL_prop_broadband_1_3_spectrum_avg           = res.SPL_prop_broadband_spectrum_avg     # already in 1/3 octave spectrum
        
    return
 
def flatten_matrix(x,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az):
    return np.reshape(x,(num_cpt*num_mic*num_rot*num_blades*num_sec*num_cf*num_az))

# def flatten_matrix(x,*args):
#     size = 1
#     for item in args:
#         size *= item
#     return np.reshape(x,size)


def unflatten_matrix(x,num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az):
    return np.reshape(x,(num_cpt,num_mic,num_rot,num_blades,num_sec,num_cf,num_az))