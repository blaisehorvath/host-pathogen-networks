SELECT pathways, interactor_a_node_name, interactor_b_node_name 
FROM (
            SELECT interactor_a_node_name, interactor_b_node_name, node.pathways
            FROM edge
                JOIN arn_nodes ON edge.interactor_a_node_name = arn_nodes.name
                JOIN node ON edge.interactor_b_node_id = node.name
            
            UNION 
            
            SELECT interactor_a_node_name, interactor_b_node_name, node.pathways
            FROM edge
            JOIN arn_nodes ON edge.interactor_b_node_name = arn_nodes.name
                JOIN node ON edge.interactor_a_node_name = node.name
    )
WHERE pathways LIKE "%Rho%"