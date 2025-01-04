# RCAIDE/Framework/Core/Data.py
#
# Created:  Jun 2016, E. Botero
# Modified: Jan 2020, M. Clarke
#           May 2020, E. Botero
#           Jul 2021, E. Botero
#           Oct 2021, E. Botero



# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import numpy as np
from .Arrays import atleast_2d_col, array_type, matrix_type 

from copy import copy

# for enforcing attribute style access names
import string
from warnings import warn
chars = string.punctuation + string.whitespace
t_table = str.maketrans( chars          + string.ascii_uppercase , 
                            '_'*len(chars) + string.ascii_lowercase )

dictgetitem = dict.__getitem__
objgetattrib = object.__getattribute__

# ----------------------------------------------------------------------
#   Data
# ----------------------------------------------------------------------        

## @ingroup Core
class Data(dict):
    """
    A dictionary-based data structure with attribute-style access

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to dict
    **kwargs : dict
        Keyword arguments passed to dict

    Attributes
    ----------
    tag : str, optional
        Identifier for data instance

    Methods
    -------
    __getattribute__(k)
        Get attribute by key or object attribute
    __setattr__(k, v)
        Set attribute or dictionary item
    append(value, key=None)
        Add new value with optional key
    update(other)
        Update with values from other dictionary
    deep_set(keys, val)
        Set nested value using dot notation
    deep_get(keys)
        Get nested value using dot notation
    get_bases()
        Get list of base classes
    pack_array(output)
        Convert to array format
    unpack_array(M)
        Convert from array format

    Notes
    -----
    - Provides both dictionary and attribute-style access
    - Supports nested data structures
    - Handles array packing/unpacking
    - For ordered storage use DataOrdered class

    **Major Assumptions**
    * Keys are valid Python identifiers
    * Values can be accessed as attributes
    """
    
    def __getattribute__(self, k):
        """
        Get attribute by key or object attribute

        Parameters
        ----------
        k : str
            Key/attribute name to retrieve

        Returns
        -------
        value
            Value stored at key k

        Notes
        -----
        Tries dictionary access first, falls back to object attribute
        """
        try:
            return dictgetitem(self,k)
        except:
            return objgetattrib(self,k)

    def __setattr__(self, k, v):
        """
        Set attribute or dictionary item

        Parameters
        ----------
        k : str
            Key/attribute name to set
        v : any
            Value to store

        Notes
        -----
        Tries object attribute first, falls back to dictionary key
        """
        try:
            objgetattrib(self, k)
        except:
            self[k] = v
        else:          
            object.__setattr__(self, k, v) 
            
    def __delattr__(self, k):
        """
        Delete attribute or dictionary item

        Parameters
        ----------
        k : str
            Key/attribute name to delete

        Notes
        -----
        - Tries object attribute first, falls back to dictionary key
        - Updates internal structure when deleting
        """
        try:
            objgetattrib(self, k)
        except:
            del self[k]
        else:
            object.__delattr__(self, k)
    
    def __defaults__(self):
        """
        Set default values for data structure

        Notes
        -----
        Base implementation does nothing
        Subclasses should override to set defaults
        """
        pass      
    
    def __new__(cls, *args, **kwarg):
        """
        Create new Data instance with defaults

        Parameters
        ----------
        args : tuple
            Positional arguments
        kwarg : dict
            Keyword arguments

        Returns
        -------
        self : Data
            New instance with defaults applied

        Notes
        -----
        - Creates empty data structure
        - Applies defaults from all base classes
        - Processes from most basic to most derived class
        """
        
        
        # initialize data, no inputs
        self = super(Data,cls).__new__(cls)
        super(Data,self).__init__() 
        
        # get base class list
        klasses = self.get_bases()
                
        # fill in defaults trunk to leaf
        for klass in klasses[::-1]:
            try:
                klass.__defaults__(self)
            except:
                pass
            
        return self
    
    def typestring(self):
        """ This function makes the .key.key structure in string form of Data()
    
            Assumptions:
            N/A
    
            Source:
            N/A
    
            Inputs:
            N/A
    
            Outputs:
            N/A
    
            Properties Used:
            N/A    
        """         
        
        # build typestring
        typestring = str(type(self)).split("'")[1]
        typestring = typestring.split('.')
        if typestring[-1] == typestring[-2]:
            del typestring[-1]
        typestring = '.'.join(typestring) 
        return typestring    
    
    def dataname(self):
        """ This function is used for printing the class
    
            Assumptions:
            N/A
    
            Source:
            N/A
    
            Inputs:
            N/A
    
            Outputs:
            N/A
    
            Properties Used:
            N/A    
        """          
        return "<data object '" + self.typestring() + "'>"     
    
    
    def __str__(self, indent=''):
        """
        Get string representation of data structure

        Parameters
        ----------
        indent : str, optional
            Indentation prefix for formatting
            Default: ''

        Returns
        -------
        str
            Formatted string showing data contents

        Notes
        -----
        - Skips items starting with underscore
        - Uses __str2() for nested content formatting
        """
        
        new_indent = '  '
        args = ''
        
        # trunk data name
        if not indent:
            args += self.dataname()  + '\n'
        else:
            args += ''
            
        args += self.__str2(indent)
        
        return args    
    
    
    def __str2(self, indent=''):
        """
        Helper function for recursive string formatting

        Parameters
        ----------
        indent : str, optional
            Indentation prefix for formatting
            Default: ''

        Returns
        -------
        str
            Formatted string of nested contents

        Notes
        -----
        - Handles recursive data structures
        - Skips 'hidden' items starting with underscore
        - Adds indentation for nested levels
        """
        
        new_indent = '  '
        args = ''
        
        # trunk data name
        if indent: args += '\n'
        
        # print values   
        for key,value in self.items():
            
            # skip 'hidden' items
            if isinstance(key,str) and key.startswith('_'):
                continue
            
            # recurse into other dict types
            if isinstance(value,dict):
                if not value:
                    val = '\n'
                else:
                    try:
                        val = value.__str2(indent+new_indent)
                    except RuntimeError: # recursion limit
                        val = ''
                    except:
                        val = value.__str__(indent+new_indent)
                                                
            # everything else
            else:
                val = str(value) + '\n'
                
            # this key-value, indented
            args+= indent + str(key) + ' : ' + val
            
        return args        
    
    def __init__(self, *args, **kwarg):
        """
        Initialize new Data instance

        Parameters
        ----------
        args : tuple
            Positional arguments passed to dict
        kwarg : dict
            Keyword arguments passed to dict

        Notes
        -----
        - Creates input data using base class
        - Updates self with input data
        - Preserves attribute-style access
        """
        
        # handle input data (ala class factory)
        input_data = Data.__base__(*args,**kwarg)
        
        # update this data with inputs
        self.update(input_data)    

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
    
    def itervalues(self):
        """
        Get iterator over values

        Returns
        -------
        iterator
            Iterator yielding values in order

        Notes
        -----
        Legacy method for Python 2 compatibility
        """
        for k in super(Data,self).__iter__():
            yield self[k]   
    
    def values(self):
        """
        Get list of all values

        Returns
        -------
        list
            List of all values in data structure

        Notes
        -----
        Uses internal __values() method
        """
        return self.__values()          
            
    def __values(self):
        """
        Get list of all values

        Returns
        -------
        list
            List of values for all keys

        Notes
        -----
        Internal implementation for values() method
        """
        return [self[key] for key in super(Data,self).__iter__()]    
    
    def update(self,other):
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
            If class is not derived from Data

        Notes
        -----
        Uses method resolution order to get ancestor tree
        """
        # Get the Method Resolution Order, i.e. the ancestor tree
        klasses = list(self.__class__.__mro__)
        
        # Make sure that this is a Data object, otherwise throw an error.
        if Data not in klasses:
            raise TypeError('class %s is not of type Data()' % self.__class__)    
        
        # Remove the last two items, dict and object. Since the line before ensures this is a data objectt this won't break
        klasses = klasses[:-2]

        return klasses    
    
    def append(self,value,key=None):
        """
        Add new value with optional key

        Parameters
        ----------
        value : any
            Value to append
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
        if key in self: raise KeyError('key "%s" already exists' % key)
        self[key] = value        
    
    def deep_set(self, keys, val):
        """
        Set nested value using dot notation

        Parameters
        ----------
        keys : str or list
            Key path using dot notation (e.g. 'a.b.c')
            Can include array indexing with brackets
        val : any
            Value to set

        Returns
        -------
        data
            Reference to modified data structure

        Notes
        -----
        - Supports array indexing with bracket notation
        - Creates path if it doesn't exist
        - Can set values in nested arrays
        """
        
        if isinstance(keys,str):
            keys = keys.split('.')
        
        data = self
         
        if len(keys) > 1:
            for k in keys[:-1]:
                data = data[k]
        
        if keys[-1][-1] ==']':
            splitkey = keys[-1].split('[')
            thing = data[splitkey[0]]
            for ii in range(1,len(splitkey)-1):
                index    = int(splitkey[ii][:-1])
                thing = thing[index]
            index    = int(splitkey[-1][:-1])
            thing[index] = val
        else:
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
        
    def pack_array(self,output='vector'):
        """
        Convert dictionary data to array format

        Parameters
        ----------
        output : {'vector', 'array'}, optional
            Output format
            Default: 'vector'

        Returns
        -------
        ndarray
            Packed data in specified format

        Notes
        -----
        - Only packs numeric types and arrays up to rank 2
        - For 'array' output, all values must have same number of rows
        """
        
        
        # check output type
        if not output in ('vector','array'): raise Exception('output type must be "vector" or "array"')        
        vector = output == 'vector'
        
        # list to pre-dump array elements
        M = []
        
        # valid types for output
        valid_types = ( int, float,
                        array_type,
                        matrix_type )
        
        # initialize array row size (for array output)
        size = [False]
        
        # the packing function
        def do_pack(D):
            for v in D.values(): 
                try:
                    rank = v.ndim
                except:
                    rank = 0
                    
                # type checking
                if isinstance( v, dict ): 
                    do_pack(v) # recursion!
                    continue
                elif not isinstance( v, valid_types ): continue
                elif rank > 2: continue
                # make column vectors
                v = atleast_2d_col(v)
                # handle output type
                if vector:
                    # unravel into 1d vector
                    v = v.ravel(order='F')
                else:
                    # check array size
                    size[0] = size[0] or v.shape[0] # updates size once on first array
                    if v.shape[0] != size[0]: 
                        #warn ('array size mismatch, skipping. all values in data must have same number of rows for array packing',RuntimeWarning)
                        continue
                # dump to list
                M.append(v)
            #: for each value
        
        # do the packing
        do_pack(self)
        
        # pack into final array
        if M:
            M = np.hstack(M)
        else:
            # empty result
            if vector:
                M = np.array([])
            else:
                M = np.array([[]])
        
        # done!
        return M
    
    def unpack_array(self,M):
        """
        Convert array data back to dictionary format

        Parameters
        ----------
        M : ndarray
            Array to unpack into data structure

        Returns
        -------
        self : Data
            Reference to modified data structure

        Notes
        -----
        - Array must match structure dimensions
        - Warns if not all values are unpacked
        """
        
        
        # dont require dict to have numpy
        import numpy as np
        from .Arrays import atleast_2d_col, array_type, matrix_type
        
        # check input type
        vector = M.ndim  == 1
        
        # valid types for output
        valid_types = ( int, float,
                        array_type,
                        matrix_type )
        
        # counter for unpacking
        _index = [0]
        
        # the unpacking function
        def do_unpack(D):
            for k,v in D.items():
                try:
                    rank = v.ndim
                except:
                    rank = 0
                # type checking
                if isinstance(v, dict): 
                    do_unpack(v) # recursion!
                    continue
                elif not isinstance(v,valid_types): continue
                
                # get unpack index
                index = _index[0]                
                
                # skip if too big
                if rank > 2: 
                    continue
                
                # scalars
                elif rank == 0:
                    if vector:
                        D[k] = M[index]
                        index += 1
                    else:#array
                        continue
                        #raise RuntimeError , 'array size mismatch, all values in data must have same number of rows for array unpacking'
                    
                # 1d vectors
                elif rank == 1:
                    n = len(v)
                    if vector:
                        D[k][:] = M[index:(index+n)]
                        index += n
                    else:#array
                        D[k][:] = M[:,index]
                        index += 1
                    
                # 2d arrays
                elif rank == 2:
                    n,m = v.shape
                    if vector:
                        D[k][:,:] = np.reshape( M[index:(index+(n*m))] ,[n,m], order='F')
                        index += n*m 
                    else:#array
                        D[k][:,:] = M[:,index:(index+m)]
                        index += m
                
                #: switch rank
                
                _index[0] = index

            #: for each itme
        
        # do the unpack
        do_unpack(self)
         
        # check
        if not M.shape[-1] == _index[0]: warn('did not unpack all values',RuntimeWarning)
         
        # done!
        return self     
    
    def do_recursive(self, method, other):
        """
        Apply method recursively to self and other

        Parameters
        ----------
        method : callable
            Method to apply recursively
        other : Data
            Other data structure to process with

        Returns
        -------
        result
            Result of recursive method application

        Notes
        -----
        - Recursively processes nested data structures
        - Used for operations between two Data instances
        """
        
        # result data structure
        klass = self.__class__
        if isinstance(klass,Data):
            klass = Data
        result = klass()
    
        # the update function
        def do_operation(A,B,C):
            for k,a in A.items():
                if isinstance(B,Data):
                    if k in B:
                        b = B[k]
                    else: 
                        C[k] = a
                        continue
                else:
                    b = B
                # recursion
                if isinstance(a,Data):
                    c = klass()
                    C[k] = c
                    do_operation(a,b,c)
                # method
                else:
                    if b is None:
                        c = method(a)
                    else:
                        c = method(a,b)
                    if not c is None:
                        C[k] = c
                #: if type
            #: for each key,value
    
        # do the update!
        do_operation(self,other,result)    
    
        return result
