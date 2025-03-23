from typing import List, Optional
from plotly.graph_objs import Figure

def set_2d_layout(fig: Figure, 
                  ticks_font_size:int,
                  dimred_labels:Optional[List[str]],
                  axis_font_size: Optional[int] = None,
                  legend_size: Optional[int] = None,
                  title_size: Optional[int] = None,
                  title: Optional[str] = None,
                  width:Optional[int|float|str] = "auto", 
                  height:Optional[int|float|str] = "auto")->Figure:
    '''
    Sets the layout of the 2D plotly figure.
    :param fig: 
        Plotly figure to set the layout
    :param ticks_font_size:  
        Size of the ticks in the plot
    :param dimred_labels: 
        Labels for the xy-coordinates
    :param axis_font_size:
        Size of the axis labels
    :param legend_size: 
        Size of the legend
    :param title_size: 
        Size of the title
    :param title: 
        Title of the plot
    :param width: 
        Width of the plot. If auto height is autosized by plotly (default is "auto")
    :param height: (default is "auto") 
        Height of the plot. If auto height is autosized by plotly (default is "auto") 
    
    Returns:
    --------
    plotly.Figure
        Figure with the layout set with the given parameters
    '''

    if title_size is None:
        title_size = 0
    fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=10,
            t=10+title_size,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
        xaxis=dict(tickfont=dict(size=ticks_font_size)),
        yaxis=dict(tickfont=dict(size=ticks_font_size))
    )

    if axis_font_size and dimred_labels:
        fig.update_layout(
            xaxis_title = dimred_labels[0],
            yaxis_title = dimred_labels[1],
            font = {
                "size": axis_font_size
        })
        
    if not legend_size:
        fig.update_layout(
            showlegend=False,
        )
    else:
        fig.update_layout(
        showlegend=True,
        legend = {"font":{"size":legend_size}}
        )

    if title_size and title:
        fig.update_layout(
            title = {"text":title,
                    "font":{"size":title_size}}
        )
    elif title:
        fig.update_layout(
            title = title
        )

    # set width and height of the plot
    fig.update_layout(autosize=width=="auto" or height=="auto")
    if height != "auto":
        fig.update_layout(
            height=height
        )
    if width != "auto":
        fig.update_layout(
            width=width
        )
    return fig

def set_3d_layout(fig: Figure,
                  ticks_font_size:int,
                  dimred_labels:Optional[List[str]] = None,
                  axis_font_size:Optional[int] = None,
                  legend_size:Optional[int] = None,
                  title_size:Optional[int] = None,
                  title:Optional[str] = None,
                  plt_size:Optional[int] = 480,
                  aspectmode: Optional[str] = "cube")->Figure:
    '''
    Sets the layout of the 3D plotly figure.
    :param fig:
        Plotly figure to set the layout
    :param ticks_font_size: 
        Size of the ticks in the plot
    :param dimred_labels:
        Labels for the xyz-coordinates
    :param axis_font_size: 
        Size of the axis labels
    :param legend_size: 
        Size of the legend
    :param title_size: 
        Size of the title
    :param title: 
        Title of the plot
    :param plt_size: 
        Size of the plot (default is 480)
    :param aspectmode:
        Aspect mode of the plot (default is "cube")
    Returns:
    --------
    plotly.Figure 
        Figure object with the layout set with the given parameters
    '''
    fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=10,
            t=10,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
        scene=dict(xaxis=dict(tickfont=dict(size=ticks_font_size)),
        yaxis=dict(tickfont=dict(size=ticks_font_size)),
        zaxis=dict(tickfont=dict(size=ticks_font_size)),
        aspectmode = aspectmode),
        height=plt_size
    )
    if axis_font_size and dimred_labels:
        fig.update_layout(
            scene = dict(
                xaxis_title = dimred_labels[0],
                yaxis_title = dimred_labels[1],
                zaxis_title = dimred_labels[2],        
                xaxis_title_font = dict(size=axis_font_size),
                yaxis_title_font = dict(size=axis_font_size),
                zaxis_title_font = dict(size=axis_font_size)
            ))
    else:
        fig.update_layout(
            scene = dict(
                xaxis_title= "",
                yaxis_title= "",
                zaxis_title= ""),    
        )
    if legend_size:
        fig.update_layout(
            showlegend=True,
            legend = {"font":{"size":legend_size}}
        )
    else:
        fig.update_layout(
        showlegend=False,
        )
    if title_size:
        fig.update_layout(
            title = {"text":title,
                    "font":{"size":title_size}}
        )
    elif title:
        fig.update_layout(
            title = title
        )
    return fig