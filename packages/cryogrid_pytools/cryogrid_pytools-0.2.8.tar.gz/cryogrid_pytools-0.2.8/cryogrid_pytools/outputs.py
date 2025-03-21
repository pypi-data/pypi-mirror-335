# depends on matlab_helpers.py
import xarray as xr
import pandas as pd
import numpy as np

from loguru import logger


def read_OUT_regridded_FCI2_file(fname:str, deepest_point=None)->xr.Dataset:
    """
    Read a CryoGrid OUT_regridded_FCI2 file and return it as an xarray dataset.

    Parameters
    ----------
    fname : str
        Path to the .mat file
    deepest_point : float, optional
        Represents the deepest depth of the profile. If not provided, 
        then elevation is returned. Negative values represent depths below
        the surface.

    Returns
    -------
    ds : xarray.Dataset
        Dataset with dimensions 'time' and 'level'. The CryoGrid variable
        `depths` is renamed to `elevation`. If deepest_point is provided, then
        `depth` will represent the depth below the surface (negative below
        surface).
    """
    from .matlab_helpers import read_mat_struct_flat_as_dict, matlab2datetime
    
    dat = read_mat_struct_flat_as_dict(fname)
    for key in dat:
        dat[key] = dat[key].squeeze()

    ds = xr.Dataset()
    ds.attrs['filename'] = fname

    times = matlab2datetime(dat.pop('timestamp'))
    elevation = dat.pop('depths')

    for key in dat:
        ds[key] = xr.DataArray(
            data = dat[key].astype('float32'), 
            dims=['level', 'time'], 
            coords={'time': times})
        
    ds['elevation'] = xr.DataArray(elevation, dims=['level'])

    if deepest_point is not None:
        assert deepest_point < 0, "deepest_point must be negative (below surface)"
        
        ds = ds.rename(level='depth')

        # calculate depth step size
        n = elevation.size - 1
        s = (elevation[-1] - elevation[0]) / n
        
        significant_number = np.abs(np.floor(np.log10((np.abs(s))))).astype(int)
        # calculate shallowest point based on step size and n
        shallowest_point = deepest_point - (s * n)
        deepest_point += s / 2  # adding half step for arange
        depth = np.arange(shallowest_point, deepest_point, s, dtype='float32').round(significant_number)
        ds['depth'] = xr.DataArray(depth, dims=['depth'])
        ds = ds.set_coords('depth')
        ds = ds.transpose('depth', 'time', ...)
    else:  
        ds = ds.transpose('elevation', 'time', ...)

    ds = ds.chunk(dict(time=-1))

    return ds


def _read_OUT_regridded_FCI2_parallel(fname_glob:str, deepest_point:float, **joblib_kwargs)->list:
    """
    Reads multiple files that are put out by the OUT_regridded_FCI2 class

    Parameters
    ----------
    fname_glob: str
        Path of the files that you want to read in. 
        Use same notation as for glob(). Note that it expects
        name to follow the format `some_project_name_GRIDCELL_date.mat`
        where GRIDCELL will be extracted to assign the gridcell dimension. 
        These GRIDCELLs correspond with the index of the data in the 
        flattened array. 
    deepest_point: float
        When setting the configuration for when the data should be 
        saved, the maximum depth is set. Give this number as a
        negative number here.
    concat_dim: str
        The dimension that the data should be concatenated along. 
        Defaults to 'time', but 'gridcell' can also be used if 
        the files are from different gridcells.
    joblib_kwargs: dict
        Uses the joblib library to do parallel reading of the files. 
        Defaults are: n_jobs=-1, backend='threading', verbose=1

    Returns
    -------
    xr.Dataset
        An array with dimensions gridcell, depth, time. 
        Variables depend on how the class was configured, but
        elevation will also be a variable. 
    """
    from glob import glob
    import joblib

    # get the file list
    flist = sorted(glob(fname_glob))
    
    # create the joblib tasks
    func = joblib.delayed(read_OUT_regridded_FCI2_file)
    tasks = [func(f, deepest_point) for f in flist]
    
    # set up the joblib configuration
    joblib_props = dict(n_jobs=-1, backend='threading', verbose=1)
    joblib_props.update(joblib_kwargs)
    worker = joblib.Parallel(**joblib_props)  # type: ignore
    list_of_ds = list(worker(tasks))  # run the tasks

    return list_of_ds


def read_OUT_regridded_FCI2_clusters(fname_glob:str, deepest_point:float, **joblib_kwargs)->xr.Dataset:
    """
    Reads multiple files that are put out by the OUT_regridded_FCI2 class

    Parameters
    ----------
    fname_glob: str
        Path of the files that you want to read in. 
        Use same notation as for glob(). Note that it expects
        name to follow the format `some_project_name_GRIDCELL_date.mat`
        where GRIDCELL will be extracted to assign the gridcell dimension. 
        These GRIDCELLs correspond with the index of the data in the 
        flattened array. 
    deepest_point: float
        When setting the configuration for when the data should be 
        saved, the maximum depth is set. Give this number as a
        negative number here.
    joblib_kwargs: dict
        Uses the joblib library to do parallel reading of the files. 
        Defaults are: n_jobs=-1, backend='threading', verbose=1

    Returns
    -------
    xr.Dataset
        An array with dimensions gridcell, depth, time. 
        Variables depend on how the class was configured, but
        elevation will also be a variable. 
    """
    from glob import glob

    # get the file list
    flist = sorted(glob(fname_glob))
    # extract the gridcell from the file name
    gridcell = [int(f.split('_')[-2]) for f in flist]
    
    list_of_ds = _read_OUT_regridded_FCI2_parallel(fname_glob, deepest_point, **joblib_kwargs)
    
    # assign the gridcell dimension so that we can combine the data by coordinates and time 
    list_of_ds = [ds.expand_dims(gridcell=[c]) for ds, c in zip(list_of_ds, gridcell)]
    ds = xr.combine_by_coords(list_of_ds, combine_attrs='drop_conflicts')

    # transpose data so that plotting is quick and easy
    ds = ds.transpose('gridcell', 'depth', 'time', ...)

    return ds
