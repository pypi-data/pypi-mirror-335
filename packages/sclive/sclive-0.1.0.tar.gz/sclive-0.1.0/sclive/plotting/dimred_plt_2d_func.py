from typing import Optional, List
import polars as pl
import plotly.graph_objects as go
from anndata import AnnData
from distinctipy import get_colors, get_hex
import warnings
from ._layout_funcs import set_2d_layout
from sclive import dataio

def dimred_plt_2d(adata: AnnData,
                dimred_id: str,
                meta_id: str,
                comps: Optional[List[int]] = None,
                selected_barcodes:Optional[List[str]] = None,
                layer:Optional[str] = None,
                use_raw: Optional[bool] = False,
                cat: Optional[bool] = None,
                dimred_id_suffix:Optional[str] = None,
                is_gene_exp: Optional[bool|None]=None,
                cont_color: Optional[str] = None, 
                meta_order: Optional[List[str]] = None, 
                meta_colors: Optional[List[str]] = None, 
                title: Optional[str] = None,
                dimred_labels: Optional[str] = None,
                pt_size: Optional[int] = 12, 
                ticks_font_size: Optional[int] = None,  
                axis_font_size: Optional[int] = None, 
                labels_size: Optional[int] = None, 
                legend_size: Optional[int] = None,
                title_size: Optional[int] = None,
                width: Optional[int|float|str] = "auto", 
                height: Optional[int|float|str] = "auto")-> go.Figure:
    """
    Creates a 2D scatter plot of the dimension reduction based on the given meta data.

    :param adata: 
        annotated data object the dimention reduction plot to be based on 
    :param dimred_id: 
        dimension reduction to use for scatter plot
    :param meta_id: 
        which obs meta feature or the gene expression to use for colors 
    :param comps: 
        which of the components of the dimension reduction to use. Default is first two
    :param selected_barcodes: 
        which data points to color. Remaining data points will be drawn grey with 0.5 opacity
    :param layer: 
        which layer to extract gene expression data from. It is ignored for meta_id from obs
    :param use_raw: 
        either to use raw gene expression or scaled. See scanpy for more details
    :param cat: 
        if meta_id is category or continuous. If not provided or None, this will be inferred using polars column types
    :param dimred_id_suffix: 
        if a suffix is added to dimred_id in the annotated data. For example "X_" if scanpy is used for preprocess
    :param is_gene_exp: 
        is the given meta id a gene expression
    :param cont_color: 
        color gradient scale for continuous cell meta or gene expression. Can be anything Plotly graph object accepts
    :param meta_order: 
        order of cell meta feature categories. This determines the order traces are added to figure and may cause some points covering other.
    :param meta_colors: 
        colors to use for categorical obs meta. If not provided it will be set randomly using distinctpy library
    :param title: 
        title for the plot
    :param dimred_labels: 
        the label of the dimension reduction axes
    :param pt_size: 
        size of points in scatter plot 
    :param ticks_font_size: 
        size of tick labels on x and y axis
    :param axis_font_size: 
        font size of the axis labels. If not provided or None, axis labels will be omitted 
    :param labels_size: 
        font size of labels for categorical meta. If set to False, labels won't be drawn
    :param legend_size: 
        font size for legend. If set to False, legend will be hidden.
    :param title_size: 
        font size for title. If set to False, legend will be hidden.
    :param width: 
        width of the plot. Can be auto or any value Plotly graph objects accepts
    :param height: 
        height of the plot. Can be auto or 'true_asp_ratio' or any value Plotly graph objects accepts. If set to true_asp_ratio, width must be explicit and height will be set using the range of x/y values
    
    Returns:
    --------
    plotly.Figure
        Figure containing the 2D scatter plot of the dimension reduction   
    """

    #extract dimension reduction data from Annotated Data
    if dimred_id_suffix is None:
        dimred_id_suffix = ""
    if comps is None:
        comps = [0,1]
    if title_size is not None and title is None:
        title = meta_id + " Dimension Reduction Plot"
    #extract meta data from Annotated Data deciding if it is meta data or gene expression
    if is_gene_exp or meta_id not in adata.obs.columns.to_list():
        dimred_data = dataio.get_dimred_with_exprs(adata, dimred_id, [meta_id], comps, use_raw, dimred_id_suffix, layer)
    else:
        dimred_data = dataio.get_dimred_with_metas(adata, dimred_id, [meta_id], comps, cat, dimred_id_suffix)
    cat = dimred_data[meta_id].dtype == pl.Categorical
    
    if selected_barcodes and len(selected_barcodes) > 0:
            plotting_data_removed = dimred_data.filter(~pl.col("barcode").is_in(selected_barcodes))
            plotting_data = dimred_data.filter(pl.col("barcode").is_in(selected_barcodes))
            fig = go.Figure(go.Scatter(x = plotting_data_removed["X"],
                        y = plotting_data_removed["Y"], 
                        mode="markers+text",
                        marker={"color":"#808080",
                                "opacity": 0.5,
                                "size":pt_size}))
    else:
        plotting_data = dimred_data
        fig = go.Figure()

    #set meta order list
    if cat and meta_order is None:
        meta_order = plotting_data[meta_id].cat.get_categories().to_list()
    elif meta_order is not None:
        meta_order = list(set(meta_order))
        if any([mt not in plotting_data[meta_id].cat.get_categories() for mt in meta_order]):
            raise(ValueError("Given meta cannot be found in the data!"))
   
    if cat and len(meta_order) > 100:
        warnings.warn("Number of categories in the meta data is too high. This may cause perfomance issues! Make sure meta id is not continuous")
    
    #set meta colors list
    if cat and meta_colors is None:
        meta_colors = [get_hex(c) for c in get_colors(len(meta_order))]
    elif meta_colors is not None:
        if len(meta_colors) != len(meta_order):
            raise(ValueError("Given meta colors does not match the categories in the data!"))

    if cat:
        colors = {k:v for k,v in zip(meta_order, meta_colors)}
        for i, meta_category in enumerate(meta_order):
            fig.add_trace(go.Scatter(x = plotting_data.filter(pl.col(meta_id) == meta_category)["X"],
                y = plotting_data.filter(pl.col(meta_id) == meta_category)["Y"], 
                mode="markers+text",
                hovertemplate="<b>X: </b>%{x:.2f}<br><b>Y: </b>%{y:.2f}<br><b>Category: </b>"+str(meta_category)+"<extra></extra>",
                marker={"size":pt_size,
                        "color":colors[str(meta_category)]}, name=str(meta_category)))
    else:
        fig.add_trace(go.Scatter(
                x = plotting_data["X"],
                y = plotting_data["Y"],
                mode="markers+text",
                showlegend=False,
                hovertemplate="<b>X: </b>%{x:.2f}<br><b>Y: </b>%{y:.2f}<br><b>Value: </b>%{marker.color:.2f}<extra></extra>",
                marker={"size":pt_size,
                        "color":plotting_data[meta_id],
                        "cmin":plotting_data[meta_id].min(),
                        "cmax":plotting_data[meta_id].max(),
                        "colorscale":'magma' if cont_color is None else cont_color,
                        "showscale":True}))
        
    if labels_size and cat:
        for name, data in plotting_data.group_by(meta_id):
            fig.add_annotation(x=data["X"].mean(), y=data["Y"].mean(), text=name[0], showarrow=False,
                                font=dict(size=labels_size))

    # set axis text size and legend text size
    if dimred_labels is None:
        dimred_labels = [f'{dimred_id_suffix + dimred_id}_{i}' for i in comps]
    elif isinstance(dimred_labels, str):
        dimred_labels = [f'{dimred_labels}_{i}' for i in comps]
    elif not isinstance(dimred_labels, list) or any(not isinstance(item, str) for item in dimred_labels):
        raise ValueError("dimred_labels must be a string or a list of strings")

    if height == "true_asp_ratio":
        height = width*(plotting_data["Y"].max() - plotting_data["Y"].min())/ (plotting_data["X"].max() - plotting_data["X"].min())
    
    fig = set_2d_layout(fig, ticks_font_size=ticks_font_size, 
                        dimred_labels=dimred_labels, 
                        axis_font_size=axis_font_size, 
                        legend_size=legend_size, 
                        title_size=title_size, 
                        title=title, 
                        width=width, height=height)
    return fig