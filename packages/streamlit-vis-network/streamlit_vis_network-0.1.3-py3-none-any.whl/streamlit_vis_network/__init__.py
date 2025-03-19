import os
from typing import Any, Dict, List, Optional, Union

import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_component_func = components.declare_component(
    "streamlit_vis_network", path=build_dir
)


# Wrapper function for Streamlit use
def streamlit_vis_network(
    nodes:List[Dict[str, Any]],
    edges:List[Dict[str, Any]],
    options:Dict[str, Any]={},
    height:Optional[int]=None,
    width:Optional[int]=None,
    key:Union[str, None]=None
) -> Union[List[List[str]], None]:
    """Create a new instance of the vis.js network visualization.

    Args:
        nodes: List of nodes to visualize.
        edges: List of edges to visualize.
        options: Configuration settings for the vis.js network visualization.
            See https://visjs.github.io/vis-network/docs/network/#options for more
            information. Defaults to None.
        height: Desired height of the container expressed in pixels. If not supplied
            height is set to parent container height.
        width: Desired width of the container expressed in pixels. If not supplied
            width is set to parent container width.
        key: An optional string or integer to use as the unique key for the widget.
            If this is omitted, a key will be generated for the widget based on its
            content. No two widgets may have the same key. Defaults to None.

    Returns:
        Returns the id of the currently selected node, if selected, otherwise returns
        None.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_vis_network import streamlit_vis_network
    >>>
    >>> nodes = [{'id': 1, "label": "node 1"}, {'id': 2, "label": "node 2"}]
    >>> edges = [{"from": 1, "to": 2, "label": "edge"}]
    >>>
    >>> selected_node = streamlit_vis_network(nodes=nodes, edges=edges)
    >>>
    >>> st.write(f"Selected node: {selected_node}")
    """
    if height:
        _height = f"{height}px"
    else:
        _height = "auto"
    if width:
        _width = f"{width}px"
    else:
        _width = "auto"

    return _component_func(
        nodes=nodes,
        edges=edges,
        options=options,
        height=_height,
        width=_width,
        key=key
    )
