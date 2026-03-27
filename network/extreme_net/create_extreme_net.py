import networkx as nx
import random

def generate_extreme(G):
    new_G = nx.graph.Graph()
    new_name = ['A', 'B', 'C', 'D', 'E', 'F']
    # for each node in G, separate it into 6 nodes
    for node in list(G.nodes()):
        new_node = " ".join(node.split()[:-1])
        for i in range(6):
            new_G.add_node(f'{new_node} {new_name[i]} Router', location=G.nodes[node]['location'], pos=str((eval(G.nodes[node]['pos'])[0] + random.uniform(-0.1, 0.1), eval(G.nodes[node]['pos'])[1] + random.uniform(-0.1, 0.1))))
        # add edges between the 6 nodes as a cycle
        for i in range(6):
            new_G.add_edge(f'{new_node} {new_name[i]} Router', f'{new_node} {new_name[(i+1)%6]} Router')
    
    # for every edge in old G, in the new_G, choose random 2 nodes of source and destination in the 6 nodes for new connection
    for edge in list(G.edges()):
        src, dst = edge
        new_src, new_dst = " ".join(src.split()[:-1]), " ".join(dst.split()[:-1])
        connection_set = set()
        while len(connection_set) < 2:
            src_i = random.randint(0, 5)
            dst_i = random.randint(0, 5)
            connection_set.add((src_i, dst_i))
        for src_dst in connection_set:
            src_i, dst_i = src_dst
            if f'{new_src} {new_name[src_i]} Router' not in new_G.nodes():
                print(f'{new_src} {new_name[src_i]} Router not in new_G.nodes()')
            if f'{new_dst} {new_name[dst_i]} Router' not in new_G.nodes():
                print(f'{new_dst} {new_name[dst_i]} Router not in new_G.nodes()')
            new_G.add_edge(f'{new_src} {new_name[src_i]} Router', f'{new_dst} {new_name[dst_i]} Router')
    return new_G
    
G = nx.read_graphml('../../cloud_net/topology/cloud_net.graphml')        

G = generate_extreme(G)

# count the number of nodes and edges
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
print(f"Number of nodes: {num_nodes}")
print(f"Number of edges: {num_edges}")

# Save the graph to a GraphML file
nx.write_graphml(G, "extreme_net.graphml")