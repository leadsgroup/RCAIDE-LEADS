## @defgroup Methods-Geometry-Two_Dimensional-Cross_Section-Airfoil Airfoil
# Geometry functions for two dimensional airfoils.
# @ingroup Methods-Geometry-Two_Dimensional-Cross_Section

from .compute_naca_4series                      import compute_naca_4series 
from .compute_airfoil_polars                    import compute_airfoil_polars
from .compute_airfoil_boundary_layer_properties import build_boundary_layer_surrogates
from .compute_airfoil_boundary_layer_properties import evaluate_boundary_layer_surrogates
from .import_airfoil_dat                        import import_airfoil_dat
from .import_airfoil_geometry                   import import_airfoil_geometry 
from .import_airfoil_polars                     import import_airfoil_polars