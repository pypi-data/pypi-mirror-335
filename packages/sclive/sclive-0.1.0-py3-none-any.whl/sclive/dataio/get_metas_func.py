from typing import List, Optional
import pandas as pd
import polars as pl
from anndata import AnnData
def get_metas(adata:AnnData, 
              meta_ids:List[str], 
              cat:Optional[bool]=None)->pl.DataFrame:
    '''
    Extract meta data from AnnData object and return as Polars DataFrame
    
    :param adata: 
        AnnData object to extract meta data from    
    :param meta_ids: 
        List of meta data ids to export from Annotated data
    :param cat: 
        If True, then the meta data is assumed categorical, if false it is assumed numeric, if None, then the function will try to infer the type using pandas api

    Returns: 
    --------
    polars.DataFrame: 
        DataFrame with meta data and barcodes
    '''
    if cat is None:
        dtys = [pd.api.types.is_numeric_dtype(adata.obs[meta_id]) for meta_id in meta_ids] 
        if all(dtys) or not any(dtys):
            cat = not dtys[0]
        else:
            raise(ValueError("Meta data types are not uniform!"))
    if cat:
        dimred_data = pl.from_pandas(adata.obs[meta_ids].reset_index()).rename({"index":"barcode"}).with_columns(
                                                                                    pl.exclude("barcode").cast(pl.String).cast(pl.Categorical))
    else:
        dimred_data = pl.from_pandas(adata.obs[meta_ids].reset_index()).rename({"index":"barcode"})
    return dimred_data