# %% Import packages
import networkx as nx
import networkx.linalg as nla
import numpy as np
import scipy.sparse as sps
import graph_utils as gu
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


# %% Manually create a graph

G = nx.DiGraph()

# Add nodes
G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)

# Add edges
G.add_edge(0, 1)
G.add_edge(2, 1)
G.add_edge(3, 2)
G.add_edge(4, 3)
G.add_edge(0, 4)
G.add_edge(0, 2)

nx.draw_networkx(G, arrows=True, with_labels=True)
plt.show()

# Gradient, divergence, and Laplacian of the graph
gradient = gradient_operator(G)
divergence = divergence_operator(G)
laplacian = laplacian_matrix(G)
velocity = velocity_matrix(np.ones(G.number_of_edges()))
advection_gradient = modified_gradient_operator(gradient)
advection_laplacian = divergence * velocity * advection_gradient


#%% Run a simulation then

# Initial conditions
u0 = 0 * np.ones(G.number_of_nodes())
u0[4] = 1  # set concentration equal to 1 at node 4

# Time parameters
T = 2  # final time
dt = 0.01  # time step
times = list(np.linspace(0, T, int(T/dt)+1))  # times

# Advection Laplacian
V = velocity_matrix(np.ones(G.number_of_edges()))
Div = divergence_operator(G)
Grad_adv = modified_gradient_operator(gradient_operator(G))
L_adv = -Div * V * Grad_adv

# Matrix of coefficients
eye = np.eye(G.number_of_nodes())
A = eye + dt * L_adv

# Store solution
sols = [u0]

for t in times[1:]:

    # Solve linear system
    u = np.linalg.solve(A.A, u0)
    sols.append(u)

    # Update value for next time step
    u0 = u


#%% Plotting
pos = nx.circular_layout(G)
colors = range(G.number_of_nodes())
cmap = plt.cm.autumn
vmin = 0
vmax = 1
for sol in sols:
    nx.draw_networkx(G,
                     pos,
                     arrows=True,
                     with_labels=False,
                     node_color=sol,
                     node_size=800,
                     cmap=plt.cm.autumn,
                     vmin=vmin,
                     vmax=vmax
                     )
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    plt.colorbar(sm)

    #nx.draw(G, pos, node_color=sol, node_size=800, cmap=plt.cm.inferno)
    plt.show()

#%%
print(u)