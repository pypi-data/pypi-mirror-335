import warnings
import polars as pl
from .get_gene_exprs_func import get_gene_exprs
from anndata import AnnData
from typing import List, Optional

def get_dimred_with_exprs(adata:AnnData,
                        dimred_id:str, 
                        genes:List[str],
                        comps:Optional[List[int]] = None,
                        use_raw:Optional[bool] = False,
                        dimred_id_suffix:Optional[str] = None,
                        layer:Optional[str] = None)->pl.DataFrame:
    '''
    Extracts dimention reduction coordinates and gene expression data from Annotated Data object.
    
    :param adata: AnnData 
                single cell object for extraction
    :param dimred_id: str 
                dimension reduction id in Annotated Data object
    :param genes: List[str]
                list of genes to extract from Annotated Data object
    :param comps: Optional[List[int]] 
                list of components to extract from dimension reduction data (default is [0, 1])
    :param use_raw: Optional[bool]
                whether to use raw data for gene expression (default is False)
    :param dimred_id_suffix: Optional[str] 
                suffix to append to dimension reduction id (default is "")
    :param layer: Optional[str] 
                layer to extract gene expression data from (default is None)

    Returns:
    --------
    pl.DataFrame
        DataFrame with the dimention reduction data and gene expressions data with a barcode column and a gene_exprs column with expression struct
    '''
    avail_genes_bool = [gene in adata.var_names for gene in genes]
    not_avail_genes = [gene for gene, avail in zip(genes, avail_genes_bool) if not avail]
    if len(not_avail_genes) > 0:
        warnings.warn(f"Following genes are not found in Annotated Data: {', '.join(not_avail_genes)}")
        avail_genes = [gene for gene, avail in zip(genes, avail_genes_bool) if avail]
    else:
        avail_genes = genes
    
    if comps is None:
         comps = [0,1]
    if dimred_id_suffix is None:
        dimred_id_suffix = ""
        
    if dimred_id_suffix + dimred_id not in adata.obsm_keys():
            raise(ValueError("Given dimention reduction with the suffix is not found in Annotated Data!"))
    else:
        dimred_data = (pl.DataFrame(adata.obsm[dimred_id_suffix + dimred_id][:,comps], schema=["X","Y", "Z"][:len(comps)])
                       .with_columns(pl.Series(name="barcode", values=adata.obs_names).cast(pl.String)))

    if len(not_avail_genes) == len(genes):
        warnings.warn("None of the given genes are found in Annotated Data! Only returning dimention reduction data.")
        return dimred_data
    else:
        return dimred_data.join(get_gene_exprs(adata, avail_genes, use_raw, layer), on="barcode")