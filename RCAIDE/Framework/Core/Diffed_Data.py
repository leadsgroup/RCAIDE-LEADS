# RCAIDE/Framework/Core/Diffed_Data.py
#
# Created:  Feb 2015, T. Lukacyzk
# Modified: Feb 2016, T. MacDonald
#           Jun 2016, E. Botero

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from copy import deepcopy
from .Container import Container as ContainerBase
from .Data import Data
from .DataOrdered import DataOrdered
import numpy as np

# ----------------------------------------------------------------------
#  Config
# ----------------------------------------------------------------------

## @ingroup Core
class Diffed_Data(Data):
    """
    A data structure that tracks differences from a base configuration

    Parameters
    ----------
    base : Data, optional
        Base configuration to track changes against
        Default: None

    Attributes
    ----------
    tag : str
        Configuration identifier, defaults to 'config'
    _base : Data
        Reference to base configuration
    _diff : Data
        Stored differences from base configuration

    Notes
    -----
    Used for creating modified configurations while only storing differences
    from a base configuration.
    """

    def __defaults__(self):
        """
        Set default values for diffed data structure

        Notes
        -----
        Initializes:
        - tag as 'config'
        - _base as empty Data()
        - _diff as empty Data()
        """
        self.tag    = 'config'
        self._base  = Data()
        self._diff  = Data()
        
    def __init__(self,base=None):
        """
        Initialize with optional base configuration

        Parameters
        ----------
        base : Data, optional
            Base configuration to track changes against
            Default: None

        Notes
        -----
        Creates deep copy of base configuration
        """  
        if base is None: base = Data()
        self._base = base
        this = deepcopy(base) # deepcopy is needed here to build configs - Feb 2016, T. MacDonald
        Data.__init__(self,this)
        
    def store_diff(self):
        """
        Store current differences from base configuration

        Notes
        -----
        Computes and stores delta between current and base state
        """          
        delta = diff(self,self._base)
        self._diff = delta
         
# ----------------------------------------------------------------------
#  Config Container
# ----------------------------------------------------------------------

class Container(ContainerBase):
    """
    Container for managing multiple diffed configurations

    Notes
    -----
    - Unordered container for Diffed_Data instances
    - Handles storing and applying differences for contained configurations
    """

    def append(self,value):
        """
        Add new configuration to container

        Parameters
        ----------
        value : Diffed_Data
            Configuration to append

        Notes
        -----
        Stores differences before appending
        """         
        try: value.store_diff()
        except AttributeError: pass
        ContainerBase.append(self,value)
        
    def pull_base(self):
        """
        Update all configurations from their bases

        Notes
        -----
        Calls pull_base() on each contained configuration
        """          
        for config in self:
            try: config.pull_base()
            except AttributeError: pass

    def store_diff(self):
        """
        Store differences for all configurations

        Notes
        -----
        Calls store_diff() on each contained configuration
        """          
        for config in self:
            try: config.store_diff()
            except AttributeError: pass
    
    def finalize(self):
        """
        Finalize all configurations

        Notes
        -----
        - Calls finalize() on each configuration
        - Effectively performs pull_base() on each
        """        
        for config in self:
            try: config.finalize()
            except AttributeError: pass


# ------------------------------------------------------------
#  Handle Linking
# ------------------------------------------------------------

Diffed_Data.Container = Container

# ------------------------------------------------------------
#  Diffing Function
# ------------------------------------------------------------

def diff(A, B):
    """
    Compute differences between two data structures

    Parameters
    ----------
    A : Data
        First data structure to compare
    B : Data
        Second data structure to compare against

    Returns
    -------
    result : Data
        Data structure containing only the differences between A and B

    Notes
    -----
    - Recursively compares nested Data structures
    - Only stores values that differ between A and B
    - Handles both Data and DataOrdered types
    - Skips special attributes (_base, _diff) for Diffed_Data instances

    Examples
    --------
    >>> base = Data()
    >>> modified = Data()
    >>> modified.x = 1 
    >>> delta = diff(modified, base)
    >>> print(delta.x)  # Shows 1
    """
    keys = set([])
    keys.update(A.keys())
    keys.update(B.keys())

    if isinstance(A, Diffed_Data):
        keys.remove('_base')
        keys.remove('_diff')

    result = type(A)()
    result.clear()

    for key in keys:
        va = A.get(key, None)
        vb = B.get(key, None)
        if isinstance(va, Data) and isinstance(vb, Data):
            sub_diff = diff(va, vb)
            if sub_diff:
                result[key] = sub_diff
        elif isinstance(va, Data) or isinstance(vb, Data):
            result[key] = va
        elif isinstance(va, DataOrdered) and isinstance(vb, DataOrdered):
            sub_diff = diff(va, vb)
            if sub_diff:
                result[key] = sub_diff
        elif isinstance(va, DataOrdered) or isinstance(vb, DataOrdered):
            result[key] = va
        elif not np.all(va == vb):
            result[key] = va

    return result    