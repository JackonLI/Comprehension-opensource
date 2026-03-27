import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Create a new graph
G = nx.Graph()

# Add central, library, and general education nodes
G.add_node('Central_Switch1', type='switch')
G.add_node('Central_Switch2', type='switch')
G.add_node('Central_Switch3', type='switch')
G.add_edge('Central_Switch1', 'Central_Switch2')
G.add_edge('Central_Switch2', 'Central_Switch3')
G.add_edge('Central_Switch3', 'Central_Switch1')
G.add_node('Library_Switch1', type='switch')
G.add_node('General_Education_Switch1', type='switch')

# Add faculties, switches, and routers
faculties = ['Arts', 'Business_Administration', 'Education', 'Law', 'Engineering', 'Science', 'Social_Science', 'Medicine', 'Graduate_School']
switch_labels = ['firewall', 'lab', 'office', 'classroom']
for faculty in faculties:
    # Add switches for each faculty
    for switch_id in range(1, 5):
        switch_name = f"{faculty}_Switch{switch_id}"
        G.add_node(switch_name, type='switch', label_location=faculty, label_subnet = switch_labels[switch_id-1])
    # Connect 4 switches in a ring
    for i in range(1, 4):
        G.add_edge(f"{faculty}_Switch{i}", f"{faculty}_Switch{i+1}")
    G.add_edge(f"{faculty}_Switch4", f"{faculty}_Switch1")

# Connect faculties
G.add_edge('Arts_Switch1', 'Business_Administration_Switch1')
G.add_edge('Arts_Switch1', 'Education_Switch1')
G.add_edge('Business_Administration_Switch1', 'Law_Switch1')
G.add_edge('Education_Switch1', 'Central_Switch1')
G.add_edge('Education_Switch1', 'Engineering_Switch1')
G.add_edge('Law_Switch1', 'Central_Switch1')
G.add_edge('Law_Switch1', 'Engineering_Switch1')
G.add_edge('Central_Switch1', 'Library_Switch1')
G.add_edge('Central_Switch1', 'Science_Switch1')
G.add_edge('Engineering_Switch1', 'Library_Switch1')
G.add_edge('Engineering_Switch1', 'Science_Switch1')
G.add_edge('Library_Switch1', 'Science_Switch1')
G.add_edge('Library_Switch1', 'Medicine_Switch1')
G.add_edge('Science_Switch1', 'Graduate_School_Switch1')
G.add_edge('Social_Science_Switch1', 'Medicine_Switch1')
G.add_edge('Social_Science_Switch1', 'Graduate_School_Switch1')
G.add_edge('Medicine_Switch1', 'Graduate_School_Switch1')
G.add_edge('Medicine_Switch1', 'General_Education_Switch1')
G.add_edge('Graduate_School_Switch1', 'General_Education_Switch1')
G.add_edge('Central_Switch2', 'Engineering_Switch2')
G.add_edge('Central_Switch2', 'Social_Science_Switch2')
G.add_edge('Central_Switch2', 'Medicine_Switch2')
G.add_edge('Central_Switch3', 'Arts_Switch2')
G.add_edge('Central_Switch3', 'Business_Administration_Switch2')
G.add_edge('Central_Switch3', 'Graduate_School_Switch2')
G.add_edge('Central_Switch3', 'General_Education_Switch1')
G.add_edge('Central_Switch3', 'Library_Switch1')

# Define positions for a custom layout
pos = {}

# Arrange faculties in a circular layout
angle_step = 360 / len(faculties)
radius = 10

for i, faculty in enumerate(faculties):
    angle = i * angle_step
    # Convert angle to radians
    angle_rad = angle * (3.14159265 / 180)

    # Calculate faculty center position
    x_faculty = radius * np.cos(angle_rad)
    y_faculty = radius * np.sin(angle_rad)

    # Set positions for switches within each faculty
    x_offsets = [0, -0.5, 0, 0.5]
    y_offsets = [0, 0.33, 1, 0.67]
    for switch_id in range(1, 5):
        switch_name = f"{faculty}_Switch{switch_id}"
        # Offset for switches within the same faculty
        pos[switch_name] = (x_faculty + 2*x_offsets[switch_id-1], y_faculty + 2*y_offsets[switch_id-1])

# Set positions for central nodes
pos['Central_Switch1'] = (0, 1)
pos['Central_Switch2'] = (-1, 0.1)
pos['Central_Switch3'] = (1, -0.2)
pos['Library_Switch1'] = (3, 3)
pos['General_Education_Switch1'] = (-3, -3)

# print the graph
print(G.nodes(data=True))

# Draw the graph
plt.figure(figsize=(12, 12))
nx.draw(G, pos, with_labels=True, node_size=500, node_color="lightblue", font_size=8)
# plt.show()
# Save the graph to a PNG file
plt.savefig("campus_net.png")

# Save the graph to a GraphML file
nx.write_graphml(G, "campus_net.graphml")