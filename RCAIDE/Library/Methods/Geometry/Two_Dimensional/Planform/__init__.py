## @defgroup Methods-Geometry-Two_Dimensional/Planform Planform
# RCAIDE/Methods/Geometry/Two_Dimensional/Planform/__init__.py
# 

""" RCAIDE Package Setup
"""

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# @ingroup Methods-Geometry-Two_Dimensional

from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import fuselage_planform
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import horizontal_tail_planform
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import vertical_tail_planform
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import wing_planform
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import horizontal_tail_planform_raymer
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import set_origin_non_dimensional, set_origin_dimensional
from .wing_segmented_planform                                 import wing_segmented_planform, segment_properties
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import vertical_tail_planform_raymer
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import wing_fuel_volume
from Legacy.trunk.S.Methods.Geometry.Two_Dimensional.Planform import populate_control_sections