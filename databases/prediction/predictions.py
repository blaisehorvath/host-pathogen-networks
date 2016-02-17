__author__ = 'blaise'

# parsing arguments
import argparse

parser = argparse.ArgumentParser(description='Convert downloaded RNA files to Mitab SQLite')
parser.add_argument('--source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the source file for nodes")
parser.add_argument('--outfile', required=True, metavar="OutputFile", type=str,
                    help="The name and optionally location where the data should be saved.")
parser.add_argument('--psimisql', required=True, metavar="PsimiSQLLocation", type=str,
                    help="The location of the PsimiSQL class")

args = parser.parse_args()

# imports
import sys

sys.path.append(args.psimisql)
from sqlite_db_api import PsimiSQL

# initiating the memory db
db_api = PsimiSQL()

# the unique nodes will be held here
nodes= {}

# parsing the file

with open(args.source_file) as source_file:

    # skipping the header line

    source_file.readline()

    for line in source_file:

        linearr = line.strip().split("\t")

        salmonella_uniprot, salmonella_gene_symbol, human_uniprot, human_gene_symbol = linearr

        if salmonella_uniprot not in nodes:

            salmonella_node = {
                'name' : salmonella_uniprot,
                'alt_accession' : salmonella_gene_symbol,
                'tax_id' : "taxid:99284",
                'pathways' : "",
                'aliases' : "",
                'topology' : ""
            }

            nodes[salmonella_uniprot] = salmonella_node

            nodes[salmonella_uniprot]["id"] = db_api.insert_node(salmonella_node)

        if human_uniprot not in nodes:

            human_node = {
                'name' : human_uniprot,
                'alt_accession' : human_gene_symbol,
                'tax_id' : "taxid:9606",
                'pathways' : "",
                'aliases' : "",
                'topology' : ""
            }

            nodes[human_uniprot] = human_node
            nodes[human_uniprot]["id"] = db_api.insert_node(human_node)

        edge_dict = {
            'interaction_detection_method': "",
            'first_author': "",
            'publication_ids': "",
            'interaction_types': "",
            'source_db': "salmonella_predictions",
            'interaction_identifiers': "",
            'confidence_scores': "",
            'layer': "0"
        }

        db_api.insert_edge(nodes[salmonella_uniprot], nodes[human_uniprot], edge_dict)

    # saving database

    db_api.save_db_to_file(args.outfile)

    print("The database was saved to %s" % (args.outfile))