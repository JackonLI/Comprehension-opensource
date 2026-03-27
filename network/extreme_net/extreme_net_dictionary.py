from dataset.util.fileio import json_store
import networkx as nx

def allocate_prefix(G):
  entity_to_prefix_dict_dcs = {}
  entity_to_prefix_dict_regions = {}
  i = 0
  j = 10
  for node in list(G.nodes()):
    region_list = []
    node = " ".join(node.split()[:-1])
    for dci in range(1,6):
      entity_to_prefix_dict_dcs[f"{node} DC{dci}"] = [f"{j}.{i}.0.0/16"]
      region_list.append(f"{j}.{i}.0.0/16")
      i += 1
      if i == 256:
        i = 0
        j += 1
    entity_to_prefix_dict_regions[node] = region_list
  return entity_to_prefix_dict_dcs, entity_to_prefix_dict_regions
    
entity_to_prefix_dict_external = {
  "Ingress A": ["172.217.1.0/24"],
  "Ingress B": ["172.217.2.0/24"],
  "Ingress C": ["172.217.3.0/24"],
  "Ingress D": ["172.217.4.0/24"],
  "Ingress E": ["172.217.5.0/24"],
  "Egress F": ["172.217.6.0/24", "172.217.7.0/24"],
  "Egress G": ["172.217.8.0/24"],
  "Egress H": ["172.217.9.0/24"],
  "Egress I": ["172.217.10.0/24"],
  "Egress J": ["172.217.11.0/24", "172.217.12.0/24"]
}

prefix_to_interface_dict_external = {
  "172.217.1.0/24": [
    [("Ingress A", "China North A Router", "China North A Router"),
    ("Ingress A", "China East A Router", "China East A Router")],
    []
  ],
  "172.217.2.0/24": [
    [("Ingress B", "North Central US A Router", "North Central US A Router")],
    []
  ],
  "172.217.3.0/24": [
    [("Ingress C", "Canada Central A Router", "Canada Central A Router")],
    [],
  ],
  "172.217.4.0/24": [
    [("Ingress D", "North Europe A Router", "North Europe A Router")],
    []
  ],
  "172.217.5.0/24": [
    [("Ingress E", "Korea Central A Router", "Korea Central A Router")],
    []
  ],
  "172.217.6.0/24": [
    [],
    [("West Europe A Router", "Egress F", "West Europe A Router"),
    ("France Central A Router", "Egress F", "France Central A Router")]
  ],
  "172.217.7.0/24": [
    [],
    [("West Europe A Router", "Egress F", "West Europe A Router"),
    ("France Central A Router", "Egress F", "France Central A Router")]
  ],
  "172.217.8.0/24": [
    [],
    [("UK West A Router", "Egress G", "UK West A Router")]
  ],
  "172.217.9.0/24": [
    [],
    [("Japan West A Router", "Egress H", "Japan West A Router")]
  ],
  "172.217.10.0/24": [
    [],
    [("Germany West Central A Router", "Egress I", "Germany West Central A Router")]
  ],
  "172.217.11.0/24": [
    [],
    [("Southeast Asia A Router", "Egress J", "Southeast Asia A Router")]
  ],
  "172.217.12.0/24": [
    [],
    [("Southeast Asia A Router", "Egress J", "Southeast Asia A Router")]
  ]
}

def generate_prefix_interfaces_dcs(entity_prefix_list):
    prefix_gateways = {}
    for dc, prefixes in entity_prefix_list.items():
        gateway_name = " ".join(dc.split()[:-1])
        gateway1 = f"{gateway_name}_gateway1"
        gateway2 = f"{gateway_name}_gateway2"
        prefix_gateways[prefixes[0]] = [
            [(dc, gateway1, gateway1),
            (dc, gateway2, gateway2)],
            [(gateway1, dc, gateway1),
            (gateway2, dc, gateway2)]
        ]
    return prefix_gateways


G = nx.read_graphml('extreme_net.graphml')
entity_to_prefix_dict_dcs, entity_to_prefix_dict_regions = allocate_prefix(G)

entity_to_prefix_dict = {}
for entity, prefixes in entity_to_prefix_dict_dcs.items():
  if entity not in entity_to_prefix_dict:
    entity_to_prefix_dict[entity] = prefixes
for entity, prefixes in entity_to_prefix_dict_regions.items():
  if entity not in entity_to_prefix_dict:
    entity_to_prefix_dict[entity] = prefixes
for entity, prefixes in entity_to_prefix_dict_external.items():
  if entity not in entity_to_prefix_dict:
    entity_to_prefix_dict[entity] = prefixes

json_store(entity_to_prefix_dict,'../json/entity_prefixes.json')
  
prefix_to_interface_dict = {}
for prefixes, gateways in generate_prefix_interfaces_dcs(entity_to_prefix_dict_dcs).items():
  if prefixes not in prefix_to_interface_dict:
    prefix_to_interface_dict[prefixes] = gateways
for prefixes, gateaways in prefix_to_interface_dict_external.items():
  if prefixes not in prefix_to_interface_dict:
    prefix_to_interface_dict[prefixes] = gateaways
    
json_store(prefix_to_interface_dict,'../json/prefix_gateways.json')

# from dataset.util.fileio import json_load

# a = json_load('../json/entity_prefixes.json')
# b = json_load('../json/prefix_gateways.json')

# print(len(a),len(b))