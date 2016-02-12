SELECT source.id, source.name, source.alt_accession, source.tax_id, source.pathways, source.aliases, source.topology
FROM edge
  JOIN node as source ON edge.interactor_a_node_id = source.id
  JOIN node as target ON edge.interactor_b_node_id = target.id
WHERE (source.pathways LIKE "%Rho%") OR (target.pathways LIKE "%Rho%")

UNION

SELECT target.id, target.name, target.alt_accession, target.tax_id, target.pathways, target.aliases, target.topology
FROM edge
  JOIN node as source ON edge.interactor_a_node_id = source.id
  JOIN node as target ON edge.interactor_b_node_id = target.id
WHERE (source.pathways LIKE "%Rho%") OR (target.pathways LIKE "%Rho%")