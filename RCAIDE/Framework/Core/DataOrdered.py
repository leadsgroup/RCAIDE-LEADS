# RCAIDE/Framework/Core/DataOrdered.py
#
# Created:  Jul 2016, E. Botero
# Modified: Sep 2016, E. Botero
#           May 2020, E. Botero
#           Jul 2020, E. Botero 
#           Jul 2021, E. Botero

   
# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------  

from collections import OrderedDict

# for enforcing attribute style access names
import string
chars = string.punctuation + string.whitespace
t_table = str.maketrans( chars          + string.ascii_uppercase , 
                            '_'*len(chars) + string.ascii_lowercase )

import numpy as np

# ----------------------------------------------------------------------
#   Property Class
# ----------------------------------------------------------------------   

class Property(object):
    """
    Property descriptor for DataOrdered class

    Parameters
    ----------
    key : str, optional
        Key name for property
        Default: None

    Notes
    -----
    Used to create the root map essential to the linking in DataOrdered()
    """
    
    def __init__(self,key=None):
        """
        Initialize property descriptor

        Parameters
        ----------
        key : str, optional
            Key name for property
            Default: None
        """           
        self._key = key
        
    def __get__(self,obj,kls=None):
        """
        Get property value

        Parameters
        ----------
        obj : object
            Instance to get property from
        kls : type, optional
            Class of the instance

        Returns
        -------
        value
            Property value or self if obj is None
        """           
        if obj is None: return self
        else          : return dict.__getitem__(obj,self._key)
        
    def __set__(self,obj,val):
        """
        Set property value

        Parameters
        ----------
        obj : object
            Instance to set property on
        val : any
            Value to set
        """          
        dict.__setitem__(obj,self._key,val)
        
    def __delete__(self,obj):
        """
        Delete property

        Parameters
        ----------
        obj : object
            Instance to delete property from
        """          
        dict.__delitem__(obj,self._key)

    
# ----------------------------------------------------------------------
#   DataOrdered
# ----------------------------------------------------------------------        

## @ingroup Core
class DataOrdered(OrderedDict):
    """
    An ordered dictionary with attribute-style access

    Parameters
    ----------
    args : tuple
        Positional arguments passed to OrderedDict
    kwargs : dict
        Keyword arguments passed to OrderedDict

    Attributes
    ----------
    _root : Property
        Root node for ordered structure
    _map : Property
        Mapping of keys to nodes

    Notes
    -----
    - Extension of Python dict allowing both tag and '.' access
    - Maintains insertion order for deterministic indexing
    """
    
    
    _root = Property('_root')
    _map  = Property('_map')    
    
    def append(self, value, key=None):
        """
        Add new value with optional key

        Parameters
        ----------
        value : any
            Value to append, must have tag attribute
        key : str, optional
            Key to use, defaults to value.tag

        Raises
        ------
        KeyError
            If key already exists

        Notes
        -----
        - Uses value.tag as default key
        - Translates key to valid Python identifier
        """
        if key is None: key = value.tag
        key = key.translate(t_table)
        if key is None: key = value.tag
        if key in self: raise KeyError('key "%s" already exists' % key)
        self.__setattr__(key,value)    

    def __defaults__(self):
        """
        Set default values for ordered data structure

        Notes
        -----
        Base implementation does nothing
        Subclasses should override to set defaults
        """
        pass
    
    def __getitem__(self, k):
        """
        Get item by key or index

        Parameters
        ----------
        k : str or int
            Key or index to retrieve

        Returns
        -------
        value
            Value at key/index k

        Notes
        -----
        Supports both string keys and integer indices
        """
        if not (isinstance(k,int) or isinstance(k,np.int64)):
            return super(DataOrdered,self).__getattribute__(k)
        else:
            return super(DataOrdered,self).__getattribute__(self.keys()[k])
    
    def __new__(cls, *args, **kwarg):
        """
        Create new DataOrdered instance

        Parameters
        ----------
        args : tuple
            Positional arguments
        kwarg : dict
            Keyword arguments

        Returns
        -------
        self : DataOrdered
            New instance with initialized root and map

        Notes
        -----
        - Creates empty ordered dictionary
        - Initializes root node and mapping structure
        - Applies defaults from base classes
        """
        self = OrderedDict.__new__(cls)
        
        if self.hasattr('_root'):
            self._root
        else:
            root = [] # sentinel node
            root[:] = [root, root, None]
            dict.__setitem__(self,'_root',root)
            dict.__setitem__(self,'_map' ,{})        
        
        # Use the base init
        self.__init2()
        
        # get base class list
        klasses = self.get_bases()
                
        # fill in defaults trunk to leaf
        for klass in klasses[::-1]:
            klass.__defaults__(self)
            
        return self
    
    def hasattr(self, k):
        """
        Check if attribute exists

        Parameters
        ----------
        k : str
            Key to check

        Returns
        -------
        bool
            True if attribute exists, False otherwise
        """
        try:
            self.__getitem__(k)
            return True
        except:
            return False
            
    
    def __init__(self, *args, **kwarg):
        """
        Initialize DataOrdered instance

        Parameters
        ----------
        args : tuple
            Positional arguments
        kwarg : dict
            Keyword arguments

        Notes
        -----
        - Creates input data using base class
        - Updates self with input data
        """
        # handle input data (ala class factory)
        input_data = DataOrdered.__base__(*args,**kwarg)
        
        # update this data with inputs
        self.update(input_data)
        
        
    def __init2(self, items=None, **kwds):
        """
        Helper function for initialization

        Parameters
        ----------
        items : dict or iterable, optional
            Initial items to add
        kwds : dict
            Additional keyword arguments

        Notes
        -----
        Handles different input types:
        - Dictionary with iterkeys/keys
        - Iterable of (key, value) pairs
        - Keyword arguments
        """         
        def append_value(key,value):  
            
            self[key] = value            
        
        # a dictionary
        if hasattr(items, 'iterkeys'):
            for key in items.keys():
                append_value(key,items[key])

        elif hasattr(items, 'keys'):
            for key in items.keys():
                append_value(key,items[key])
                
        # items lists
        elif items:
            for key, value in items:
                append_value(key,value)
                
        # key words
        for key, value in kwds.items():
            append_value(key,value)     

    # iterate on values, not keys
    def __iter__(self):
        """
        Get iterator over values

        Returns
        -------
        iterator
            Iterator yielding values in order

        Notes
        -----
        Iterates over values rather than keys
        """
        return iter(self.values())
    
    def get_bases(self):
        """
        Get list of base classes

        Returns
        -------
        list
            List of ancestor classes excluding dict and object

        Raises
        ------
        TypeError
            If class is not derived from DataOrdered

        Notes
        -----
        Uses method resolution order to get ancestor tree
        """
        # Get the Method Resolution Order, i.e. the ancestor tree
        klasses = list(self.__class__.__mro__)
        
        # Make sure that this is a Data object, otherwise throw an error.
        if DataOrdered not in klasses:
            raise TypeError('class %s is not of type Data()' % self.__class__)    
        
        # Remove the last two items, dict and object. Since the line before ensures this is a data object this won't break
        klasses = klasses[:-3]

        return klasses 
    
    def typestring(self):
        """
        Get dot-notation string representation of class hierarchy

        Returns
        -------
        str
            Type string in format 'package.module.class'

        Notes
        -----
        Removes duplicate class names from end of path
        """
        typestring = str(type(self)).split("'")[1]
        typestring = typestring.split('.')
        if typestring[-1] == typestring[-2]:
            del typestring[-1]
        typestring = '.'.join(typestring) 
        return typestring
    
    def dataname(self):
        """
        Get formatted name of data object

        Returns
        -------
        str
            String in format "<data object 'type.path'>"

        Notes
        -----
        Uses typestring() to get class path
        """
        return "<data object '" + self.typestring() + "'>"

    def deep_set(self, keys, val):
        """
        Set nested value using dot notation

        Parameters
        ----------
        keys : str or list
            Key path using dot notation (e.g. 'a.b.c')
        val : any
            Value to set

        Returns
        -------
        data
            Reference to modified data structure

        Notes
        -----
        - Splits string keys on dots
        - Traverses nested dictionaries
        """
        if isinstance(keys,str):
            keys = keys.split('.')
        
        data = self
         
        if len(keys) > 1:
            for k in keys[:-1]:
                data = data[k]
        
        data[ keys[-1] ] = val
        
        return data

    def deep_get(self, keys):
        """
        Get nested value using dot notation

        Parameters
        ----------
        keys : str or list
            Key path using dot notation (e.g. 'a.b.c')

        Returns
        -------
        value
            Value at specified path

        Notes
        -----
        - Splits string keys on dots
        - Traverses nested dictionaries
        """
        if isinstance(keys,str):
            keys = keys.split('.')
        
        data = self
         
        if len(keys) > 1:
            for k in keys[:-1]:
                data = data[k]
        
        value = data[ keys[-1] ]
        
        return value   
    
    def update(self, other):
        """
        Update with values from other dictionary

        Parameters
        ----------
        other : dict
            Dictionary to update from

        Raises
        ------
        TypeError
            If input is not a dictionary

        Notes
        -----
        - Recursively updates nested structures
        - Skips keys starting with underscore
        - Maintains insertion order
        """
        if not isinstance(other,dict):
            raise TypeError('input is not a dictionary type')
        for k,v in other.items():
            # recurse only if self's value is a Dict()
            if k.startswith('_'):
                continue
        
            try:
                self[k].update(v)
            except:
                self[k] = v
        return 

    def __delattr__(self, key):
        """
        Delete attribute or dictionary item

        Parameters
        ----------
        key : str
            Key/attribute name to delete

        Notes
        -----
        - Updates links in predecessor and successor nodes
        - Maintains ordered structure
        - Removes from mapping
        """
        # Deleting an existing item uses self._map to find the link which is
        # then removed by updating the links in the predecessor and successor nodes.
        OrderedDict.__delattr__(self,key)
        link_prev, link_next, key = self._map.pop(key)
        link_prev[1] = link_next
        link_next[0] = link_prev 
        
    def __len__(self):
        """
        Get number of items

        Returns
        -------
        int
            Number of items in dictionary

        Notes
        -----
        Uses internal __dict__ length
        """
        return self.__dict__.__len__()   

    def __iter_basic__(self):
        """
        Get basic iterator over keys

        Returns
        -------
        iterator
            Iterator yielding keys in insertion order

        Notes
        -----
        - Uses internal linked list structure
        - Core iterator used by other iteration methods
        """
        root = self._root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]
            
    def __reduce__(self):
        """
        Support for pickling

        Returns
        -------
        tuple
            (reconstructor, (class, items), instance_dict)

        Notes
        -----
        - Used for making configurations
        - Preserves order and custom attributes
        """
        items = [( k, DataOrdered.__getitem2(self,k) ) for k in DataOrdered.iterkeys(self)]
        inst_dict = vars(self).copy()
        for k in vars(DataOrdered()):
            inst_dict.pop(k, None)
        return (_reconstructor, (self.__class__,items,), inst_dict)
    
    def __setattr__(self, key, value):
        """
        Set attribute or dictionary item

        Parameters
        ----------
        key : str
            Key/attribute name to set
        value : any
            Value to store

        Notes
        -----
        - Creates new link at end of list
        - Updates mapping structure
        - Maintains insertion order
        """
        # Setting a new item creates a new link which goes at the end of the linked
        # list, and the inherited dictionary is updated with the new key/value pair.
        if not hasattr(self,key) and not hasattr(self.__class__,key):
        #if not self.has_key(key) and not hasattr(self.__class__,key):
            root = dict.__getitem__(self,'_root')
            last = root[0]
            map  = dict.__getitem__(self,'_map')
            last[1] = root[0] = map[key] = [last, root, key]
        OrderedDict.__setattr__(self,key, value)

    def __setitem__(self, k, v):
        """
        Set item by key

        Parameters
        ----------
        k : str
            Key to set
        v : any
            Value to store

        Notes
        -----
        Uses __setattr__ to maintain ordered structure
        """
        self.__setattr__(k,v)
         

    def clear(self):
        """
        Remove all items from dictionary

        Notes
        -----
        - Resets root node and mapping structure
        - Clears all attributes
        - Handles AttributeError if structure not initialized
        """
        try:
            for node in self._map.values():
                del node[:]
            root = self._root
            root[:] = [root, root, None]
            self._map.clear()
        except AttributeError:
            pass
        self.__dict__.clear()
        
    def get(self, k, d=None):
        """
        Get value with optional default

        Parameters
        ----------
        k : str
            Key to retrieve
        d : any, optional
            Default value if key not found
            Default: None

        Returns
        -------
        value
            Value at key or default value
        """
        return self.__dict__.get(k,d)
        
    def has_key(self, k):
        """
        Check if key exists in dictionary

        Parameters
        ----------
        k : str
            Key to check

        Returns
        -------
        bool
            True if key exists, False otherwise
        """
        return k in self.__dict__

    # allow override of iterators
    __iter = __iter__
    __getitem2 = OrderedDict.__getattribute__ 

    def keys(self):
        """
        Get list of dictionary keys

        Returns
        -------
        list
            List of keys in insertion order

        Notes
        -----
        Uses __iter_basic__ to maintain order
        """
        return list(self.__iter_basic__())
    
    def values(self):
        """
        Get list of dictionary values

        Returns
        -------
        list
            List of values in insertion order

        Notes
        -----
        Maintains insertion order of values
        """
        return [self[key] for key in self.__iter_basic__()]
    
    def items(self):
        """
        Get list of dictionary items

        Returns
        -------
        list
            List of (key, value) pairs in insertion order

        Notes
        -----
        Maintains insertion order of items
        """
        return [(key, self[key]) for key in self.__iter_basic__()]
    
    def iterkeys(self):
        """
        Get iterator over dictionary keys

        Returns
        -------
        iterator
            Iterator yielding keys in insertion order

        Notes
        -----
        Uses __iter_basic__ for ordered iteration
        """
        return self.__iter_basic__() 

    def itervalues(self):
        """
        Get iterator over values

        Returns
        -------
        iterator
            Iterator yielding values in insertion order

        Notes
        -----
        Uses __iter_basic__ for ordered iteration
        """
        return iter(self.values())

    def iteritems(self):
        """
        Get iterator over items

        Returns
        -------
        iterator
            Iterator yielding (key, value) pairs in insertion order

        Notes
        -----
        Maintains insertion order during iteration
        """

# for rebuilding dictionaries with attributes
def _reconstructor(klass,items):
    """
    Rebuild dictionary with attributes

    Parameters
    ----------
    klass : class
        Class to instantiate
    items : list
        List of (key, value) pairs

    Returns
    -------
    DataOrdered
        New instance with restored items

    Notes
    -----
    Used for rebuilding dictionaries with attributes
    """        
    self = DataOrdered.__new__(klass)
    DataOrdered.__init__(self,items)
    return self