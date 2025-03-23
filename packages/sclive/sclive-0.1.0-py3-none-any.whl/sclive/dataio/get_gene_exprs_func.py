from typing import List, Optional
import warnings
import polars as pl
from scipy import sparse
import numpy as np
from anndata import AnnData

def get_gene_exprs(adata:AnnData, 
                   genes:List[str], 
                   use_raw:Optional[bool]=False, 
                   layer:Optional[str] = None)->pl.DataFrame:
    '''
    Extract gene expression data from an AnnData object.
    
    Parameters:
    -----------
    :param adata: AnnData
            Annotated data object
    :param genes: list of str
            List of gene names to extract expression data
    :param use_raw: bool, optional (default: False)
            Whether to use raw counts from the AnnData object
    :param layer: str, optional (default: None)
            Specific layer of the AnnData object to use for extracting data
    Returns:
    --------
    polars.DataFrame
        DataFrame containing gene expression data with barcodes as row identifiers.
    '''
    if use_raw and layer is not None:
        warnings.warn("Both use_raw and layer are set. Using raw data and ignoring raw")
    if use_raw and sparse.issparse(adata.raw.X):
        dimred_data = (pl.DataFrame({"gene_exprs":np.array(adata.raw[:,genes].X.todense())})
                       .with_columns(
                           pl.col("gene_exprs").arr.to_struct(fields=genes),
                           pl.Series(name = "barcode", values=adata.obs_names).cast(pl.String))
                      .with_columns(pl.col("gene_exprs").struct.unnest()))
    elif use_raw:
        dimred_data = (pl.DataFrame({"gene_exprs":np.array(adata.raw[:,genes].X)})
                       .with_columns(
                           pl.col("gene_exprs").arr.to_struct(fields=genes),
                           pl.Series(name = "barcode", values=adata.obs_names).cast(pl.String))
                      .with_columns(pl.col("gene_exprs").struct.unnest()))
    else:
        dimred_data = (pl.from_pandas(adata[:,genes].to_df(layer=layer).reset_index())
                       .rename({"index":"barcode"})
                        .with_columns(gene_exprs = pl.struct(**{gene:pl.col(gene) for gene in genes})))
    return dimred_data