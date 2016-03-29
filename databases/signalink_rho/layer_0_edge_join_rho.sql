SELECT edge.id, edge.interactor_a_node_id, edge.interactor_b_node_id, edge.interactor_a_node_name, edge.interactor_b_node_name, replace(edge.interaction_detection_method, char(10),'') , edge.first_author, replace(edge.publication_ids, char(10),''), edge.interaction_types, edge.source_db, edge.interaction_identifiers, edge.confidence_scores, edge.layer
FROM edge
  JOIN node as source ON edge.interactor_a_node_id = source.id
  JOIN node as target ON edge.interactor_b_node_id = target.id
WHERE (source.pathways LIKE "%Rho%") AND (target.pathways LIKE "%Rho%")