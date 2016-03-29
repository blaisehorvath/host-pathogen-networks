__author__ = 'blaise'

# parsing arguments
import argparse

parser = argparse.ArgumentParser(description='Convert downloaded RNA files to Mitab SQLite')
parser.add_argument('--node-source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the source file for nodes")
parser.add_argument('--edge-source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the source file for edges")
parser.add_argument('--outfile', required=True, metavar="OutputFile", type=str,
                    help="The name and optionally location where the data should be saved.")
parser.add_argument('--db-name', required=True, metavar="DatabaseName", type=str,
                    help="The name of the source database")
parser.add_argument('--psimisql', required=True, metavar="PsimiSQLLocation", type=str,
                    help="The location of the PsimiSQL class")

args = parser.parse_args()

# imports
import sys

sys.path.append(args.psimisql)
from sqlite_db_api import PsimiSQL

# initiating the memory db
db_api = PsimiSQL()

# parsing nodes

# nodes will be stored temporarily in memory, because re-querying them is slower
nodes = {}

# looping through the node file
with open(args.node_source_file) as node_file:

    # informing the user
    print "Parsing nodes"
    sum_nodes = sum([1 for x in node_file])
    progress = 1
    node_file.seek(0)

    # skipping header
    node_file.readline()

    # looping through the file
    for line in node_file:

        # infroming the user
        progress += 1
        sys.stdout.write("Parsing node %d/%d\r" % (sum_nodes, progress))

        # parsing the line

        linearr = line.split("\t")

        # deconstructing the array generated from the line
        node_id, name, alt_accession, tax_id, pathways, aliases, topology = linearr

        node_dict = {
            'name' : name,
            'alt_accession' : alt_accession,
            'tax_id' : tax_id,
            'pathways' : pathways,
            'aliases' : aliases,
            'topology' : topology
        }

        node_dict['id'] = db_api.insert_node(node_dict)

        nodes[name] = node_dict

    print("Parsing nodes done.")

# parsing edges

with open(args.edge_source_file) as edge_file:

    # informing the user
    print "Parsing edges"
    sum_edges = sum([1 for line in edge_file])
    progress = 1
    edge_file.seek(0)

    # skipping the first line
    edge_file.readline()

    linearrshit = set()

    # looping through file
    for line in edge_file:

        # parsing edges
        progress += 1
        sys.stdout.write("Inserting edge to memory db %d/%d\r" % (progress, sum_edges))

        linearr = line.split('\t')

        source_name = linearr[3]
        target_name = linearr[4]

        edge_dict = {
            'interaction_detection_method': linearr[5],
            'first_author': linearr[6],
            'publication_ids': linearr[7],
            'interaction_types': linearr[8],
            'source_db': "SLK3_layer0", #TODO: change back to linearr[9]. if needed
            'interaction_identifiers': linearr[10],
            'confidence_scores': linearr[11],
            'layer': "0"
        }

        db_api.insert_edge(nodes[source_name], nodes[target_name], edge_dict)

    print("Inserting edges to db done, saving database...")

db_api.save_db_to_file(args.outfile)

print("Database is saved to: %s" % (args.outfile))