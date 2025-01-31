import json
from dataset.util.fileio import json_store, json_load

# summerize all names of departments
mt_list = ["Arts", "Business_Administration", "Education", "Engineering", "General_Education", "Graduate_School", "Law", "Medicine", "Science", "Social_Science"]

# entity_to_prefix_dict: dictionary that maps entity name to its IP prefix
entity_to_prefix_dict = {
    "Central Control": ["10.0.1.0/24", "10.0.13.0/24", "10.0.14.0/24"],
    "Library": ["10.0.2.0/24"],
    "General_Education": ["10.0.3.0/24"],
    "Arts": ["10.0.4.0/24"],
    "Arts firewall": ["10.0.4.0/32"],
    "Arts lab": ["10.0.4.32/27", "10.0.4.64/26"],
    "Arts office": ["10.0.4.128/26"],
    "Arts classroom": ["10.0.4.192/26"],
    "Arts exam area": ["10.0.4.32/27", "10.0.4.64/26", "10.0.4.192/26"],
    "Business_Administration": ["10.0.5.0/24"],
    "Business_Administration firewall": ["10.0.5.0/32"],
    "Business_Administration lab": ["10.0.5.64/26"],
    "Business_Administration office": ["10.0.5.128/26"],
    "Business_Administration classroom": ["10.0.5.192/26"],
    "Education": ["10.0.6.0/24"],
    "Education firewall": ["10.0.6.0/32"],
    "Education lab": ["10.0.6.64/26"],
    "Education office": ["10.0.6.128/26"],
    "Education classroom": ["10.0.6.192/26"],
    "Law": ["10.0.7.0/24"],
    "Law firewall": ["10.0.7.0/32"],
    "Law lab": ["10.0.7.64/26"],
    "Law office": ["10.0.7.128/26"],
    "Law classroom": ["10.0.7.192/26"],
    "Engineering": ["10.0.8.0/24"],
    "Engineering firewall": ["10.0.8.0/32"],
    "Engineering lab": ["10.0.8.32/27", "10.0.8.64/26"],
    "Engineering office": ["10.0.8.128/26"],
    "Engineering classroom": ["10.0.8.192/26"],
    "Engineering exam area": ["10.0.8.32/27", "10.0.8.64/26", "10.0.8.192/26"],
    "Science": ["10.0.9.0/24"],
    "Science firewall": ["10.0.9.0/32"],
    "Science lab": ["10.0.9.64/26"],
    "Science office": ["10.0.9.128/26"],
    "Science classroom": ["10.0.9.192/26"],
    "Social_Science": ["10.0.10.0/24"],
    "Social_Science firewall": ["10.0.10.0/32"],
    "Social_Science lab": ["10.0.10.64/26"],
    "Social_Science office": ["10.0.10.128/26"],
    "Social_Science classroom": ["10.0.10.192/26"],
    "Medicine": ["10.0.11.0/24"],
    "Medicine firewall": ["10.0.11.0/32"],
    "Medicine lab": ["10.0.11.64/26"],
    "Medicine office": ["10.0.11.128/26"],
    "Medicine classroom": ["10.0.11.192/26"],
    "Graduate_School": ["10.0.12.0/24"],
    "Graduate_School firewall": ["10.0.12.0/32"],
    "Graduate_School lab": ["10.0.12.64/26"],
    "Graduate_School office": ["10.0.12.128/26"],
    "Graduate_School classroom": ["10.0.12.192/26"],
    "Ingress A": ["69.63.1.0/24"],
    "Ingress B": ["69.63.2.0/24"],
    "Ingress C": ["69.63.3.0/24"],
    "Ingress D": ["69.63.4.0/24"],
    "Ingress E": ["69.63.5.0/24"],
    "Egress F": ["69.63.6.0/24", "69.63.7.0/24"],
    "Egress G": ["69.63.8.0/24"],
    "Egress H": ["69.63.9.0/24"],
    "Egress I": ["69.63.10.0/24"],
    "Egress J": ["69.63.11.0/24", "69.63.12.0/24"]
}


# prefix_to_interface_dict: dictionary that maps IP prefix to its interfaces
# <prefix>: (<source>, <destination>, <gateway location>)
prefix_to_interface_dict = {
    # Central Control: Central_Switch1, Central_Switch2, Central_Switch3
    '10.0.1.0/24': [[('Central Control', 'Central_Switch1', 'Central_Switch1')], [('Central_Switch1', 'Central Control', 'Central_Switch1')]],
    '10.0.13.0/24': [[('Central Control', 'Central_Switch2', 'Central_Switch2')], [('Central_Switch2', 'Central Control', 'Central_Switch2')]],
    '10.0.14.0/24': [[('Central Control', 'Central_Switch3', 'Central_Switch3')], [('Central_Switch3', 'Central Control', 'Central_Switch3')]],
    # Library: Library_Switch1
    '10.0.2.0/24': [[('Library', 'Library_Switch1', 'Library_Switch1')], [('Library_Switch1', 'Library', 'Library_Switch1')]],
    # General Education: General_Education_Switch1
    '10.0.3.0/24': [[('General_Education', 'General_Education_Switch1', 'General_Education_Switch1')], [('General_Education_Switch1', 'General_Education', 'General_Education_Switch1')]],
    # Arts: Arts_Switch1, Arts_Switch2
    '10.0.4.0/24': [[('Arts_Switch1', 'Education_Switch1', 'Arts_Switch1'), 
                    ('Arts_Switch1', 'Business_Administration_Switch1', 'Arts_Switch1'),
                    ('Arts_Switch2', 'Central_Switch3', 'Arts_Switch2')],
                    [('Education_Switch1', 'Arts_Switch1', 'Arts_Switch1'),  
                    ('Business_Administration_Switch1', 'Arts_Switch1', 'Arts_Switch1'),  
                    ('Central_Switch3', 'Arts_Switch2', 'Arts_Switch2')]],
    # Arts firewall: Arts_Switch1
    '10.0.4.0/32': [[('Arts firewall', 'Arts_Switch1', 'Arts_Switch1')], [('Arts_Switch1', 'Arts firewall', 'Arts_Switch1')]],
    # Arts lab: Arts_Switch2
    '10.0.4.32/27': [[('Arts lab', 'Arts_Switch2', 'Arts_Switch2')], [('Arts_Switch2', 'Arts lab', 'Arts_Switch2')]],
    '10.0.4.64/26': [[('Arts lab', 'Arts_Switch2', 'Arts_Switch2')], [('Arts_Switch2', 'Arts lab', 'Arts_Switch2')]],
    # Arts office: Arts_Switch3
    '10.0.4.128/26': [[('Arts office', 'Arts_Switch3', 'Arts_Switch3')], [('Arts_Switch3', 'Arts office', 'Arts_Switch3')]],
    # Arts classroom: Arts_Switch4
    '10.0.4.192/26': [[('Arts classroom', 'Arts_Switch4', 'Arts_Switch4')], [('Arts_Switch4', 'Arts classroom', 'Arts_Switch4')]],
    # Arts exam area: omitted since all the prefixes have occurred
    # TODO: continue to finish the dict for other faculties and graduate school like arts by referring to entity_to_prefix_dict and snmt
        # Business_Administration: Business_Administration_Switch1, Business_Administration_Switch2
        '10.0.5.0/24': [
            [('Business_Administration_Switch1', 'Law_Switch1', 'Business_Administration_Switch1'),
            ('Business_Administration_Switch1', 'Arts_Switch1', 'Business_Administration_Switch1'),
            ('Business_Administration_Switch2', 'Central_Switch3', 'Business_Administration_Switch2')],
            [('Law_Switch1', 'Business_Administration_Switch1', 'Business_Administration_Switch1'),
            ('Arts_Switch1', 'Business_Administration_Switch1', 'Business_Administration_Switch1'),
            ('Central_Switch3', 'Business_Administration_Switch2', 'Business_Administration_Switch2')],
        ],
        # Business_Administration firewall: Business_Administration_Switch1
        '10.0.5.0/32': [
            [('Business_Administration firewall', 'Business_Administration_Switch1', 'Business_Administration_Switch1')],
            [('Business_Administration_Switch1', 'Business_Administration firewall', 'Business_Administration_Switch1')]
        ],
        # Business_Administration lab: Business_Administration_Switch2
        '10.0.5.64/26': [
            [('Business_Administration lab', 'Business_Administration_Switch2', 'Business_Administration_Switch2')],
            [('Business_Administration_Switch2', 'Business_Administration lab', 'Business_Administration_Switch2')]
        ],
        # Business_Administration office: Business_Administration_Switch3
        '10.0.5.128/26': [
            [('Business_Administration office', 'Business_Administration_Switch3', 'Business_Administration_Switch3')],
            [('Business_Administration_Switch3', 'Business_Administration office', 'Business_Administration_Switch3')]
        ],
        # Business_Administration classroom: Business_Administration_Switch4
        '10.0.5.192/26': [
            [('Business_Administration classroom', 'Business_Administration_Switch4', 'Business_Administration_Switch4')],
            [('Business_Administration_Switch4', 'Business_Administration classroom', 'Business_Administration_Switch4')]
        ],
        # Education: Education_Switch1
        '10.0.6.0/24': [
            [('Education_Switch1', 'Engineering_Switch1', 'Education_Switch1'),
            ('Education_Switch1', 'Arts_Switch1', 'Education_Switch1'),
            ('Education_Switch1', 'Central_Switch1', 'Education_Switch1')],
            [('Engineering_Switch1', 'Education_Switch1', 'Education_Switch1'),
            ('Central_Switch1', 'Education_Switch1', 'Education_Switch1'),
            ('Arts_Switch1', 'Education_Switch1', 'Education_Switch1')]
        ],
        # Education firewall: Education_Switch1
        '10.0.6.0/32': [
            [('Education firewall', 'Education_Switch1', 'Education_Switch1')],
            [('Education_Switch1', 'Education firewall', 'Education_Switch1')]
        ],
        # Education lab: Education_Switch2
        '10.0.6.64/26': [
            [('Education lab', 'Education_Switch2', 'Education_Switch2')],
            [('Education_Switch2', 'Education lab', 'Education_Switch2')]
        ],
        # Education office: Education_Switch3
        '10.0.6.128/26': [
            [('Education office', 'Education_Switch3', 'Education_Switch3')],
            [('Education_Switch3', 'Education office', 'Education_Switch3')]
        ],
        # Education classroom: Education_Switch4
        '10.0.6.192/26': [
            [('Education classroom', 'Education_Switch4', 'Education_Switch4')],
            [('Education_Switch4', 'Education classroom', 'Education_Switch4')]
        ],
        # Law: Law_Switch1
        '10.0.7.0/24': [
            [('Law_Switch1', 'Engineering_Switch1', 'Law_Switch1'),
            ('Law_Switch1', 'Central_Switch1', 'Education_Switch1'),
            ('Law_Switch1', 'Business_Administration_Switch1', 'Education_Switch1')],
            [('Engineering_Switch1', 'Law_Switch1', 'Law_Switch1'),
            ('Central_Switch1', 'Law_Switch1', 'Education_Switch1'),
            ('Business_Administration_Switch1', 'Law_Switch1', 'Education_Switch1')]
        ],
        # Law firewall: Law_Switch1
        '10.0.7.0/32': [
            [('Law firewall', 'Law_Switch1', 'Law_Switch1')],
            [('Law_Switch1', 'Law firewall', 'Law_Switch1')]
        ],
        # Law lab: Law_Switch2
        '10.0.7.64/26': [
            [('Law lab', 'Law_Switch2', 'Law_Switch2')],
            [('Law_Switch2', 'Law lab', 'Law_Switch2')]
        ],
        # Law office: Law_Switch3
        '10.0.7.128/26': [
            [('Law office', 'Law_Switch3', 'Law_Switch3')],
            [('Law_Switch3', 'Law office', 'Law_Switch3')]
        ],
        # Law classroom: Law_Switch4
        '10.0.7.192/26': [
            [('Law classroom', 'Law_Switch4', 'Law_Switch4')],
            [('Law_Switch4', 'Law classroom', 'Law_Switch4')]
        ],
        # Engineering: Engineering_Switch1, Engineering_Switch2
        '10.0.8.0/24': [
            [('Engineering_Switch1', 'Science_Switch1', 'Engineering_Switch1'),
            ('Engineering_Switch1', 'Library_Switch1', 'Engineering_Switch1'),
            ('Engineering_Switch1', 'Education_Switch1', 'Engineering_Switch1'),
            ('Engineering_Switch1', 'Law_Switch1', 'Engineering_Switch1'),
            ('Engineering_Switch2', 'Central_Switch2', 'Engineering_Switch2')],
            [('Science_Switch1', 'Engineering_Switch1', 'Engineering_Switch1'),
            ('Library_Switch1', 'Engineering_Switch1', 'Engineering_Switch1'),
            ('Education_Switch1', 'Engineering_Switch1', 'Engineering_Switch1'),
            ('Law_Switch1', 'Engineering_Switch1', 'Engineering_Switch1'),
            ('Central_Switch2', 'Engineering_Switch2', 'Engineering_Switch2')]
        ],
        # Engineering firewall: Engineering_Switch1
        '10.0.8.0/32': [
            [('Engineering firewall', 'Engineering_Switch1', 'Engineering_Switch1')],
            [('Engineering_Switch1', 'Engineering firewall', 'Engineering_Switch1')]
        ],
        # Engineering lab: Engineering_Switch2
        '10.0.8.32/27': [
            [('Engineering lab', 'Engineering_Switch2', 'Engineering_Switch2')],
            [('Engineering_Switch2', 'Engineering lab', 'Engineering_Switch2')]
        ],
        '10.0.8.64/26': [
            [('Engineering lab', 'Engineering_Switch2', 'Engineering_Switch2')],
            [('Engineering_Switch2', 'Engineering lab', 'Engineering_Switch2')]
        ],
        # Engineering office: Engineering_Switch3
        '10.0.8.128/26': [
            [('Engineering office', 'Engineering_Switch3', 'Engineering_Switch3')],
            [('Engineering_Switch3', 'Engineering office', 'Engineering_Switch3')]
        ],
        # Engineering classroom: Engineering_Switch4
        '10.0.8.192/26': [
            [('Engineering classroom', 'Engineering_Switch4', 'Engineering_Switch4')],
            [('Engineering_Switch4', 'Engineering classroom', 'Engineering_Switch4')]
        ],
        # Engineering exam area: omitted
        # Science: Science_Switch1
        '10.0.9.0/24': [
            [('Science_Switch1', 'Engineering_Switch1', 'Science_Switch1'),
            ('Science_Switch1', 'Library_Switch1', 'Science_Switch1'),
            ('Science_Switch1', 'Central_Switch1', 'Science_Switch1'),
            ('Science_Switch1', 'Graduate_School_Switch1', 'Science_Switch1')],
            [('Engineering_Switch1', 'Science_Switch1', 'Science_Switch1'),
            ('Library_Switch1', 'Science_Switch1', 'Science_Switch1'),
            ('Central_Switch1', 'Science_Switch1', 'Science_Switch1'),
            ('Graduate_School_Switch1', 'Science_Switch1', 'Science_Switch1')]
        ],
        # Science firewall: Science_Switch1
        '10.0.9.0/32': [
            [('Science firewall', 'Science_Switch1', 'Science_Switch1')],
            [('Science_Switch1', 'Science firewall', 'Science_Switch1')]
        ],
        # Science lab: Science_Switch2
        '10.0.9.64/26': [
            [('Science lab', 'Science_Switch2', 'Science_Switch2')],
            [('Science_Switch2', 'Science lab', 'Science_Switch2')]
        ],
        # Science office: Science_Switch3
        '10.0.9.128/26': [
            [('Science office', 'Science_Switch3', 'Science_Switch3')],
            [('Science_Switch3', 'Science office', 'Science_Switch3')]
        ],
        # Science classroom: Science_Switch4
        '10.0.9.192/26': [
            [('Science classroom', 'Science_Switch4', 'Science_Switch4')],
            [('Science_Switch4', 'Science classroom', 'Science_Switch4')]
        ],
        # Social_Science: Social_Science_Switch1, Social_Science_Switch2
        '10.0.10.0/24': [
            [('Social_Science_Switch1', 'Graduate_School_Switch1', 'Social_Science_Switch1'),
            ('Social_Science_Switch1', 'Medicine_Switch1', 'Social_Science_Switch1'),
            ('Social_Science_Switch2', 'Central_Switch2', 'Social_Science_Switch2')],
            [('Graduate_School_Switch1', 'Social_Science_Switch1', 'Social_Science_Switch1'),
            ('Medicine_Switch1', 'Social_Science_Switch1', 'Social_Science_Switch1'),
            ('Central_Switch2', 'Social_Science_Switch2', 'Social_Science_Switch2')]
        ],
        # Social_Science firewall: Social_Science_Switch1
        '10.0.10.0/32': [
            [('Social_Science firewall', 'Social_Science_Switch1', 'Social_Science_Switch1')],
            [('Social_Science_Switch1', 'Social_Science firewall', 'Social_Science_Switch1')]
        ],
        # Social_Science lab: Social_Science_Switch2
        '10.0.10.64/26': [
            [('Social_Science lab', 'Social_Science_Switch2', 'Social_Science_Switch2')],
            [('Social_Science_Switch2', 'Social_Science lab', 'Social_Science_Switch2')]
        ],
        # Social_Science office: Social_Science_Switch3
        '10.0.10.128/26': [
            [('Social_Science office', 'Social_Science_Switch3', 'Social_Science_Switch3')],
            [('Social_Science_Switch3', 'Social_Science office', 'Social_Science_Switch3')]
        ],
        # Social_Science classroom: Social_Science_Switch4
        '10.0.10.192/26': [
            [('Social_Science classroom', 'Social_Science_Switch4', 'Social_Science_Switch4')],
            [('Social_Science_Switch4', 'Social_Science classroom', 'Social_Science_Switch4')]
        ],
        # Medicine: Medicine_Switch1, Medicine_Switch2
        '10.0.11.0/24': [
            [('Medicine_Switch1', 'Social_Science_Switch1', 'Medicine_Switch1'),
            ('Medicine_Switch1', 'General_Education_Switch1', 'Medicine_Switch1'),
            ('Medicine_Switch1', 'Library_Switch1', 'Medicine_Switch1'),
            ('Medicine_Switch1', 'Graduate_School_Switch1', 'Medicine_Switch1'),
            ('Medicine_Switch2', 'Central_Switch2', 'Medicine_Switch2')],
            [('Social_Science_Switch1', 'Medicine_Switch1', 'Medicine_Switch1'),
            ('General_Education_Switch1', 'Medicine_Switch1', 'Medicine_Switch1'),
            ('Library_Switch1', 'Medicine_Switch1', 'Medicine_Switch1'),
            ('Graduate_School_Switch1', 'Medicine_Switch1', 'Medicine_Switch1'),
            ('Central_Switch2', 'Medicine_Switch2', 'Medicine_Switch2')]
        ],
        # Medicine firewall: Medicine_Switch1
        '10.0.11.0/32': [
            [('Medicine firewall', 'Medicine_Switch1', 'Medicine_Switch1')],
            [('Medicine_Switch1', 'Medicine firewall', 'Medicine_Switch1')]
        ],
        # Medicine lab: Medicine_Switch2
        '10.0.11.64/26': [
            [('Medicine lab', 'Medicine_Switch2', 'Medicine_Switch2')],
            [('Medicine_Switch2', 'Medicine lab', 'Medicine_Switch2')]
        ],
        # Medicine office: Medicine_Switch3
        '10.0.11.128/26': [
            [('Medicine office', 'Medicine_Switch3', 'Medicine_Switch3')],
            [('Medicine_Switch3', 'Medicine office', 'Medicine_Switch3')]
        ],
        # Medicine classroom: Medicine_Switch4
        '10.0.11.192/26': [
            [('Medicine classroom', 'Medicine_Switch4', 'Medicine_Switch4')],
            [('Medicine_Switch4', 'Medicine classroom', 'Medicine_Switch4')]
        ],
        # Graduate_School: Graduate_School_Switch1, Graduate_School_Switch2
        '10.0.12.0/24': [
            [('Graduate_School_Switch1', 'General_Education_Switch1', 'Graduate_School_Switch1'),
            ('Graduate_School_Switch1', 'Science_Switch1', 'Graduate_School_Switch1'),
            ('Graduate_School_Switch1', 'Social_Science_Switch1', 'Graduate_School_Switch1'),
            ('Graduate_School_Switch1', 'Medicine_Switch1', 'Graduate_School_Switch1'),
            ('Graduate_School_Switch2', 'Central_Switch3', 'Graduate_School_Switch2')],
            [('General_Education_Switch1', 'Graduate_School_Switch1', 'Graduate_School_Switch1'),
            ('Science_Switch1', 'Graduate_School_Switch1', 'Graduate_School_Switch1'),
            ('Social_Science_Switch1', 'Graduate_School_Switch1', 'Graduate_School_Switch1'),
            ('Medicine_Switch1', 'Graduate_School_Switch1', 'Graduate_School_Switch1'),
            ('Central_Switch3', 'Graduate_School_Switch2', 'Graduate_School_Switch2')]
        ],
        '10.0.12.0/32': [
            [('Graduate_School firewall', 'Graduate_School_Switch1', 'Graduate_School_Switch1')],
            [('Graduate_School_Switch1', 'Graduate_School firewall', 'Graduate_School_Switch1')]
        ],
        '10.0.12.64/26': [
            [('Graduate_School lab', 'Graduate_School_Switch2', 'Graduate_School_Switch2')],
            [('Graduate_School_Switch2', 'Graduate_School lab', 'Graduate_School_Switch2')]
        ],
        '10.0.12.128/26': [
            [('Graduate_School office', 'Graduate_School_Switch3', 'Graduate_School_Switch3')],
            [('Graduate_School_Switch3', 'Graduate_School office', 'Graduate_School_Switch3')]
        ],
        '10.0.12.192/26': [
            [('Graduate_School classroom', 'Graduate_School_Switch4', 'Graduate_School_Switch4')],
            [('Graduate_School_Switch4', 'Graduate_School classroom', 'Graduate_School_Switch4')]
        ],
    # Ingress A: Central_Switch1, Library_Switch1
    '69.63.1.0/24': [
            [('Ingress A', 'Central_Switch1', 'Central_Switch1'),  
            ('Ingress A', 'Central_Switch1', 'Central_Switch1')],
            [] 
        ],
    # TODO: continue to finish the dict for other ingress and egress traffic by referring to entity_to_prefix_dict and snmt
        # Ingress B: Central_Switch2
        '69.63.2.0/24': [
            [('Ingress B', 'Central_Switch2', 'Central_Switch2')],
            []
        ],
        # Ingress C: Library_Switch1
        '69.63.3.0/24': [
            [('Ingress C', 'Library_Switch1', 'Library_Switch1')],
            []
        ],
        # Ingress D: Engineering_Switch1
        '69.63.4.0/24': [
            [('Ingress D', 'Engineering_Switch1', 'Engineering_Switch1')],
            []
        ],
        # Ingress E: Science_Switch1
        '69.63.5.0/24': [
            [('Ingress E', 'Science_Switch1', 'Science_Switch1')],
            []
        ],
        # Egress F: Central_Switch3, Library_Switch1
        '69.63.6.0/24': [
            [],
            [('Central_Switch3', 'Egress F', 'Central_Switch3'),
            ('Library_Switch1', 'Egress F', 'Library_Switch1')]
        ],
        '69.63.7.0/24': [
            [],
            [('Central_Switch3', 'Egress F', 'Central_Switch3'),
            ('Library_Switch1', 'Egress F', 'Library_Switch1')]
        ],
        # Egress G: Law_Switch1
        '69.63.8.0/24': [
            [],
            [('Law_Switch1', 'Egress G', 'Law_Switch1')]
        ],
        # Egress H: Education_Switch1
        '69.63.9.0/24': [
            [],
            [('Education_Switch1', 'Egress H', 'Education_Switch1')]
        ],
        # Egress I: Graduate_School_Switch1
        '69.63.10.0/24': [
            [],
            [('Graduate_School_Switch1', 'Egress I', 'Graduate_School_Switch1')]
        ],
        # Egress J: Medicine_Switch1
        '69.63.11.0/24': [
            [],
            [('Medicine_Switch1', 'Egress J', 'Medicine_Switch1')]
        ],
        '69.63.12.0/24': [
            [],
            [('Medicine_Switch1', 'Egress J', 'Medicine_Switch1')]
        ]
}

json_store(entity_to_prefix_dict,'../json/entity_prefixes.json')
json_store(prefix_to_interface_dict,'../json/prefix_gateways.json')