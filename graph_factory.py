import networkx as nx
import numpy as np


def graph_wave_equation_example() -> nx.DiGraph:
    """Create directed graph for the wave equation exampple"""

    # Generator of equally spaced circular point clouds
    def rtpairs(r, n):
        for i in range(len(r)):
            for j in range(n[i]):
                yield r[i], j * (2 * np.pi / n[i])

    # Number of points per ring (T) and radius of each concentric circle (R)
    T = [1, 10, 20, 30, 40, 50, 60, 70, 80]
    R = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    # Initialize graph
    G = nx.DiGraph()

    # Loop through the point clouds and add nodes of the graph
    counter = 0
    for r, t in rtpairs(R, T):

        G.add_node(counter)
        G.nodes[counter]["pos"] = (r * np.cos(t), r * np.sin(t))

        # Label nodes (This for sure can be written in a non-hardcoded way)
        if r == 0:
            G.nodes[counter]["ring"] = 0
        elif r == 0.1:
            G.nodes[counter]["ring"] = 1
        elif r == 0.2:
            G.nodes[counter]["ring"] = 2
        elif r == 0.3:
            G.nodes[counter]["ring"] = 3
        elif r == 0.4:
            G.nodes[counter]["ring"] = 4
        elif r == 0.5:
            G.nodes[counter]["ring"] = 5
        elif r == 0.6:
            G.nodes[counter]["ring"] = 6
        elif r == 0.7:
            G.nodes[counter]["ring"] = 7
        elif r == 0.8:
            G.nodes[counter]["ring"] = 8

        # Increase counter
        counter += 1

    # Create node list per ring
    nodes_rings = [[0]]
    for ring in range(1, len(T)):
        nodes_rings.append([node for node, data in G.nodes(data=True) if data["ring"] == ring])

    # Ring 0 (central node)
    for outter_node in nodes_rings[1]:
        G.add_edge(0, outter_node)

    # The rest of the rings
    for ring, nodes_ring in enumerate(nodes_rings[1:]):
        for inner_node in nodes_rings[ring]:
            inner_x = G.nodes[inner_node]["pos"][0]
            inner_y = G.nodes[inner_node]["pos"][1]
            dist = []
            for outter_node in nodes_rings[ring + 1]:
                outter_x = G.nodes[outter_node]["pos"][0]
                outter_y = G.nodes[outter_node]["pos"][1]
                norm = np.sqrt((inner_x - outter_x) ** 2 + (inner_y - outter_y) ** 2)
                dist.append((norm, outter_node))
            closest_nei = [nei for _, nei in sorted(dist)[:5]]
            for nei in closest_nei:
                G.add_edge(inner_node, nei)

    return G
