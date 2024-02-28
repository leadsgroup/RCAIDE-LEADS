
# package imports
import numpy as np
def compute_shaft_off_take_power(self, state):
    """ This computes the work done from the power draw.

    Assumptions:
    None

    Source:
    https://web.stanford.edu/~cantwell/AA283_Course_Material/AA283_Course_Notes/

    Inputs:
    self.inputs.
      mdhc                  [-] Compressor nondimensional mass flow
      reference_temperature [K]
      reference_pressure    [Pa]

    Outputs:
    self.outputs.
      power                 [W]
      work_done             [J/kg] (if power draw is not zero)

    Properties Used:
    self.power_draw         [W]
    """  
    if self.power_draw == 0.0:
        self.outputs.work_done = np.array([0.0])

    else:

        mdhc = self.inputs.mdhc
        Tref = self.reference_temperature
        Pref = self.reference_pressure

        total_temperature_reference = self.inputs.total_temperature_reference
        total_pressure_reference    = self.inputs.total_pressure_reference

        self.outputs.power = self.power_draw

        mdot_core = mdhc * np.sqrt(Tref / total_temperature_reference) * (total_pressure_reference / Pref)

        self.outputs.work_done = self.outputs.power / mdot_core

        self.outputs.work_done[mdot_core == 0] = 0
