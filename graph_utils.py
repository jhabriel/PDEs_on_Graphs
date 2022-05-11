import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt

from typing import Union


def plot_directed_graph(G: nx.DiGraph, show_plot=False) -> None:
    """Plot a directed graph using matplotlib"""

    pos = nx.circular_layout(G, scale=2)
    plt.figure(figsize=(10, 7))
    nx.draw_networkx(G,
                     pos,
                     arrows=True,
                     with_labels=True,
                     node_size=800,
                     alpha=0.8
                     )
    if show_plot:
        plt.show()


def assign_node_position(G: Union[nx.Graph, nx.DiGraph],
                         layout: str = "circular"
                         ) -> None:
    """Assign node position as attribute to each node"""

    if layout == "circular":
        pos = nx.circular_layout(G)

    for node in G.nodes:
        G.nodes[node]["pos"] = (pos[node][0], pos[node][1])


def get_edge_trace(G: nx.Graph) -> go.Scatter:
    """Produce edge_trace for plotting with plotly"""

    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    return edge_trace


def get_node_trace(G: nx.Graph,
                   color_vals=None,
                   node_size=10,
                   c_min_max=(0, 1)
                   ) -> go.Scatter:
    """Produce node_trace for plotting with plotly"""

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]["pos"]
        node_x.append(x)
        node_y.append(y)

    if color_vals is not None:

        node_text = ["{:.3}".format(color_val) for color_val in color_vals]
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                reversescale=True,
                cmin=c_min_max[0],
                cmax=c_min_max[1],
                color=color_vals,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale="Hot",
                size=node_size,
                colorbar=dict(
                    thickness=15, title="Value", xanchor="left", titleside="right"
                ),
                line_width=2,
            ),
            text=node_text,
        )

    else:

        node_text = [f"# of connections: {str(len(adj[1]))}" for adj in G.adjacency()]
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color="Black",
                size=node_size,
                line_width=2,
            ),
            text=node_text,
        )

    return node_trace


def plot_graph(G: nx.Graph,
               show_plot=False,
               node_size=10,
               fig_size=(500, 500)) -> go.Figure:
    """Plot graph"""

    num_edges = G.number_of_edges()
    edge_trace = get_edge_trace(G)

    num_nodes = G.number_of_nodes()
    node_trace = get_node_trace(G, node_size=node_size)

    node_text = []
    for (node, adj) in zip(range(0, G.number_of_nodes()), G.adjacency()):
        node_text.append(f"v_{node} has {str(len(adj[1]))} connections")
    node_trace.text = node_text

    title = f"Graph with {num_nodes} nodes and {num_edges} edges"

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=fig_size[0],
            height=fig_size[1],
        ),
    )

    if show_plot:
        fig.show()

    return fig


def animate_graph(data: list,
                  times: list,
                  show_animation=False,
                  title="",
                  fig_size=(900, 600)
                  ) -> go.Figure:
    """Produce graph animation"""

    # make figure
    fig_dict = {"data": [], "layout": {}, "frames": []}

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {
        "showgrid": False,
        "zeroline": False,
        "showticklabels": False,
    }
    fig_dict["layout"]["yaxis"] = {
        "showgrid": False,
        "zeroline": False,
        "showticklabels": False,
    }
    fig_dict["layout"]["title"] = {"text": title}
    fig_dict["layout"]["titlefont_size"] = 20
    fig_dict["layout"]["showlegend"] = False
    fig_dict["layout"]["width"] = fig_size[0]
    fig_dict["layout"]["height"] = fig_size[1]
    fig_dict["layout"]["margin"] = {"b": 20, "l": 5, "r": 5, "t": 40}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 50, "redraw": False},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 30,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ]

    # set data
    fig_dict["data"] = data[0]

    # set sliders
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Time:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 30, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    # make frames
    for idx, time in enumerate(times):
        frame = {"data": data[idx], "name": str("{:.3}".format(time))}
        fig_dict["frames"].append(frame)

        slider_step = {
            "args": [
                ["{:.3}".format(time)],
                {
                    "frame": {"duration": 30, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 30},
                },
            ],
            "label": "{:.3}".format(time),
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)
        fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    if show_animation:
        fig.show()

    return fig
