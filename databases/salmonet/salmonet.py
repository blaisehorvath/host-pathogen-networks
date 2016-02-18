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
nodes = {}
edges = {}


# parsing the file
with open(args.source_file) as source_file:

    # read the first line

    source_file.readline()

    for line in source_file:

        line_arr = line.split('\t')
        line_length = len(line_arr)

        source_uniprot, target_uniprot, type, source, mechanism = line_arr

        # continue the loop if the edge is already in

        edge_name = "%s@%s" % (source_uniprot, target_uniprot)

        if edge_name in edges:
            continue

        if mechanism == "ppi":
            reverse_edge_name = "%s@%s" % (target_uniprot, source_uniprot)
            if reverse_edge_name in edges:
                continue


        if source_uniprot not in nodes:

            source = {
                'name' : source_uniprot,
                'alt_accession' : "",
                'tax_id' : "taxid:99284",
                'pathways' : "",
                'aliases' : "",
                'topology' : ""
            }

            nodes[source_uniprot] = source

            nodes[source_uniprot]["id"] = db_api.insert_node(source)

        if target_uniprot not in nodes:

            target = {
                'name' : target_uniprot,
                'alt_accession' : "",
                'tax_id' : "taxid:99284",
                'pathways' : "",
                'aliases' : "",
                'topology' : ""
            }

            nodes[target_uniprot] = target

            nodes[target_uniprot]["id"] = db_api.insert_node(target)

        edge_dict = {
            'interaction_detection_method': "",
            'first_author': "",
            'publication_ids': "",
            'interaction_types': mechanism,
            'source_db': "salmonet",
            'interaction_identifiers': "",
            'confidence_scores': "",
            'layer': "0"
        }

        db_api.insert_edge(nodes[source_uniprot], nodes[target_uniprot], edge_dict)

print("Saving db file to %s" % (args.outfile))
db_api.save_db_to_file(args.outfile)