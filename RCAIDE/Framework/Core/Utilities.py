# RCAIDE/Framework/Core/Utilities.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# Package imports 
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  interp2d
# ----------------------------------------------------------------------------------------------------------------------
 
def interp2d(x, y, xp, yp, zp, fill_value=None):
    """
    Perform bilinear interpolation on a grid

    Parameters
    ----------
    x : array_like
        X coordinates at which to interpolate
    y : array_like
        Y coordinates at which to interpolate
    xp : array_like
        1D array of grid x coordinates
    yp : array_like
        1D array of grid y coordinates
    zp : array_like
        2D array of function values, zp[i,j] = f(xp[i], yp[j])
    fill_value : float, optional
        Value to use for out-of-bounds points
        Default: None

    Returns
    -------
    array_like
        Interpolated values z[i] = f(x[i], y[i])

    Notes
    -----
    - Out-of-bounds coordinates are clamped to lie in-bounds
    - CartesianGrid is much faster if data lies on a regular grid
    - Uses Wikipedia's notation for bilinear interpolation
    """
    ix = np.clip(np.searchsorted(xp, x, side="right"), 1, len(xp) - 1)
    iy = np.clip(np.searchsorted(yp, y, side="right"), 1, len(yp) - 1)

    # Using Wikipedia's notation (https://en.wikipedia.org/wiki/Bilinear_interpolation)
    z_11 = zp[ix - 1, iy - 1]
    z_21 = zp[ix, iy - 1]
    z_12 = zp[ix - 1, iy]
    z_22 = zp[ix, iy]

    z_xy1 = (xp[ix] - x) / (xp[ix] - xp[ix - 1]) * z_11 + (x - xp[ix - 1]) / (
        xp[ix] - xp[ix - 1]
    ) * z_21
    z_xy2 = (xp[ix] - x) / (xp[ix] - xp[ix - 1]) * z_12 + (x - xp[ix - 1]) / (
        xp[ix] - xp[ix - 1]
    ) * z_22

    z = (yp[iy] - y) / (yp[iy] - yp[iy - 1]) * z_xy1 + (y - yp[iy - 1]) / (
        yp[iy] - yp[iy - 1]
    ) * z_xy2

    if fill_value is not None:
        oob = np.logical_or(
            x < xp[0], np.logical_or(x > xp[-1], np.logical_or(y < yp[0], y > yp[-1]))
        )
        z = np.where(oob, fill_value, z)

    return z

# ----------------------------------------------------------------------------------------------------------------------
# orientation_product
# ----------------------------------------------------------------------------------------------------------------------
 
def orientation_product(T, Bb):
    """
    Compute product of tensor and vector

    Parameters
    ----------
    T : ndarray
        3D array with rotation matrix patterned along dimension zero
    Bb : ndarray
        3D or 2D vector to transform

    Returns
    -------
    ndarray
        Transformed vector C = T * Bb

    Raises
    ------
    AssertionError
        If T is not 3-dimensional
    Exception
        If Bb has invalid dimensions

    Notes
    -----
    Uses einsum for efficient computation of tensor-vector product
    """
    
    assert T.ndim == 3
    
    if Bb.ndim == 3:
        C = np.einsum('aij,ajk->aik', T, Bb )
    elif Bb.ndim == 2:
        C = np.einsum('aij,aj->ai', T, Bb )
    else:
        raise Exception('bad B rank')
        
    return C

# ----------------------------------------------------------------------------------------------------------------------
# orientation_transpose
# ----------------------------------------------------------------------------------------------------------------------

def orientation_transpose(T):
    """
    Compute transpose of a tensor

    Parameters
    ----------
    T : ndarray
        3D array with rotation matrix patterned along dimension zero

    Returns
    -------
    ndarray
        Transposed tensor Tt

    Raises
    ------
    AssertionError
        If T is not 3-dimensional

    Notes
    -----
    Uses swapaxes to efficiently transpose dimensions 1 and 2
    """   
    
    assert T.ndim == 3
    
    Tt = np.swapaxes(T,1,2)
        
    return Tt

# ----------------------------------------------------------------------------------------------------------------------
# angles_to_dcms
# ----------------------------------------------------------------------------------------------------------------------

def angles_to_dcms(rotations, sequence=(2,1,0)):
    """
    Build euler angle rotation matrix

    Parameters
    ----------
    rotations : ndarray
        Column array of rotations [r1s r2s r3s] in radians
    sequence : tuple, optional
        Rotation sequence, e.g. (2,1,0), (2,1,2)
        Default: (2,1,0)

    Returns
    -------
    ndarray
        3D array with direction cosine matrices

    Notes
    -----
    - Uses T0, T1, T2 rotation matrices based on sequence
    - Applies rotations in reverse sequence order
    - Returns transform patterned along dimension zero
    """         
    # transform map
    Ts = { 0:T0, 1:T1, 2:T2 }
    
    # a bunch of eyes
    transform = new_tensor(rotations[:,0])
    
    # build the tranform
    for dim in sequence[::-1]:
        angs = rotations[:,dim]
        transform = orientation_product( transform, Ts[dim](angs) )
    
    # done!
    return transform

# ----------------------------------------------------------------------------------------------------------------------
# T0
# ----------------------------------------------------------------------------------------------------------------------  

def T0(a):
    """
    Create rotation matrix about first axis

    Parameters
    ----------
    a : ndarray
        Angle of rotation in radians

    Returns
    -------
    ndarray
        3D rotation matrix array

    Notes
    -----
    Matrix form:
    [[1,   0,  0],
     [0, cos,sin],
     [0,-sin,cos]]
    """      
    # T = np.array([[1,   0,  0],
    #               [0, cos,sin],
    #               [0,-sin,cos]])
    
    cos = np.cos(a)
    sin = np.sin(a)
                  
    T = new_tensor(a)
    
    T[:,1,1] = cos
    T[:,1,2] = sin
    T[:,2,1] = -sin
    T[:,2,2] = cos
    
    return T

# ----------------------------------------------------------------------------------------------------------------------
# T1
# ----------------------------------------------------------------------------------------------------------------------          

def T1(a):
    """
    Create rotation matrix about second axis

    Parameters
    ----------
    a : ndarray
        Angle of rotation in radians

    Returns
    -------
    ndarray
        3D rotation matrix array

    Notes
    -----
    Matrix form:
    [[cos,0,-sin],
     [0  ,1,   0],
     [sin,0, cos]]
    """      
    # T = np.array([[cos,0,-sin],
    #               [0  ,1,   0],
    #               [sin,0, cos]])
    
    cos = np.cos(a)
    sin = np.sin(a)     
    
    T = new_tensor(a)
    
    T[:,0,0] = cos
    T[:,0,2] = -sin
    T[:,2,0] = sin
    T[:,2,2] = cos
    
    return T

# ----------------------------------------------------------------------------------------------------------------------
# T2
# ----------------------------------------------------------------------------------------------------------------------  

def T2(a):
    """
    Create rotation matrix about third axis

    Parameters
    ----------
    a : ndarray
        Angle of rotation in radians

    Returns
    -------
    ndarray
        3D rotation matrix array

    Notes
    -----
    Matrix form:
    [[cos ,sin,0],
     [-sin,cos,0],
     [0   ,0  ,1]]
    """      
    # T = np.array([[cos ,sin,0],
    #               [-sin,cos,0],
    #               [0   ,0  ,1]])
        
    cos = np.cos(a)
    sin = np.sin(a)     
    
    T = new_tensor(a)
    
    T[:,0,0] = cos
    T[:,0,1] = sin
    T[:,1,0] = -sin
    T[:,1,1] = cos
        
    return T

# ----------------------------------------------------------------------------------------------------------------------
# new_tensor
# ----------------------------------------------------------------------------------------------------------------------  

def new_tensor(a):
    """
    Initialize tensor with identity matrices

    Parameters
    ----------
    a : ndarray
        1D array of angles in radians

    Returns
    -------
    ndarray
        3D array with identity matrices patterned along dimension zero

    Raises
    ------
    AssertionError
        If input is not 1-dimensional

    Notes
    -----
    - Creates array of 3x3 identity matrices
    - Handles both real and complex values
    - Number of matrices matches length of input array
    """      
    assert a.ndim == 1
    n_a = len(a)
    
    T = np.eye(3)
    
    if a.dtype is np.dtype('complex'):
        T = T + 0j
    
    T = np.resize(T,[n_a,3,3])
    
    return T