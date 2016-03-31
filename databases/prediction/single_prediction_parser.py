__author__ = 'blaise'

# parsing arguments
import argparse
import sqlite3
import sys


parser = argparse.ArgumentParser(description='Convert edgelists to Mitab SQLite')
parser.add_argument('--source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the source file for nodes")
parser.add_argument('--outfile', required=True, metavar="OutputFile", type=str,
                    help="The name and optionally location where the data should be saved.")
parser.add_argument('--psimisql', required=True, metavar="PsimiSQLLocation", type=str,
                    help="The location of the PsimiSQL class")
parser.add_argument('--map-file', required=True, metavar="MapFile", type=str,
                    help="The location of the file that maps salmonella proteins to uniprot")
parser.add_argument('--dictionary-db', required=True, metavar="Dictionary-db", type=str)
parser.add_argument('--prediction-name', required=True, metavar="PredName", type=str)

args = parser.parse_args()
dictionary_api = sqlite3.connect(args.dictionary_db)
dictionary_cursor = dictionary_api.cursor()


sys.path.append(args.psimisql)
from sqlite_db_api import PsimiSQL

# initiating the memory db
db_api = PsimiSQL()

# the unique nodes will be held here
salmonella_nodes= {}
human_nodes = {}
edges = []

# parsing the map file
with open(args.map_file) as mapFile:

    # skipping header
    mapFile.readline()

    for line in mapFile:
        uniprot, salmonella = line.strip().split("\t")

        salmonella_nodes[salmonella] = salmonella_node ={
            'name': "uniprot:" + uniprot,
            'alt_accession': "gene symbol:" + salmonella,
            'tax_id': "taxid:99284",
            'pathways': "",
            'aliases': "",
            'topology': ""
        }

        salmonella_nodes[salmonella]["id"] = db_api.insert_node(salmonella_node)

with open(args.source_file) as source_file:

    # skipping the header
    source_file.readline()

    for line in source_file:
        salm_node_acc, human_node_acc = line.strip().split(';')

        dictionary_cursor.execute("""
              SELECT DISTINCT uniprot.accession
              FROM uniprot
              JOIN foreign_ids on uniprot.id == foreign_ids.uniprot_id
              WHERE foreign_ids.accession = ? AND uniprot.is_swissprot = 1
            """, (human_node_acc,))

        human_uniprot = dictionary_cursor.fetchone()

        if human_node_acc not in human_nodes:

            human_nodes[human_node_acc] = human_node = {
                'name': "uniprot:" + human_uniprot[0],
                'alt_accession': "gene symbol:" + human_node_acc,
                'tax_id': "taxid:9606",
                'pathways': "",
                'aliases': "",
                'topology': ""
            }

            human_nodes[human_node_acc]['id'] = db_api.insert_node(human_node)

        edges.append([salm_node_acc, human_node_acc])

for edge in edges:

    edge_dict = {
        'interaction_detection_method': "",
        'first_author': "",
        'publication_ids': "",
        'interaction_types': "",
        'source_db': args.prediction_name,
        'interaction_identifiers': "",
        'confidence_scores': "",
        'layer': "0"
    }

    if edge[0] in salmonella_nodes:

        db_api.insert_edge(salmonella_nodes[edge[0]], human_nodes[edge[1]], edge_dict)

db_api.save_db_to_file(args.outfile)

print("The database was saved to %s" % (args.outfile + ".db"))