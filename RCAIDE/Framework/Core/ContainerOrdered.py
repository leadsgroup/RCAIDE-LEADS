# ContainerOrdered.py
#
# Created:  Jan 2015, T. Lukacyzk
# Modified: Feb 2016, T. MacDonald
#           Jun 2016, E. Botero
#           May 2020, E. Botero



# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------        

from .DataOrdered import DataOrdered

# ----------------------------------------------------------------------
#   Data Container Base Class
# ----------------------------------------------------------------------        

class ContainerOrdered(DataOrdered):
    """
    An ordered container for managing collections of DataOrdered objects

    Parameters
    ----------
    args : tuple
        Positional arguments passed to DataOrdered parent
    kwargs : dict
        Keyword arguments passed to DataOrdered parent

    Attributes
    ----------
    tag : str
        Identifier for container instance
    _root : Property
        Root node for ordered structure
    _map : Property
        Mapping of keys to nodes

    Methods
    -------
    append(value)
        Add new value maintaining insertion order
    get_children()
        Get list of allowed child components

    Notes
    -----
    - Maintains insertion order of components
    - Provides attribute-style and index access
    - For unordered storage use Container class

    **Major Assumptions**
    * Components have tag attributes
    * Order of insertion matters
    """
        
    def __defaults__(self):
        """
        Set default values for ordered container

        Notes
        -----
        Base implementation does nothing
        Subclasses should override to set defaults
        """          
        pass
    
    def __init__(self,*args,**kwarg):
       
        super(ContainerOrdered,self).__init__(*args,**kwarg)
        self.__defaults__()
    
    def append(self, val):
        """
        Add new value maintaining insertion order

        Parameters
        ----------
        val : DataOrdered
            Value to append, must have tag attribute

        Notes
        -----
        - Maintains order of insertion
        - Uses DataOrdered append mechanism
        """
        DataOrdered.append(self, val)
        
    def get_children(self):
        """
        Get list of allowed child components

        Returns
        -------
        list
            Empty list in base implementation

        Notes
        -----
        Subclasses should override to specify allowed children
        Used for validation of container contents
        """
        return []  