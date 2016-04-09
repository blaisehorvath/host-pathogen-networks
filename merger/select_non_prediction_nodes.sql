SELECT arn_nodes.name, arn_nodes.tax_id, node.pathways FROM arn_nodes
JOIN node ON arn_nodes.name = node.name

UNION

SELECT slk_nodes.name, slk_nodes.tax_id, node.pathways FROM slk_nodes
JOIN node ON slk_nodes.name = node.name

UNION

SELECT salmonet_nodes.name, salmonet_nodes.tax_id, node.pathways FROM salmonet_nodes
JOIN node ON salmonet_nodes.name = node.name