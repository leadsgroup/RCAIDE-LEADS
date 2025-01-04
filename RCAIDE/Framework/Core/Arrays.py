# RCAIDE/Framework/Core/Arrays.py

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------
import numpy as np

# ----------------------------------------------------------------------
#   Array
# ----------------------------------------------------------------------       

array_type  = np.ndarray
matrix_type = np.matrixlib.defmatrix.matrix
 
def atleast_2d_col(A):
    """
    Convert array to 2D column format

    Parameters
    ----------
    A : array_like
        Input array to convert

    Returns
    -------
    ndarray
        2D array with shape (N,1)

    Notes
    -----
    Ensures array has at least 2 dimensions with data in column format
    """
    return atleast_2d(A, 'col')


def atleast_2d_row(A):
    """
    Convert array to 2D row format

    Parameters
    ----------
    A : array_like
        Input array to convert

    Returns
    -------
    ndarray
        2D array with shape (1,N)

    Notes
    -----
    Ensures array has at least 2 dimensions with data in row format
    """
    return atleast_2d(A, 'row')


def atleast_2d(A, oned_as='row'):
    """
    Ensure array is at least 2-dimensional

    Parameters
    ----------
    A : array_like
        Input array to convert
    oned_as : str, optional
        Format for 1D arrays: 'row' or 'col'
        Default: 'row'

    Returns
    -------
    ndarray
        Array with at least 2 dimensions

    Raises
    ------
    Exception
        If oned_as is not 'row' or 'col'

    Notes
    -----
    - Converts non-array inputs to numpy arrays
    - Expands 1D arrays according to oned_as parameter
    - Leaves higher dimensional arrays unchanged
    """       
    
    # not an array yet
    if not isinstance(A,(array_type,matrix_type)):
        if not isinstance(A,(list,tuple)):
            A = [A]
        A = np.array(A)
        
    # check rank
    if A.ndim < 2:
        # expand row or col
        if oned_as == 'row':
            A = A[None,:]
        elif oned_as == 'col':
            A = A[:,None]
        else:
            raise Exception("oned_as must be 'row' or 'col' ")
            
    return A