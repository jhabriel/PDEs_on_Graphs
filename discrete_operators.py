import networkx as nx
import networkx.linalg as nla
import numpy as np
import scipy.sparse as sps

from typing import Tuple, Union


def orientation(node: int, edge: Tuple[int, int]) -> int:
    """Compute orientation of a node/edge pair"""

    if node == edge[1]:
        omega = 1
    elif node == edge[0]:
        omega = -1
    else:
        omega = 0

    return omega


def gradient_operator(graph: nx.DiGraph) -> sps.csc_matrix:
    """Computes gradient of a directed graph"""

    if not isinstance(graph, nx.DiGraph):
        raise TypeError("Expected a directed graph")

    grad = np.zeros((graph.number_of_edges(), graph.number_of_nodes()))
    for j, node in enumerate(graph.nodes):
        for i, edge in enumerate(graph.edges):
            grad[i, j] = orientation(node, edge)

    grad = sps.csc_matrix(grad)

    return grad


def divergence_operator(graph: nx.DiGraph) -> sps.csr_matrix:
    """Computes divergence of a directed graph"""

    if not isinstance(graph, nx.DiGraph):
        raise TypeError("Expected a directed graph")

    grad = gradient_operator(graph)
    div = sps.csr_matrix(grad.T)

    return div


def laplacian_matrix(graph: Union[nx.Graph, nx.DiGraph]) -> sps.csc_matrix:
    """Computes the Laplacian of a graph"""

    if isinstance(graph, nx.DiGraph):
        graph = graph.to_undirected()

    return nla.laplacian_matrix(graph)


def velocity_matrix(velocity: np.ndarray) -> sps.csc_matrix:
    """Creates the velocity matrix"""

    vel = sps.diags(velocity, format="csc")

    return vel


def modified_gradient_operator(gradient: sps.csc_matrix) -> sps.csc_matrix:
    """Computes the modified gradient operator needed for advection processes"""

    # Get rows and cols
    rows, cols = gradient.shape

    gradient_adv = np.zeros(shape=(rows, cols))
    for i in range(0, rows):
        for j in range(0, cols):
            if gradient[i, j] < 0:
                gradient_adv[i, j] = -gradient[i, j]

    return sps.csc_matrix(gradient_adv)


# def incidence_matrix(G: nx.Graph) -> sps.csc_matrix:
#     """Compute incidence matrix"""
#
#     K = np.zeros((G.number_of_nodes(), G.number_of_edges()))
#     for i in G.nodes:
#         for j, (k, h) in enumerate(G.edges):
#             if i == k and i > h:
#                 K[i, j] = -1
#             elif i == h and i > k:
#                 K[i, j] = -1
#             elif i == k and i < h:
#                 K[i, j] = 1
#             elif i == h and i < k:
#                 K[i, j] = 1
#             else:
#                 K[i, j] = 0
#
#     K = sps.csc_matrix(K)
#
#     return K