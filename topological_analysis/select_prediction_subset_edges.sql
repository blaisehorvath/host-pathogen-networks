SELECT source, target, source_db
FROM non_prediction_edges
WHERE source_db LIKE "%skhirshagar%" OR source_db = "arn" OR source_db = "salmonet"