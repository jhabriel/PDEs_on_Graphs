# %% Import packages
import networkx as nx
import networkx.linalg as nla
import numpy as np
import scipy.sparse as sps
import graph_utils as gu
import graph_factory as gf
import discrete_operators as do
import matplotlib.pyplot as plt


from typing import Tuple, Union

import plotly.io as pio
pio.renderers.default = "browser"


# %% Functions
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


def incidence_matrix(G: nx.Graph) -> sps.csc_matrix:
    """Compute incidence matrix"""

    K = np.zeros((G.number_of_nodes(), G.number_of_edges()))
    for i in G.nodes:
        for j, (k, h) in enumerate(G.edges):
            if i == k and i > h:
                K[i, j] = -1
            elif i == h and i > k:
                K[i, j] = -1
            elif i == k and i < h:
                K[i, j] = 1
            elif i == h and i < k:
                K[i, j] = 1
            else:
                K[i, j] = 0

    K = sps.csc_matrix(K)

    return K


# %%
G = gf.graph_wave_equation_example()

# Parameters
T = 4  # final time
tau = 0.01  # time step
times = list(np.linspace(0, T, int(T / tau) + 1))  # times
c = 2  # wave speed
c_lim = (-0.8501321357603164, 1.0)
amp = 10
freq = 5

# Operators
L = do.laplacian_matrix(G)
I = np.eye(G.number_of_nodes())
A = 2 * I - tau ** 2 * c ** 2 * L.A

# First time level
u0 = np.zeros(G.number_of_nodes())
u0[0] = 1
edge_trace = gu.get_edge_trace(G)
node_trace = gu.get_node_trace(G, color_vals=u0, node_size=10, c_min_max=c_lim)
data = [[edge_trace, node_trace]]
sol = [u0]

# Second time level
f1 = np.zeros(G.number_of_nodes())
#f1[0] = 10
u1 = 0.5 * np.dot(A, u0) + 0.5 * tau ** 2 * f1
node_trace = gu.get_node_trace(G, color_vals=u1, node_size=10, c_min_max=c_lim)
data.append([edge_trace, node_trace])
sol.append(u1)

f = np.zeros(G.number_of_nodes())

for t in times[2:]:

    # Solve explicitly
    # f[0] = 10
    # if t > 2:
    #     f[0] = -10

    u = np.dot(A, u1) - u0 + tau ** 2 * f
    sol.append(u)

    # Update node trace
    node_trace = gu.get_node_trace(G, color_vals=u, node_size=10, c_min_max=c_lim)
    data.append([edge_trace, node_trace])

    # Update previous values
    u0 = u1
    u1 = u

c_lim = (np.min(sol), np.max(sol))

#%%
fig = gu.animate_graph(
    data,
    times,
    show_animation=True,
    title="Wave equation on a graph"
)



