# RCAIDE/Framework/Core/Container.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------        

from .               import Data
from warnings        import warn
import random

import string
chars = string.punctuation + string.whitespace
t_table = str.maketrans( chars          + string.ascii_uppercase , 
                            '_'*len(chars) + string.ascii_lowercase )

# ----------------------------------------------------------------------------------------------------------------------
#  Container
# ----------------------------------------------------------------------------------------------------------------------   

class Container(Data):
    """
    A dictionary-based container for managing collections of Data objects

    Parameters
    ----------
    args : tuple
        Positional arguments passed to Data parent
    kwargs : dict
        Keyword arguments passed to Data parent

    Attributes
    ----------
    tag : str
        Identifier for container instance

    Methods
    -------
    append(value)
        Add new value with automatic tag handling
    extend(vals)
        Append multiple values from list, tuple or dict
    get_children()
        Get list of allowed child components

    Notes
    -----
    - Unordered container with attribute-style access
    - Handles duplicate component names by modifying tags
    - For ordered storage use ContainerOrdered class

    **Major Assumptions**
    * Components have tag attributes
    * Duplicate tags are resolved by appending numbers
    """

    def __defaults__(self):
        """
        Set default values for container

        Notes
        -----
        Base implementation does nothing
        Subclasses should override to set defaults
        """
        pass

    def __init__(self,*args,**kwarg):
        
        super(Container,self).__init__(*args,**kwarg)
        self.__defaults__()
    
    def append(self, val):
        """
        Add new value with automatic tag handling

        Parameters
        ----------
        val : Data
            Value to append, must have tag attribute

        Notes
        -----
        - Translates tag to valid Python identifier
        - Handles duplicate tags by appending numbers
        - Falls back to random number if still duplicate
        """
        # See if the item tag exists, if it does modify the name
        keys = self.keys()
        
        tag = str.lower(val.tag.translate(t_table))
        if tag in keys:
            string_of_keys = "".join(self.keys())
            n_comps = string_of_keys.count(val.tag)
            val.tag = tag + str(n_comps+1)
            
            # Check again, because theres an outside chance that its duplicate again
            if val.tag in keys:
                val.tag = tag + str(n_comps+random.randint(0,1000))
        
        Data.append(self,val)
        
    def extend(self, vals):
        """
        Append multiple values from list, tuple or dict

        Parameters
        ----------
        vals : list, tuple, or dict
            Values to append

        Raises
        ------
        Exception
            If vals is not list, tuple or dict

        Notes
        -----
        - Lists/tuples: appends each value
        - Dicts: updates container with dict items
        """
        if isinstance(vals,(list,tuple)):
            for v in val: self.append(v)
        elif isinstance(vals,dict):
            self.update(vals)
        else:
            raise Exception('unrecognized data type')
        
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