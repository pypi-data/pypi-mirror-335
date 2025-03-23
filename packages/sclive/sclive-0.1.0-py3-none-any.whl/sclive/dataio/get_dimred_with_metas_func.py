import polars as pl
from anndata import AnnData
from typing import List, Optional
from .get_metas_func import get_metas

def get_dimred_with_metas(adata:AnnData,
                        dimred_id: str,
                        meta_ids: Optional[List[str]] = None,
                        comps: Optional[List[int]]  = None,
                        cat: Optional[bool] = None,
                        dimred_id_suffix: Optional[str] = None)->pl.DataFrame:
    
    '''
    Extracts dimention reduction coordinates and meta data from Annotated Data object. 

    :param adata: AnnData 
                Single cell object for extraction
    :param dimred_id: str 
                Dimension reduction id in Annotated Data object
    :param meta_ids: Optional[List[str]] (default is None)
                List of meta data ids to extract from Annotated Data object. If None, then only dimension reduction data is returned
    :param comps: Optional[List[int]] (default is [0, 1])
                List of components to extract from dimension reduction data 
    :param cat: Optional[bool] (default is None)
                Whether to treat meta data as categorical. If None, then the function will try to infer the type using pandas api 
    :param dimred_id_suffix: Optional[str] (default is "")
                Suffix to append to dimension reduction id 
    
    Returns: 
    --------
    polars.DataFrame
        DataFrame with the dimention reduction data and meta data with a barcode column
    '''

    if comps is None:
        comps = [0,1]
    if dimred_id_suffix is None:
        dimred_id_suffix = ""
    if dimred_id_suffix + dimred_id not in adata.obsm_keys():
            raise(ValueError("Given dimention reduction with the suffix is not found in Annotated Data!"))
    else:
        dimred_data = (pl.DataFrame(adata.obsm[dimred_id_suffix + dimred_id][:,comps], schema=["X","Y","Z"][:len(comps)])
                       .with_columns(pl.Series(name="barcode", values=adata.obs_names).cast(pl.String)))
    if meta_ids is None:
        return dimred_data
    else:
        return dimred_data.join(get_metas(adata, meta_ids, cat), on="barcode")