SELECT 
    edge.interactor_a_node_name as "source",
    edge.interactor_b_node_name as "target",
    edge.source_db
FROM edge
    JOIN non_prediction_nodes as source ON edge.interactor_a_node_name = source.name
    JOIN non_prediction_nodes as target ON edge.interactor_b_node_name = target.name