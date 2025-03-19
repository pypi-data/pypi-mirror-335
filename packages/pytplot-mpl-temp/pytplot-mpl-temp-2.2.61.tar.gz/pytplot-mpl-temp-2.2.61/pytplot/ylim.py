# Copyright 2018 Regents of the University of Colorado. All Rights Reserved.
# Released under the MIT license.
# This software was developed at the University of Colorado's Laboratory for Atmospheric and Space Physics.
# Verify current version before use at: https://github.com/MAVENSDC/PyTplot
import logging
import pytplot

def ylim(name, min, max):
    """
    This function will set the y axis range displayed for a specific tplot variable.
    
    Parameters
    ----------
        name : str, int, list of str, list of int
            The names, indices, or wildcard patterns of the tplot variable that you wish to set y limits for.
        min : flt
            The start of the y axis.
        max : flt
            The end of the y axis.   
            
    Returns
    -------
        None
    
    Examples
    --------
        >>> # Change the y range of Variable1 
        >>> import pyspedas
        >>> x_data = [1,2,3,4,5]
        >>> y_data = [1,2,3,4,5]
        >>> pyspedas.store_data("Variable1", data={'x':x_data, 'y':y_data})
        >>> pyspedas.ylim('Variable1', 2, 4)

    """

    pytplot.options(name,'y_range',[min, max])
    return