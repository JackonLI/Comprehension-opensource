import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from adjustText import adjust_text

G = nx.Graph()

# North America
# Add nodes with slightly different positions for those in the same city
G.add_node('West US 2', location='Washington', pos=(38.9072, -77.0369))  
G.add_node('West US', location='California', pos=(36.7783, -119.4179))
G.add_node('West US 3', location='Arizona', pos=(34.0489, -111.0937))
G.add_node('West Central US', location='Wyoming', pos=(43.0750, -107.2903))
G.add_node('Mexico Central', location='Queretaro State', pos=(20.5888, -100.3899))
G.add_node('South Central US', location='Texas', pos=(31.9686, -99.9018))
G.add_node('Central US', location='Iowa', pos=(41.8780, -93.0977))
G.add_node('North Central US', location='Illinois', pos=(40.6331, -89.3985))
G.add_node('East US 3', location='Georgia', pos=(33.7490, -84.3880))
G.add_node('East US 2', location='Virginia', pos=(37.4316, -78.6569))
G.add_node('East US', location='Virginia', pos=(37.5407, -77.4360))
G.add_node('Canada Central', location='Toronto', pos=(43.6511, -79.3837))
G.add_node('Canada East', location='Quebec City', pos=(46.8139, -71.2082))

# Add edges
G.add_edge('West US 2', 'West US')
G.add_edge('West US 2', 'West Central US')
G.add_edge('West US', 'West US 3')
G.add_edge('West US', 'West Central US')
G.add_edge('West US 3', 'West Central US')
G.add_edge('West US 3', 'South Central US')
G.add_edge('West Central US', 'Central US')
G.add_edge('West Central US', 'South Central US')
G.add_edge('South Central US', 'Mexico Central')
G.add_edge('South Central US', 'Central US')
G.add_edge('South Central US', 'East US 2')
G.add_edge('Central US', 'North Central US')
G.add_edge('Central US', 'Canada Central')
G.add_edge('North Central US', 'Canada Central')
G.add_edge('North Central US', 'East US 2') 
G.add_edge('East US 3', 'East US 2')
G.add_edge('East US 3', 'South Central US')
G.add_edge('East US 2', 'East US')
G.add_edge('East US', 'Canada Central')
G.add_edge('East US', 'Canada East')
G.add_edge('Canada Central', 'Canada East')

# South America
G.add_node('Brazil South', location='Sao Paulo State', pos=(-23.5505, -46.6333))
G.add_node('Chile Central', location='Santiago', pos=(-33.4489, -70.6693))

G.add_edge('Brazil South', 'East US 3')
G.add_edge('Brazil South', 'East US 2')
G.add_edge('Brazil South', 'South Central US')
G.add_edge('Brazil South', 'Chile Central')

# Europe
G.add_node('North Europe', location='Ireland', pos=(53.1424, -7.6921))
G.add_node('UK West', location='Cardiff', pos=(51.4816, -3.1791))
G.add_node('UK South', location='London', pos=(51.5074, -0.1278))
G.add_node('Spain Central', location='Madrid', pos=(40.4168, -3.7038))
G.add_node('France Central', location='Paris', pos=(48.8566, 2.3522))
G.add_node('West Europe', location='Netherlands', pos=(52.3676, 4.9041))
G.add_node('Germany West Central', location='Frankfurt', pos=(50.1109, 8.6821))
G.add_node('Switzerland North', location='Zurich', pos=(47.3769, 8.5417))
G.add_node('Italy North', location='Milan', pos=(45.4642, 9.1900))
G.add_node('Norway East', location='Oslo', pos=(59.9139, 10.7522))
G.add_node('Sweden Central', location='Gavle and Sandviken', pos=(60.6749, 17.1413))
G.add_node('Poland Central', location='Warsaw', pos=(52.2297, 21.0122))
G.add_node('Belgium Central', location='Brussels', pos=(50.8503, 4.3517))
G.add_node('Denmark East', location='Copenhagen', pos=(55.6761, 12.5683))
G.add_node('Finland Central', location='Helsinki', pos=(60.1695, 24.9354))
G.add_node('Austria East', location='Vienna', pos=(48.2082, 16.3738))
G.add_node('Greece Central', location='Athens', pos=(37.9838, 23.7275))

# Add edges
G.add_edge('Canada East', 'UK West')
G.add_edge('East US', 'Spain Central')
G.add_edge('North Europe', 'UK West')
G.add_edge('UK West', 'UK South')
G.add_edge('UK West', 'France Central')
G.add_edge('Spain Central', 'France Central')
G.add_edge('Spain Central', 'Italy North')
G.add_edge('UK South', 'France Central')
G.add_edge('UK South', 'Norway East')
G.add_edge('France Central', 'West Europe')
G.add_edge('France Central', 'Switzerland North')
G.add_edge('France Central', 'Italy North')
G.add_edge('West Europe', 'Sweden Central')
G.add_edge('West Europe', 'Germany West Central')
G.add_edge('Germany West Central', 'Sweden Central')
G.add_edge('Germany West Central', 'Poland Central')
G.add_edge('Germany West Central', 'Switzerland North')
G.add_edge('Switzerland North', 'Italy North')
G.add_edge('Italy North', 'Poland Central')
G.add_edge('Norway East', 'Sweden Central')
G.add_edge('Belgium Central', 'France Central')
G.add_edge('Belgium Central', 'Germany West Central')
G.add_edge('Denmark East', 'Germany West Central')
G.add_edge('Denmark East', 'Sweden Central')
G.add_edge('Finland Central', 'Sweden Central')
G.add_edge('Austria East', 'Germany West Central')
G.add_edge('Austria East', 'Italy North')
G.add_edge('Greece Central', 'Italy North')
G.add_edge('Greece Central', 'Spain Central')

# Africa
G.add_node('South Africa North', location='Johannesburg', pos=(-26.2041, 28.0473))
G.add_edge('South Africa North', 'Spain Central')

# Asia
G.add_node('Israel Central', location='Israel', pos=(31.0461, 34.8516))
G.add_node('Qatar Central', location='Doha', pos=(25.276987, 51.520008))
G.add_node('UAE North', location='Dubai', pos=(25.2048, 55.2708))
G.add_node('Central India', location='Pune', pos=(18.5204, 73.8567))
G.add_node('South India', location='Chennai', pos=(13.0827, 80.2707))
G.add_node('Southeast Asia', location='Singapore', pos=(1.3521, 103.8198))
G.add_node('East Asia', location='Hong Kong', pos=(22.3193, 114.1694))
G.add_node('China North', location='Beijing', pos=(39.9042, 116.4074))
G.add_node('China North 3', location='Hebei', pos=(39.0500, 116.2900))
G.add_node('China North 2', location='Beijing', pos=(39.9050, 116.4075))
G.add_node('China East 2', location='Shanghai', pos=(31.2304, 121.4737))
G.add_node('China East', location='Shanghai', pos=(31.2305, 121.4738))
G.add_node('Korea Central', location='Seoul', pos=(37.5665, 126.9780))
G.add_node('Japan West', location='Osaka', pos=(34.6937, 135.5023))
G.add_node('Japan East', location='Tokyo', pos=(35.6895, 139.6917))
G.add_node('Saudi Arabia East', location='Dammam', pos=(26.3927, 49.9777))
G.add_node('India South Central', location='Hyderabad', pos=(17.3850, 78.4867))
G.add_node('Malaysia West', location='Kuala Lumpur', pos=(3.1390, 101.6869))
G.add_node('Indonesia Central', location='Jakarta', pos=(-6.2088, 106.8456))
G.add_node('Taiwan North', location='Taipei', pos=(25.0320, 121.5654))

# Add edges
G.add_edge('South Africa North', 'Israel Central')
G.add_edge('Israel Central', 'Spain Central')
G.add_edge('Israel Central', 'Italy North')
G.add_edge('Israel Central', 'Southeast Asia')
G.add_edge('Israel Central', 'UAE North')
G.add_edge('Qatar Central', 'UAE North')
G.add_edge('UAE North', 'Central India')
G.add_edge('UAE North', 'Southeast Asia')
G.add_edge('Central India', 'Spain Central')
G.add_edge('Central India', 'South India')
G.add_edge('South India', 'Southeast Asia')
G.add_edge('Southeast Asia', 'Spain Central')
G.add_edge('Southeast Asia', 'Italy North')
G.add_edge('Southeast Asia', 'East Asia')
G.add_edge('Southeast Asia', 'Korea Central')
G.add_edge('Southeast Asia', 'Japan East')
G.add_edge('East Asia', 'China North')
G.add_edge('East Asia', 'China East')
G.add_edge('East Asia', 'China East 2')
G.add_edge('East Asia', 'Korea Central')
G.add_edge('East Asia', 'Japan East')
G.add_edge('China North', 'China North 3')
G.add_edge('China North', 'China North 2')
G.add_edge('China North 3', 'China North 2')
G.add_edge('China North 2', 'China East')
G.add_edge('China East 2', 'China East')
G.add_edge('China East', 'Japan West')
G.add_edge('China East', 'Korea Central')
G.add_edge('Korea Central', 'Japan West')
G.add_edge('Korea Central', 'Japan East')
G.add_edge('Japan West', 'Japan East')
G.add_edge('Japan East', 'West US 2')
G.add_edge('East Asia', 'West US')
G.add_edge('Southeast Asia', 'West US')
G.add_edge('Saudi Arabia East', 'Qatar Central')
G.add_edge('India South Central', 'Central India')
G.add_edge('India South Central', 'South India')
G.add_edge('Malaysia West', 'Southeast Asia')
G.add_edge('Indonesia Central', 'Southeast Asia')
G.add_edge('Taiwan North', 'East Asia')
G.add_edge('Taiwan North', 'Japan East')
G.add_edge('Taiwan North', 'Korea Central')

# Australia
G.add_node('Australia Southeast', location='Victoria', pos=(-37.8136, 144.9631))
G.add_node('Australia East', location='New South Wales', pos=(-33.8688, 151.2093))
G.add_node('Australia Central', location='Canberra', pos=(-35.2809, 149.1300))
G.add_node('New Zealand North', location='Auckland', pos=(-36.8485, 174.7633))

# Add edges
G.add_edge('Australia Southeast', 'Southeast Asia')
G.add_edge('Australia Southeast', 'Australia East')
G.add_edge('Australia Southeast', 'Australia Central')
G.add_edge('Australia East', 'Australia Central')
G.add_edge('Australia Central', 'East Asia')
G.add_edge('Australia Central', 'Japan East')
G.add_edge('Australia Central', 'West US')
G.add_edge('Australia Central', 'New Zealand North')

# For all nodes, add a label type='backbone' for each node
for node in G.nodes():
    G.add_node(node, type='backbone')

pos = nx.get_node_attributes(G, 'pos')

nodes = gpd.GeoDataFrame(
    {'id': list(pos.keys())},
    geometry=[Point(lon, lat) for lat, lon in pos.values()],
    crs="EPSG:4326"
)

# Set up the plot
fig, ax = plt.subplots(figsize=(15, 10))

# Plot the backbone nodes, omit the gateway nodes
nodes[nodes['id'].str.contains('gateway') == False].plot(ax=ax, color='red', markersize=100, label='Backbone Nodes')

# Draw edges
for edge in G.edges():
    x = [pos[edge[0]][1], pos[edge[1]][1]]
    y = [pos[edge[0]][0], pos[edge[1]][0]]
    ax.plot(x, y, color='blue', linewidth=1)

# Create a list of text objects for labels, only show the backbone nodes
texts = []
for node, data in G.nodes(data=True):
    if data['type'] == 'backbone':
        x, y = pos[node]
        texts.append(plt.text(y, x, node, fontsize=8))

# Adjust text to prevent overlap
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))

# # Set labels and title
# for node, (lat, lon) in pos.items():
#     ax.text(lon, lat, node, fontsize=8, ha='right')

ax.set_title('Simulated Azure Cloud Network Graph')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()

for node, data in G.nodes(data=True):
    if 'pos' in data:
        data['pos'] = str(data['pos'])  # Convert tuple to string

# Save the graph to a PNG file
plt.savefig("cloud_net.png")

G = nx.relabel_nodes(G, lambda x: f"{x} Router")

# Save the graph to a GraphML file
nx.write_graphml(G, "cloud_net.graphml")

# count the number of nodes and edges
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
print(f"Number of nodes: {num_nodes}")
print(f"Number of edges: {num_edges}")
