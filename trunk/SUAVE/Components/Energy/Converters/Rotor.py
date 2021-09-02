## @ingroup Components-Energy-Converters
# Rotor.py
#
# Created:  Jun 2014, E. Botero
# Modified: Jan 2016, T. MacDonald
#           Feb 2019, M. Vegh            
#           Mar 2020, M. Clarke
#           Sep 2020, M. Clarke 
#           Mar 2021, R. Erhard
#           Apr 2021, M. Clarke
#           Jul 2021, E. Botero
#           Jul 2021, R. Erhard

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
from SUAVE.Core import Data, Units
from SUAVE.Components.Energy.Energy_Component import Energy_Component
from SUAVE.Methods.Geometry.Three_Dimensional \
     import  orientation_product, orientation_transpose

from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.generate_propeller_wake_distribution import generate_propeller_wake_distribution
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.compute_wake_induced_velocity import compute_wake_induced_velocity

# package imports
import numpy as np
import scipy as sp

# ----------------------------------------------------------------------
#  Generalized Rotor Class
# ----------------------------------------------------------------------    
## @ingroup Components-Energy-Converters
class Rotor(Energy_Component):
    """This is a general rotor component.
    
    Assumptions:
    None

    Source:
    None
    """     
    def __defaults__(self):
        """This sets the default values for the component to function.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """         
        
        self.tag                       = 'rotor'
        self.number_of_blades          = 0.0 
        self.tip_radius                = 0.0
        self.hub_radius                = 0.0
        self.twist_distribution        = 0.0
        self.chord_distribution        = 0.0
        self.mid_chord_alignment       = 0.0
        self.thickness_to_chord        = 0.0
        self.blade_solidity            = 0.0
        self.design_power              = None
        self.design_thrust             = None    
        self.airfoil_geometry          = None
        self.airfoil_polars            = None
        self.airfoil_polar_stations    = None 
        self.radius_distribution       = None
        self.rotation                  = 1
        self.orientation_euler_angles  = [0.,0.,0.]   # This is X-direction thrust in vehicle frame
        self.ducted                    = False 
        self.number_azimuthal_stations = 24
        self.induced_power_factor      = 1.48         # accounts for interference effects
        self.profile_drag_coefficient  = .03      
        
        self.use_2d_analysis           = False    # True if rotor is at an angle relative to freestream or nonuniform freestream
        self.nonuniform_freestream     = False 
        self.axial_velocities_2d       = None     # user input for additional velocity influences at the rotor
        self.tangential_velocities_2d  = None     # user input for additional velocity influences at the rotor
        self.radial_velocities_2d      = None     # user input for additional velocity influences at the rotor        
        
        self.Wake_VD                   = Data()
        self.wake_method               = "momentum"
        self.wake_settings             = Data()
        
        self.wake_settings.initial_timestep_offset   = 0
        self.wake_settings.wake_development_time     = 0.05
        self.wake_settings.number_of_wake_timesteps  = 30   
        
        self.inputs.y_axis_rotation    = 0.
        self.inputs.pitch_command      = 0.
        self.variable_pitch            = False

    def spin(self,conditions):
        """Analyzes a general rotor given geometry and operating conditions.

        Assumptions:
        per source

        Source:
        Drela, M. "Qprop Formulation", MIT AeroAstro, June 2006
        http://web.mit.edu/drela/Public/web/qprop/qprop_theory.pdf
        
        Leishman, Gordon J. Principles of helicopter aerodynamics
        Cambridge university press, 2006.      

        Inputs:
        self.inputs.omega                    [radian/s]
        conditions.freestream.               
          density                            [kg/m^3]
          dynamic_viscosity                  [kg/(m-s)]
          speed_of_sound                     [m/s]
          temperature                        [K]
        conditions.frames.                   
          body.transform_to_inertial         (rotation matrix)
          inertial.velocity_vector           [m/s]
        conditions.propulsion.               
          throttle                           [-]
                                             
        Outputs:                             
        conditions.propulsion.outputs.        
           number_radial_stations            [-]
           number_azimuthal_stations         [-] 
           disc_radial_distribution          [m]
           speed_of_sound                    [m/s]
           density                           [kg/m-3]
           velocity                          [m/s]
           disc_tangential_induced_velocity  [m/s]
           disc_axial_induced_velocity       [m/s]
           disc_tangential_velocity          [m/s]
           disc_axial_velocity               [m/s]
           drag_coefficient                  [-]
           lift_coefficient                  [-]
           omega                             [rad/s]
           disc_circulation                  [-] 
           blade_dQ_dR                       [N/m]
           blade_dT_dr                       [N]
           blade_thrust_distribution         [N]
           disc_thrust_distribution          [N]
           thrust_per_blade                  [N]
           thrust_coefficient                [-] 
           azimuthal_distribution            [rad]
           disc_azimuthal_distribution       [rad]
           blade_dQ_dR                       [N]
           blade_dQ_dr                       [Nm]
           blade_torque_distribution         [Nm] 
           disc_torque_distribution          [Nm] 
           torque_per_blade                  [Nm] 
           torque_coefficient                [-] 
           power                             [W]    
           power_coefficient                 [-] 
                                             
        Properties Used:                     
        self.                                
          number_of_blades                   [-]
          tip_radius                         [m]
          twist_distribution                 [radians]
          chord_distribution                 [m]
          orientation_euler_angles           [rad, rad, rad]
        """         
           
        # Unpack rotor blade parameters
        B       = self.number_of_blades 
        R       = self.tip_radius
        beta_0  = self.twist_distribution
        c       = self.chord_distribution
        r_1d    = self.radius_distribution 
        tc      = self.thickness_to_chord 
        
        # Unpack rotor airfoil data
        a_geo   = self.airfoil_geometry      
        a_loc   = self.airfoil_polar_stations  
        cl_sur  = self.airfoil_cl_surrogates
        cd_sur  = self.airfoil_cd_surrogates  
          
        # Unpack rotor inputs and conditions
        omega                 = self.inputs.omega
        Na                    = self.number_azimuthal_stations 
        nonuniform_freestream = self.nonuniform_freestream
        use_2d_analysis       = self.use_2d_analysis
        wake_method           = self.wake_method
        rotation              = self.rotation           
        pitch_c               = self.inputs.pitch_command  
        
        # Check for variable pitch
        if np.any(pitch_c !=0) and not self.variable_pitch:
            print("Warning: pitch commanded for a fixed-pitch rotor. Changing to variable pitch rotor for weights analysis.")
            self.variable_pitch = True
        
        # Unpack freestream conditions
        rho     = conditions.freestream.density[:,0,None]
        mu      = conditions.freestream.dynamic_viscosity[:,0,None]
        a       = conditions.freestream.speed_of_sound[:,0,None]
        T       = conditions.freestream.temperature[:,0,None]
        Vv      = conditions.frames.inertial.velocity_vector 
        nu      = mu/rho   
        rho_0   = rho
        
        # Helpful shorthands
        BB      = B*B    
        BBB     = BB*B
        pi      = np.pi        
        pi2     = pi*pi         
     
        # Calculate total blade pitch
        total_blade_pitch = beta_0 + pitch_c
    
        # Velocity in the rotor frame
        T_body2inertial = conditions.frames.body.transform_to_inertial
        T_inertial2body = orientation_transpose(T_body2inertial)
        V_body          = orientation_product(T_inertial2body,Vv)
        body2thrust     = self.body_to_prop_vel()
        T_body2thrust   = orientation_transpose(np.ones_like(T_body2inertial[:])*body2thrust)
        V_thrust        = orientation_product(T_body2thrust,V_body) 
        
        # Check and correct for hover
        V         = V_thrust[:,0,None]  
        V[V==0.0] = 1E-6
        
        #Things that don't change with iteration
        Nr       = len(c) # Number of stations radially    
        ctrl_pts = len(Vv)
                 
        # Non-dimensional radial distribution and differential radius
        chi           = r_1d/R 
        diff_r        = np.diff(r_1d)
        deltar        = np.zeros(len(r_1d))
        deltar[1:-1]  = diff_r[0:-1]/2 + diff_r[1:]/2
        deltar[0]     = diff_r[0]/2
        deltar[-1]    = diff_r[-1]/2 
        
        # Calculating rotational parameters
        omegar   = np.outer(omega,r_1d)    
        n        = omega/(2.*pi)   # Rotations per second  
    
        # Azimuthal distribution of stations
        psi            = np.linspace(0,2*pi,Na+1)[:-1]
        psi_2d         = np.tile(np.atleast_2d(psi).T,(1,Nr))
        psi_2d         = np.repeat(psi_2d[np.newaxis, :, :], ctrl_pts, axis=0)   
        
        # 2 dimensiona radial distribution non dimensionalized
        chi_2d         = np.tile(chi ,(Na,1))            
        chi_2d         = np.repeat(chi_2d[None,:,:], ctrl_pts, axis=0) 
        r_dim_2d       = np.tile(r_1d ,(Na,1))  
        r_dim_2d       = np.repeat(r_dim_2d[None,:,:], ctrl_pts, axis=0)          
        c_2d           = np.tile(c ,(Na,1)) 
        c_2d           = np.repeat(c_2d[None,:,:], ctrl_pts, axis=0)  
        
        # Starting with uniform freestream
        ua       = 0             
        ut       = 0            
        ur       = 0             
        
        # Include velocities introduced by rotor incidence angles 
        if (np.any(abs(V_thrust[:,1]) >1e-3) or np.any(abs(V_thrust[:,2]) >1e-3)) and use_2d_analysis:
            
            # y-component of freestream in the propeller plane
            Vy  = V_thrust[:,1,None,None]
            Vy  = np.repeat(Vy, Na,axis=1)
            Vy  = np.repeat(Vy, Nr,axis=2)
            
            # z-component of freestream in the propeller plane
            Vz  = V_thrust[:,2,None,None]
            Vz  = np.repeat(Vz, Na,axis=1)
            Vz  = np.repeat(Vz, Nr,axis=2)            
            
            # check for invalid rotation angle
            if (rotation == 1) or (rotation == -1):  
                pass
            else: 
                print("Invalid rotation direction. Setting to 1.")
                rotation = 1
            
            # compute resulting radial and tangential velocities in rotational frame
            utz =  Vz*np.cos(psi_2d) * rotation
            urz = -Vz*np.sin(psi_2d)
            uty = -Vy*np.sin(psi_2d) * rotation
            ury = -Vy*np.cos(psi_2d)
            
            ut +=  (utz + uty)
            ur +=  (urz + ury)
            ua +=  np.zeros_like(ut)
            
        # Include external velocities introduced by user  
        if nonuniform_freestream:
            use_2d_analysis   = True

            # include additional influences specified at rotor sections, shape=(ctrl_pts,Na,Nr)
            ua += self.axial_velocities_2d
            ut += self.tangential_velocities_2d
            ur += self.radial_velocities_2d        
        
                
        if use_2d_analysis:
            # make everything 2D with shape (ctrl_pts,Na,Nr)
            size   = (ctrl_pts,Na,Nr)
            PSI    = np.ones(size)
            PSIold = np.zeros(size)
            
            # 2-D freestream velocity and omega*r
            V_2d   = V_thrust[:,0,None,None]
            V_2d   = np.repeat(V_2d, Na,axis=1)
            V_2d   = np.repeat(V_2d, Nr,axis=2)
            omegar = (np.repeat(np.outer(omega,r_1d)[:,None,:], Na, axis=1))
            
            # total velocities
            Ua     = V_2d + ua      
            
            # 2-D blade pitch and radial distributions
            if np.size(pitch_c)>1:
                # control variable is the blade pitch, repeat around azimuth
                beta = np.repeat(total_blade_pitch[:,None,:], Na, axis=1)
            else:
                beta = np.tile(total_blade_pitch,(Na ,1))
                beta = np.repeat(beta[np.newaxis,:, :], ctrl_pts, axis=0)
            r    = np.tile(r_1d,(Na ,1))
            r    = np.repeat(r[np.newaxis,:, :], ctrl_pts, axis=0) 
            
            # 2-D atmospheric properties
            a   = np.tile(np.atleast_2d(a),(1,Nr))
            a   = np.repeat(a[:, np.newaxis,  :], Na, axis=1)  
            nu  = np.tile(np.atleast_2d(nu),(1,Nr))
            nu  = np.repeat(nu[:, np.newaxis,  :], Na, axis=1)    
            rho = np.tile(np.atleast_2d(rho),(1,Nr))
            rho = np.repeat(rho[:, np.newaxis,  :], Na, axis=1)  
            T   = np.tile(np.atleast_2d(T),(1,Nr))
            T   = np.repeat(T[:, np.newaxis,  :], Na, axis=1)              
            
        else:
            # total velocities
            r      = r_1d
            Ua     = np.outer((V + ua),np.ones_like(r))
            beta   = total_blade_pitch
            
            # Things that will change with iteration
            size   = (ctrl_pts,Nr)
            PSI    = np.ones(size)
            PSIold = np.zeros(size)  
        
        
        # Total velocities
        Ut     = omegar - ut
        U      = np.sqrt(Ua*Ua + Ut*Ut + ur*ur) 
        
        if wake_method == "momentum":
            # perform a Newton iteration for BEMT
            # Setup a Newton iteration
            diff   = 1.
            tol    = 1e-6  # Convergence tolerance
            ii     = 0             
            
            # BEMT Iteration
            while (diff>tol):
                sin_psi      = np.sin(PSI)
                cos_psi      = np.cos(PSI)
                Wa           = 0.5*Ua + 0.5*U*sin_psi
                Wt           = 0.5*Ut + 0.5*U*cos_psi
                va           = Wa - Ua
                vt           = Ut - Wt
                alpha        = beta - np.arctan2(Wa,Wt)
                W            = (Wa*Wa + Wt*Wt)**0.5
                Ma           = W/a        # a is the speed of sound  
                lamdaw       = r*Wa/(R*Wt)
                
                # Limiter to keep from Nan-ing
                lamdaw[lamdaw<0.] = 0.
                f            = (B/2.)*(1.-r/R)/lamdaw
                f[f<0.]      = 0.
                piece        = np.exp(-f)
                arccos_piece = np.arccos(piece)
                F            = 2.*arccos_piece/pi
                Gamma        = vt*(4.*pi*r/B)*F*(1.+(4.*lamdaw*R/(pi*B*r))*(4.*lamdaw*R/(pi*B*r)))**0.5
                Re           = (W*c)/nu
                
                # Compute aerodynamic forces based on specified input airfoil or surrogate
                Cl, Cdval = compute_aerodynamic_forces(a_loc, a_geo, cl_sur, cd_sur, ctrl_pts, Nr, Na, Re, Ma, alpha, tc, use_2d_analysis)
                
                # Newton residual
                Rsquiggly   = Gamma - 0.5*W*c*Cl
            
                # An analytical derivative for dR_dpsi, this is derived by taking a derivative of the above equations
                # This was solved symbolically in Matlab and exported        
                f_wt_2      = 4*Wt*Wt
                f_wa_2      = 4*Wa*Wa
                Ucospsi     = U*cos_psi
                Usinpsi     = U*sin_psi
                Utcospsi    = Ut*cos_psi
                Uasinpsi    = Ua*sin_psi 
                UapUsinpsi  = (Ua + Usinpsi)
                utpUcospsi  = (Ut + Ucospsi) 
                utpUcospsi2 = utpUcospsi*utpUcospsi
                UapUsinpsi2 = UapUsinpsi*UapUsinpsi 
                dR_dpsi     = ((4.*U*r*arccos_piece*sin_psi*((16.*UapUsinpsi2)/(BB*pi2*f_wt_2) + 1.)**(0.5))/B - 
                               (pi*U*(Ua*cos_psi - Ut*sin_psi)*(beta - np.arctan((Wa+Wa)/(Wt+Wt))))/(2.*(f_wt_2 + f_wa_2)**(0.5))
                               + (pi*U*(f_wt_2 +f_wa_2)**(0.5)*(U + Utcospsi  +  Uasinpsi))/(2.*(f_wa_2/(f_wt_2) + 1.)*utpUcospsi2)
                               - (4.*U*piece*((16.*UapUsinpsi2)/(BB*pi2*f_wt_2) + 1.)**(0.5)*(R - r)*(Ut/2. - 
                                (Ucospsi)/2.)*(U + Utcospsi + Uasinpsi ))/(f_wa_2*(1. - np.exp(-(B*(Wt+Wt)*(R - 
                                r))/(r*(Wa+Wa))))**(0.5)) + (128.*U*r*arccos_piece*(Wa+Wa)*(Ut/2. - (Ucospsi)/2.)*(U + 
                                Utcospsi  + Uasinpsi ))/(BBB*pi2*utpUcospsi*utpUcospsi2*((16.*f_wa_2)/(BB*pi2*f_wt_2) + 1.)**(0.5))) 
            
                dR_dpsi[np.isnan(dR_dpsi)] = 0.1
            
                dpsi        = -Rsquiggly/dR_dpsi
                PSI         = PSI + dpsi
                diff        = np.max(abs(PSIold-PSI))
                PSIold      = PSI
            
                # omega = 0, do not run BEMT convergence loop 
                if all(omega[:,0]) == 0. :              
                    break
                
                # If its really not going to converge
                if np.any(PSI>pi/2) and np.any(dpsi>0.0):
                    print("Rotor BEMT did not converge to a solution (Stall)")
                    break
            
                ii+=1 
                if ii>10000:
                    print("Rotor BEMT did not converge to a solution (Iteration Limit)")
                    break
                
            # correction for velocities, since tip loss correction is only applied to loads in prior BEMT iteration
            va = F*va
            vt = F*vt  
            
        elif wake_method == "helical_fixed_wake":
            # compute induced velocities at blade by wake, 
            va, vt = compute_HFW_blade_velocities(self, self.outputs)
        
            
            # Skip Newton iteration, use va,vt directly (external optimizer is used to converge)
            Wa = va + Ua
            Wt = Ut - vt
        
            alpha        = beta - np.arctan2(Wa,Wt)
            W            = (Wa*Wa + Wt*Wt)**0.5
            Ma           = W/a        # a is the speed of sound  
            lamdaw       = r*Wa/(R*Wt)
        
            # Limiter to keep from Nan-ing
            lamdaw[lamdaw<0.] = 0.
            f            = (B/2.)*(1.-r/R)/lamdaw
            f[f<0.]      = 0.
            piece        = np.exp(-f)
            arccos_piece = np.arccos(piece)
            F            = 2.*arccos_piece/pi
            Gamma        = vt*(4.*pi*r/B)*F*(1.+(4.*lamdaw*R/(pi*B*r))*(4.*lamdaw*R/(pi*B*r)))**0.5
            Re           = (W*c)/nu
        
            # Compute aerodynamic forces based on specified input airfoil or surrogate
            Cl, Cdval = compute_aerodynamic_forces(a_loc, a_geo, cl_sur, cd_sur, ctrl_pts, Nr, Na, Re, Ma, alpha, tc, use_2d_analysis)
            
            Rsquiggly   = Gamma - 0.5*W*c*Cl
        
        # More Cd scaling from Mach from AA241ab notes for turbulent skin friction
        Tw_Tinf     = 1. + 1.78*(Ma*Ma)
        Tp_Tinf     = 1. + 0.035*(Ma*Ma) + 0.45*(Tw_Tinf-1.)
        Tp          = (Tp_Tinf)*T
        Rp_Rinf     = (Tp_Tinf**2.5)*(Tp+110.4)/(T+110.4) 
        Cd          = ((1/Tp_Tinf)*(1/Rp_Rinf)**0.2)*Cdval  
        
        epsilon                  = Cd/Cl
        epsilon[epsilon==np.inf] = 10. 

        # thrust and torque and their derivatives on the blade. 
        blade_T_distribution     = rho*(Gamma*(Wt-epsilon*Wa))*deltar 
        blade_Q_distribution     = rho*(Gamma*(Wa+epsilon*Wt)*r)*deltar 
        blade_dT_dr              = rho*(Gamma*(Wt-epsilon*Wa))
        blade_dQ_dr              = rho*(Gamma*(Wa+epsilon*Wt)*r)          
        
        if use_2d_analysis:
            blade_T_distribution_2d = blade_T_distribution
            blade_Q_distribution_2d = blade_Q_distribution
            blade_dT_dr_2d          = blade_dT_dr
            blade_dQ_dr_2d          = blade_dQ_dr
            blade_Gamma_2d          = Gamma
            alpha_2d                = alpha
            
            # set 1d blade loadings to be the average:
            blade_T_distribution    = np.mean((blade_T_distribution_2d), axis = 1)
            blade_Q_distribution    = np.mean((blade_Q_distribution_2d), axis = 1)  
            blade_dT_dr             = np.mean((blade_dT_dr_2d), axis = 1) 
            blade_dQ_dr             = np.mean((blade_dQ_dr_2d), axis = 1)
            
            Va_2d = Wa
            Vt_2d = Wt
            Va_avg = np.average(Wa, axis=1)      # averaged around the azimuth
            Vt_avg = np.average(Wt, axis=1)      # averaged around the azimuth
            
            Va_ind_2d  = va
            Vt_ind_2d  = vt
            Vt_ind_avg = np.average(vt, axis=1)
            Va_ind_avg = np.average(va, axis=1)   
            
            # compute the hub force / rotor drag distribution along the blade
            dL_2d    = 0.5*rho*c_2d*Cd*omegar**2*deltar
            dD_2d    = 0.5*rho*c_2d*Cl*omegar**2*deltar
            
            rotor_drag_distribution = np.mean(dL_2d*np.sin(psi_2d) + dD_2d*np.cos(psi_2d),axis=1)
            
        else:
            Va_2d   = np.repeat(Wa.T[ : , np.newaxis , :], Na, axis=1).T
            Vt_2d   = np.repeat(Wt.T[ : , np.newaxis , :], Na, axis=1).T
    
            blade_T_distribution_2d  = np.repeat(blade_T_distribution.T[ np.newaxis,:  , :], Na, axis=0).T 
            blade_Q_distribution_2d  = np.repeat(blade_Q_distribution.T[ np.newaxis,:  , :], Na, axis=0).T 
            blade_dT_dr_2d           = np.repeat(blade_dT_dr.T[ np.newaxis,:  , :], Na, axis=0).T 
            blade_dQ_dr_2d           = np.repeat(blade_dQ_dr.T[ np.newaxis,:  , :], Na, axis=0).T 
            blade_Gamma_2d           = np.repeat(Gamma.T[ : , np.newaxis , :], Na, axis=1).T
            alpha_2d                 = np.repeat(alpha.T[ : , np.newaxis , :], Na, axis=1).T

            Vt_avg                  = Wt
            Va_avg                  = Wa 
            Vt_ind_avg              = vt
            Va_ind_avg              = va            
            Va_ind_2d               = np.repeat(va.T[ : , np.newaxis , :], Na, axis=1).T
            Vt_ind_2d               = np.repeat(vt.T[ : , np.newaxis , :], Na, axis=1).T     
            
            # compute the hub force / rotor drag distribution along the blade
            dL    = 0.5*rho*c*Cd*omegar**2*deltar
            dL_2d = np.repeat(dL[:,None,:], Na, axis=1)
            dD    = 0.5*rho*c*Cl*omegar**2*deltar            
            dD_2d = np.repeat(dD[:,None,:], Na, axis=1)
            
            rotor_drag_distribution = np.mean(dL_2d*np.sin(psi_2d) + dD_2d*np.cos(psi_2d),axis=1)
        
       
        # forces
        thrust                  = np.atleast_2d((B * np.sum(blade_T_distribution, axis = 1))).T 
        torque                  = np.atleast_2d((B * np.sum(blade_Q_distribution, axis = 1))).T
        rotor_drag              = np.atleast_2d((B * np.sum(rotor_drag_distribution, axis=1))).T
        power                   = omega*torque   
        
        # calculate coefficients 
        D        = 2*R 
        Cq       = torque/(rho_0*(n*n)*(D*D*D*D*D)) 
        Ct       = thrust/(rho_0*(n*n)*(D*D*D*D))
        Cp       = power/(rho_0*(n*n*n)*(D*D*D*D*D))
        Crd      = rotor_drag/(rho_0*(n*n)*(D*D*D*D))
        etap     = V*thrust/power 
        
        # prevent things from breaking 
        Cq[Cq<0]                                               = 0.  
        Ct[Ct<0]                                               = 0.  
        Cp[Cp<0]                                               = 0.  
        thrust[conditions.propulsion.throttle[:,0] <=0.0]      = 0.0
        power[conditions.propulsion.throttle[:,0]  <=0.0]      = 0.0 
        torque[conditions.propulsion.throttle[:,0]  <=0.0]     = 0.0
        rotor_drag[conditions.propulsion.throttle[:,0]  <=0.0] = 0.0
        thrust[omega<0.0]                                      = - thrust[omega<0.0]  
        thrust[omega==0.0]                                     = 0.0
        power[omega==0.0]                                      = 0.0
        torque[omega==0.0]                                     = 0.0
        rotor_drag[omega==0.0]                                 = 0.0
        Ct[omega==0.0]                                         = 0.0
        Cp[omega==0.0]                                         = 0.0 
        etap[omega==0.0]                                       = 0.0           
          
        
        # Make the thrust a 3D vector
        thrust_prop_frame      = np.zeros((ctrl_pts,3))
        thrust_prop_frame[:,0] = thrust[:,0]
        thrust_vector          = orientation_product(orientation_transpose(T_body2thrust),thrust_prop_frame)
       
        # Assign efficiency to network
        conditions.propulsion.etap = etap 
        
        # Store data
        self.azimuthal_distribution                   = psi  
        results_conditions                            = Data     
        outputs                                       = results_conditions( 
                    number_radial_stations            = Nr,
                    number_azimuthal_stations         = Na,   
                    disc_radial_distribution          = r_dim_2d,  
                    speed_of_sound                    = conditions.freestream.speed_of_sound,
                    density                           = conditions.freestream.density,
                    velocity                          = Vv, 
                    blade_tangential_induced_velocity = Vt_ind_avg, 
                    blade_axial_induced_velocity      = Va_ind_avg,  
                    blade_tangential_velocity         = Vt_avg, 
                    blade_axial_velocity              = Va_avg,  
                    disc_tangential_induced_velocity  = Vt_ind_2d, 
                    disc_axial_induced_velocity       = Va_ind_2d,  
                    disc_tangential_velocity          = Vt_2d, 
                    disc_axial_velocity               = Va_2d, 
                    drag_coefficient                  = Cd,
                    lift_coefficient                  = Cl,       
                    omega                             = omega,  
                    disc_circulation                  = blade_Gamma_2d, 
                    blade_dT_dr                       = blade_dT_dr,
                    disc_dT_dr                        = blade_dT_dr_2d,
                    blade_thrust_distribution         = blade_T_distribution, 
                    disc_thrust_distribution          = blade_T_distribution_2d, 
                    disc_effective_angle_of_attack    = alpha_2d,
                    thrust_per_blade                  = thrust/B, 
                    thrust_coefficient                = Ct, 
                    disc_azimuthal_distribution       = psi_2d, 
                    blade_dQ_dr                       = blade_dQ_dr,
                    disc_dQ_dr                        = blade_dQ_dr_2d,
                    blade_torque_distribution         = blade_Q_distribution,    
                    disc_torque_distribution          = blade_Q_distribution_2d, 
                    torque_per_blade                  = torque/B,   
                    torque_coefficient                = Cq,   
                    power                             = power,
                    power_coefficient                 = Cp,  
                    converged_inflow_ratio            = lamdaw,
                    propeller_efficiency              = etap,
                    blade_H_distribution              = rotor_drag_distribution,
                    rotor_drag                        = rotor_drag,
                    rotor_drag_coefficient            = Crd,
                    Ua=Ua,
                    Ut=Ut,
                    a=a,
                    beta=beta,
                    r=r,
                    R=R,
                    a_loc=a_loc,
                    a_geo=a_geo,
                    cl_sur=cl_sur,
                    cd_sur=cd_sur,
                    use_2d_analysis=use_2d_analysis,
                    c=c,
                    nu=nu,
                    ctrl_pts=ctrl_pts,
                    Na=Na,
                    tc=tc
            ) 
    
        return thrust_vector, torque, power, Cp, outputs , etap
    
    
    def spin_HFW(self,conditions):
        """Analyzes a general rotor given geometry and operating conditions.
        Runs the blade element theory with a helical fixed-wake model for the
        iterative wake analysis.

        Assumptions:
          Helical fixed-wake with wake skew angle

        Source:
          N/A

        Inputs:
        self.inputs.omega                    [radian/s]
        conditions.freestream.               
          density                            [kg/m^3]
          dynamic_viscosity                  [kg/(m-s)]
          speed_of_sound                     [m/s]
          temperature                        [K]
        conditions.frames.                   
          body.transform_to_inertial         (rotation matrix)
          inertial.velocity_vector           [m/s]
        conditions.propulsion.               
          throttle                           [-]
                                             
        Outputs:                             
        conditions.propulsion.outputs.        
           number_radial_stations            [-]
           number_azimuthal_stations         [-] 
           disc_radial_distribution          [m]
           speed_of_sound                    [m/s]
           density                           [kg/m-3]
           velocity                          [m/s]
           disc_tangential_induced_velocity  [m/s]
           disc_axial_induced_velocity       [m/s]
           disc_tangential_velocity          [m/s]
           disc_axial_velocity               [m/s]
           drag_coefficient                  [-]
           lift_coefficient                  [-]
           omega                             [rad/s]
           disc_circulation                  [-] 
           blade_dQ_dR                       [N/m]
           blade_dT_dr                       [N]
           blade_thrust_distribution         [N]
           disc_thrust_distribution          [N]
           thrust_per_blade                  [N]
           thrust_coefficient                [-] 
           azimuthal_distribution            [rad]
           disc_azimuthal_distribution       [rad]
           blade_dQ_dR                       [N]
           blade_dQ_dr                       [Nm]
           blade_torque_distribution         [Nm] 
           disc_torque_distribution          [Nm] 
           torque_per_blade                  [Nm] 
           torque_coefficient                [-] 
           power                             [W]    
           power_coefficient                 [-] 
                                             
        Properties Used:                     
        self.                                
          number_of_blades                   [-]
          tip_radius                         [m]
          twist_distribution                 [radians]
          chord_distribution                 [m]
          orientation_euler_angles           [rad, rad, rad]
        """           

        #--------------------------------------------------------------------------------        
        # Initialize by running BEMT for initial blade circulation
        #--------------------------------------------------------------------------------
        _, _, _, _, bemt_outputs , _ = self.spin(conditions)
        conditions.noise.sources.propellers[self.tag] = bemt_outputs
        self.outputs = bemt_outputs
        omega = self.inputs.omega
        
        #--------------------------------------------------------------------------------
        # generate wake vortex distribution
        #--------------------------------------------------------------------------------
        props = Data()
        props.propeller = self
        
        # initialize inputs
        VD        = Data()
        m         = 1
        identical = True
        
        # generate wake distribution for n rotor rotation
        nrots         = 5
        steps_per_rot = 30
        rpm           = omega/Units.rpm
        
        # simulation parameters for n rotor rotations
        init_timestep_offset     = 0.
        time                     = 60*nrots/rpm[0][0]
        number_of_wake_timesteps = steps_per_rot*nrots
        
        self.wake_settings.init_timestep_offset     = init_timestep_offset
        self.wake_settings.wake_development_time    = time
        self.wake_settings.number_of_wake_timesteps = number_of_wake_timesteps
        
        # generate wake distribution using initial circulation from BEMT
        _, _, _, _, _  = generate_propeller_wake_distribution(props,identical,m,VD,init_timestep_offset, time, number_of_wake_timesteps,conditions ) 
        
        # spin propeller with helical fixed-wake
        self.wake_method = "helical_fixed_wake"
        thrust_vector, torque, power, Cp, outputs , etap = self.spin(conditions)
        
        return thrust_vector, torque, power, Cp, outputs , etap
    def vec_to_vel(self):
        """This rotates from the propellers vehicle frame to the propellers velocity frame

        Assumptions:
        There are two propeller frames, the vehicle frame describing the location and the propeller velocity frame
        velocity frame is X out the nose, Z towards the ground, and Y out the right wing
        vehicle frame is X towards the tail, Z towards the ceiling, and Y out the right wing

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """
        
        rot_mat = sp.spatial.transform.Rotation.from_rotvec([0,np.pi,0]).as_matrix()
        
        return rot_mat
    
    
    def body_to_prop_vel(self):
        """This rotates from the systems body frame to the propellers velocity frame

        Assumptions:
        There are two propeller frames, the vehicle frame describing the location and the propeller velocity frame
        velocity frame is X out the nose, Z towards the ground, and Y out the right wing
        vehicle frame is X towards the tail, Z towards the ceiling, and Y out the right wing

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """
        
        # Go from body to vehicle frame
        body_2_vehicle = sp.spatial.transform.Rotation.from_rotvec([0,np.pi,0]).as_matrix()
        
        # Go from vehicle frame to propeller vehicle frame: rot 1 including the extra body rotation
        rots    = np.array(self.orientation_euler_angles) * 1.
        rots[1] = rots[1] + self.inputs.y_axis_rotation
        vehicle_2_prop_vec = sp.spatial.transform.Rotation.from_rotvec(rots).as_matrix()        
        
        # GO from the propeller vehicle frame to the propeller velocity frame: rot 2
        prop_vec_2_prop_vel = self.vec_to_vel()
        
        # Do all the matrix multiplies
        rot1    = np.matmul(body_2_vehicle,vehicle_2_prop_vec)
        rot_mat = np.matmul(rot1,prop_vec_2_prop_vel)

        
        return rot_mat
    
    
    def prop_vel_to_body(self):
        """This rotates from the systems body frame to the propellers velocity frame

        Assumptions:
        There are two propeller frames, the vehicle frame describing the location and the propeller velocity frame
        velocity frame is X out the nose, Z towards the ground, and Y out the right wing
        vehicle frame is X towards the tail, Z towards the ceiling, and Y out the right wing

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """
        
        body2propvel = self.body_to_prop_vel()
        
        r = sp.spatial.transform.Rotation.from_matrix(body2propvel)
        r = r.inv()
        rot_mat = r.as_matrix()

        return rot_mat

def compute_HFW_blade_velocities(prop, bemt_outputs ):
    """
    
    Outputs:
       Va - axial velocity array of shape (ctrl_pts, Na, Nr)
       Vt - tangential velocity array of shape (ctrl_pts, Na, Nr)
    """
    VD                       = Data()
    omega                    = prop.inputs.omega  
    time                     = prop.wake_settings.wake_development_time
    init_timestep_offset     = prop.wake_settings.init_timestep_offset
    number_of_wake_timesteps = prop.wake_settings.number_of_wake_timesteps     
    
    cpts                     = 1   # only testing one condition
    Na = prop.number_azimuthal_stations 
    Nr = len(prop.chord_distribution)

    conditions = Data()
    conditions.noise = Data()
    conditions.noise.sources = Data()
    conditions.noise.sources.propellers = Data()
    conditions.noise.sources.propellers.propeller = bemt_outputs
    
    # compute radial blade section locations based on initial timestep offset 
    dt   = time/number_of_wake_timesteps
    t0   = dt*init_timestep_offset
    m=1
    identical=True
    props=Data()
    props.propeller = prop
    
    # set shape of velocitie arrays
    Va = np.zeros((cpts,Na,Nr))
    Vt = np.zeros((cpts,Na,Nr))
    for i in range(Na):
        # increment blade angle to new axial position
        blade_angle   = omega[0]*t0 + i*(2*np.pi/(Na))
        
        # update wake geometry
        init_timestep_offset = blade_angle/(omega * dt)
        
        # generate wake distribution using initial circulation from BEMT
        WD, _, _, _, _  = generate_propeller_wake_distribution(props,identical,m,VD,init_timestep_offset, time, number_of_wake_timesteps,conditions ) 
               
        # position in propeller frame:
        r          = prop.radius_distribution
        y          = -r * np.cos(blade_angle)
        z          = r * np.sin(blade_angle)
        
        # ----------------------------------------------------------------    
        # Compute the wake-induced velocities at propeller blade
        # ----------------------------------------------------------------
        offset_angle = -2*Units.deg
        offset_time  = offset_angle/omega[0][0]
        x_offset     = offset_time*prop.outputs.velocity[0][0]
        rot_mat = np.array([[np.cos(offset_angle), -np.sin(offset_angle)],
                            [np.sin(offset_angle), np.cos(offset_angle)]])
        
        # set the evaluation points in the vortex distribution
        Yb   = prop.Wake_VD.Yblades[0,:]  #y
        Zb   = prop.Wake_VD.Zblades[0,:]  #z
        Xb   = prop.Wake_VD.Xblades[0,:]  #prop.origin[0][0]*np.ones_like(VD.YC)
        
        VD.YC = Yb*rot_mat[0,0] + Zb*rot_mat[0,1]
        VD.ZC = Yb*rot_mat[1,0] + Zb*rot_mat[1,1]
        VD.XC = Xb + x_offset
        
        
        VD.n_cp = np.size(VD.YC)   
    
        # Compute induced velocities at blade from the helical fixed wake
        VD.Wake_collapsed = WD
        
        V_ind   = compute_wake_induced_velocity(WD, VD, cpts)
        u       = V_ind[0,:,0]
        v       = V_ind[0,:,1]
        w       = V_ind[0,:,2]   
        
        Va[:,i,:]  = -u
        Vt[:,i,:]  = (w*np.cos(blade_angle) - v*np.sin(blade_angle))*prop.rotation
    
        # test generate vtk
        from SUAVE.Input_Output.VTK.save_prop_wake_vtk import save_prop_wake_vtk
        from SUAVE.Input_Output.VTK.save_evaluation_points_vtk import save_evaluation_points_vtk
        Results = Data()
        Results["prop_outputs"] = prop.outputs
        save_prop_wake_vtk(VD.Wake, filename="/Users/rerha/Desktop/vtk_test/wake."+str(i)+".vtk", Results=Results, i_prop=0)
        save_evaluation_points_vtk(VD, filename="/Users/rerha/Desktop/vtk_test/eval_points."+str(i)+".vtk")
    return Va, Vt


def compute_aerodynamic_forces(a_loc, a_geo, cl_sur, cd_sur, ctrl_pts, Nr, Na, Re, Ma, alpha, tc, use_2d_analysis):
    """
    Cl, Cdval = compute_aerodynamic_forces(  a_loc, 
                                             a_geo, 
                                             cl_sur, 
                                             cd_sur, 
                                             ctrl_pts, 
                                             Nr, 
                                             Na, 
                                             Re, 
                                             Ma, 
                                             alpha, 
                                             tc, 
                                             nonuniform_freestream )
                                             
    Computes the aerodynamic forces at sectional blade locations. If airfoil 
    geometry and locations are specified, the forces are computed using the 
    airfoil polar lift and drag surrogates, accounting for the local Reynolds 
    number and local angle of attack. 
    
    If the airfoils are not specified, an approximation is used.

    Assumptions:
    N/A

    Source:
    N/A

    Inputs:
    a_loc                      Locations of specified airfoils                 [-]
    a_geo                      Geometry of specified airfoil                   [-]
    cl_sur                     Lift Coefficient Surrogates                     [-]
    cd_sur                     Drag Coefficient Surrogates                     [-]
    ctrl_pts                   Number of control points                        [-]
    Nr                         Number of radial blade sections                 [-]
    Na                         Number of azimuthal blade stations              [-]
    Re                         Local Reynolds numbers                          [-]
    Ma                         Local Mach number                               [-]
    alpha                      Local angles of attack                          [radians]
    tc                         Thickness to chord                              [-]
    use_2d_analysis            Specifies 2d disc vs. 1d single angle analysis  [Boolean]
                                                     
                                                     
    Outputs:                                          
    Cl                       Lift Coefficients                         [-]                               
    Cdval                    Drag Coefficients  (before scaling)       [-]
    """        
    # If propeller airfoils are defined, use airfoil surrogate 
    if a_loc != None:
        # Compute blade Cl and Cd distribution from the airfoil data  
        dim_sur = len(cl_sur)   
        if use_2d_analysis:
            # return the 2D Cl and CDval of shape (ctrl_pts, Na, Nr)
            Cl      = np.zeros((ctrl_pts,Na,Nr))              
            Cdval   = np.zeros((ctrl_pts,Na,Nr))
            for jj in range(dim_sur):                 
                Cl_af           = cl_sur[a_geo[jj]](Re,alpha,grid=False)  
                Cdval_af        = cd_sur[a_geo[jj]](Re,alpha,grid=False)  
                locs            = np.where(np.array(a_loc) == jj )
                Cl[:,:,locs]    = Cl_af[:,:,locs]
                Cdval[:,:,locs] = Cdval_af[:,:,locs]          
        else:
            # return the 1D Cl and CDval of shape (ctrl_pts, Nr)
            Cl      = np.zeros((ctrl_pts,Nr))              
            Cdval   = np.zeros((ctrl_pts,Nr))  
            
            for jj in range(dim_sur):                 
                Cl_af         = cl_sur[a_geo[jj]](Re,alpha,grid=False)  
                Cdval_af      = cd_sur[a_geo[jj]](Re,alpha,grid=False)  
                locs          = np.where(np.array(a_loc) == jj )
                Cl[:,locs]    = Cl_af[:,locs]
                Cdval[:,locs] = Cdval_af[:,locs]                   
    else:
        # Estimate Cl max 
        Cl_max_ref = -0.0009*tc**3 + 0.0217*tc**2 - 0.0442*tc + 0.7005
        Re_ref     = 9.*10**6      
        Cl1maxp    = Cl_max_ref * ( Re / Re_ref ) **0.1
        
        # If not airfoil polar provided, use 2*pi as lift curve slope
        Cl = 2.*np.pi*alpha
    
        # By 90 deg, it's totally stalled.
        Cl[Cl>Cl1maxp]  = Cl1maxp[Cl>Cl1maxp] # This line of code is what changed the regression testing
        Cl[alpha>=np.pi/2] = 0.
        
        # Scale for Mach, this is Karmen_Tsien
        Cl[Ma[:,:]<1.] = Cl[Ma[:,:]<1.]/((1-Ma[Ma[:,:]<1.]*Ma[Ma[:,:]<1.])**0.5+((Ma[Ma[:,:]<1.]*Ma[Ma[:,:]<1.])/(1+(1-Ma[Ma[:,:]<1.]*Ma[Ma[:,:]<1.])**0.5))*Cl[Ma<1.]/2)
        
        # If the blade segments are supersonic, don't scale
        Cl[Ma[:,:]>=1.] = Cl[Ma[:,:]>=1.]  
        
        #This is an atrocious fit of DAE51 data at RE=50k for Cd
        Cdval = (0.108*(Cl*Cl*Cl*Cl)-0.2612*(Cl*Cl*Cl)+0.181*(Cl*Cl)-0.0139*Cl+0.0278)*((50000./Re)**0.2)
        Cdval[alpha>=np.pi/2] = 2.    
        
    
    # prevent zero Cl to keep Cd/Cl from breaking in bemt  
    Cl[Cl==0] = 1e-6
        
    return Cl, Cdval