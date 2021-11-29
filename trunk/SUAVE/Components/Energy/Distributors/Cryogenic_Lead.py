## @ingroup Components-Energy-Distributors
# Cryogenic_Lead.py
#
# Created:  Feb 2020, K.Hamilton
# Modified: Nov 2021,   S. Claridge

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

from SUAVE.Components.Energy.Energy_Component import Energy_Component
from SUAVE.Attributes.Solids.Solid import Solid
from scipy import integrate
from scipy import interpolate
from scipy.misc import derivative
import numpy as np
# ----------------------------------------------------------------------
#  Cryogenic Lead Class
# ----------------------------------------------------------------------

## @ingroup Components-Energy-Distributors
class Cryogenic_Lead(Energy_Component):
    
    def __defaults__(self):
        """ This sets the default values.
    
            Assumptions:
            Cryogenic Leads only operate at their optimum current, or at zero current.
    
            Source:
            Current Lead Optimization for Cryogenic Operation at Intermediate Temperatures - Broomberg
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            None
            """         
        self.cold_temp          = 0.0    # [K]
        self.hot_temp           = 0.0    # [K]
        self.current            = 0.0       # [A]
        self.length             = 0.0    # [m]
        self.material           = None
    
        self.cross_section      = 0.0    # [m2]
        self.optimum_current   = 0.0         # [A]
        self.minimum_Q          = 0.0         # [W]
        self.unpowered_Q        = 0.0         # [W]

    def Q_min(self, material, cold_temp, hot_temp, current):
        # Estimate the area under the thermal:electrical conductivity vs temperature plot for the temperature range of the current lead.
        integral = integrate.quad(lambda T: material.thermal_conductivity(T)/material.electrical_conductivity(T), cold_temp, hot_temp)

        # Estimate the average thermal:electrical conductivity for the lead.
        average_ratio = (1/(hot_temp-cold_temp)) * integral[0]

        # Solve the heat flux at the cold end. This is both the load on the cryocooler and the power loss in the current lead.
        minimum_Q = current * (2*average_ratio*(hot_temp-cold_temp))**0.5
        # This represents the special case where all the electrical power is delivered to the cryogenic environment as this optimised the lead for reduced cryogenic load. Q = electrical power
        power = minimum_Q

        return [minimum_Q, power]

    def LARatio(self, material, cold_temp, hot_temp, current, minimum_Q):
        # Calculate the optimum length to cross-sectional area ratio
        # Taken directly from McFee

        sigTL = material.electrical_conductivity(cold_temp)
        inte = integrate.quad(lambda T: self.Q_min(material,T,hot_temp,current)[0]*derivative(material.electrical_conductivity,T), cold_temp, hot_temp)[0]
        la_ratio = (sigTL * minimum_Q + inte)/(current**2)

        return la_ratio

    def initialize_material_lead(self):
        """
        Defines an optimum material lead for supplying current to a cryogenic environment given the operating conditions and material properties.
        
        Assumptions:
        None
        
        Inputs:
            lead.
                cold_temp           [K]
                hot_temp            [K]
                current             [A]
                length              [m]

        Outputs:      
            lead.     
                mass                [kg]
                cross_section       [m]
                optimum_current     [A]
                minimum_Q           [W]
        """

        # Unpack properties
        cold_temp   = self.cold_temp
        hot_temp    = self.hot_temp 
        current     = self.current  
        length      = self.length   
        material    = self.material
        

        # Find the heat generated by the optimum lead
        minimum_Q = self.Q_min(material, cold_temp, hot_temp, current)[0]

        # # Calculate the optimum length to cross-sectional area ratio
        la_ratio = self.LARatio(material, cold_temp, hot_temp, current, minimum_Q)

        # Calculate the cross-sectional area
        cs_area = length/la_ratio
        # Apply the material density to calculate the mass
        mass = cs_area*length*material.density

        # 

        # Pack up results
        self.mass_properties.mass   = mass
        self.cross_section          = cs_area
        self.optimum_current        = current
        self.minimum_Q              = minimum_Q

        # find the heat conducted into the cryogenic environment if no current is flowing
        unpowered_Q             = self.Q_unpowered()

        # Pack up unpowered lead
        self.unpowered_Q        = unpowered_Q[0]

    def Q_unpowered(self):
        # Estimates the heat flow into the cryogenic environment if no current is supplied to the lead.

        # unpack properties
        hot_temp        = self.hot_temp     
        cold_temp       = self.cold_temp    
        cross_section   = self.cross_section
        length          = self.length
        material          = self.material

        # Integrate the thermal conductivity across the relevant temperature range.
        integral = integrate.quad(lambda T: material.thermal_conductivity(T), cold_temp, hot_temp)

        # Apply the conductivity to estimate the heat flow
        Q       = integral[0] * cross_section / length

        # Electrical power is obviously zero if no current is flowing
        power   = 0.0

        return [Q, power]

    def Q_offdesign(self, current):
        # Estimates the heat flow into the cryogenic environment when a current other than the current the lead was optimised for is flowing. Assumes the temperature difference remains constant.
        values = list(map(self.calc_current, current.tolist()))
        values = np.asarray(values)

        return values

    def calc_current(self, current ):

        design_current      = self.optimum_current
        design_Q            = self.minimum_Q
        zero_Q              = self.unpowered_Q
        cold_temp           = self.cold_temp
        hot_temp            = self.hot_temp
        cs_area             = self.cross_section
        length              = self.length
        material            = self.material

        
        # The thermal gradient along the lead is assumed to remain constant for all currents below the design current. The resistance remains constant if the temperature remains constant. The estimated heat flow is reduced in proportion with the carried current.
        if current <= design_current:
            proportion      = current/design_current
            R               = design_Q/(design_current**2.0)
            power           = R*current**2.0
            Q               = zero_Q + proportion * (design_Q - zero_Q)
   

        # If the supplied current is higher than the design current the maximum temperature in the lead will be higher than ambient. Solve by dividing the lead at the maximum temperature point.
        else:
            # Initial guess at max temp in lead
            max_temp        = 2 * hot_temp
            # Find actual maximum temperature by bisection, accept result within 1% of correct.
            error           = 1
            guess_over      = 0
            guess_diff      = hot_temp

            while error > 0.01:
                # Find length of warmer part of lead
                warm_Q          = self.Q_min(material, hot_temp, max_temp, current)
    
                warm_la         = self.LARatio(material, hot_temp, max_temp, current, warm_Q)
                warm_length     = cs_area * warm_la
                # Find length of cooler part of lead
                cool_Q          = self.Q_min(material, cold_temp, max_temp, current)
                cool_la         = self.LARatio(material, cold_temp, max_temp, current, cool_Q)
                cool_length     = cs_area * cool_la
                # compare lead length with known lead length as test of the max temp guess
                test_length     = warm_length + cool_length
                error           = abs((test_length-length)/length)
                # change the guessed max_temp
                # A max_temp too low will result in the test length being too long
                if test_length > length:
                    if guess_over == 0:             # query whether solving by bisection yet
                        guess_diff  = max_temp      # if not, continue to double guess
                        max_temp    = 2*max_temp
                    else:
                        max_temp    = max_temp + guess_diff
                else:
                    guess_over  = 1              # set flag that bisection range found
                    max_temp    = max_temp - guess_diff
                # Prepare guess difference for next iteration
                guess_diff  = 0.5*guess_diff
                # The cool_Q is the cryogenic heat load as warm_Q is sunk to ambient
                Q           = cool_Q
                # All Q is out of the lead, so the electrical power use in the lead is the sum of the Qs
                power       = warm_Q + cool_Q
            

        return [Q,power]