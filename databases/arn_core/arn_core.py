__author__ = 'blaise'

# parsing arguments
import argparse

parser = argparse.ArgumentParser(description='Convert downloaded RNA files to Mitab SQLite')
parser.add_argument('--source-file', required=True, metavar="SourceFile", type=str,
                    help="The location of the csv that was saved from arn")
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

# extracting nodes
nodes = {}
edges = {}

print("Parsing file")

with open(args.source_file) as arn_file:

    # skipping the first line
    arn_file.readline()

    for line in arn_file:

        # splitting up the line

        linearr = line.split(';')

        source_name = linearr[1]

        if source_name not in nodes:

            source = {
                'name' : "uniprot:"+source_name,
                'alt_accession' : "gene symbol:"+linearr[0],
                'tax_id' : "taxid:"+linearr[2],
                'pathways' : linearr[7],
                'aliases' : "",
                'topology' : linearr[4]
            }

            nodes[source_name] = source

            source_id = db_api.insert_node(source)

            nodes[source_name]["id"] = source_id


        target_name = linearr[9]

        if target_name not in nodes:

            target = {
                'name' : "uniprot:"+target_name,
                'alt_accession' : "gene symbol:"+linearr[8],
                'tax_id' : "taxid:"+linearr[10],
                'pathways' : linearr[15],
                'aliases' : "",
                'topology' : linearr[12]
            }

            nodes[target_name] = target

            target_id = db_api.insert_node(target)

            nodes[target_name]["id"] = target_id

        # crafting edge

        effect = linearr[19]
        is_directed = "directed" if "directed" in linearr[17] else "undirected"
        is_direct = "direct"  # all of them are direct so hardcoded

        interaction_types = "effect:%s|is_directed:%s|is_direct:%s" % (effect, is_directed, is_direct)

        publication_ids_l = linearr[20].split('|')
        publication_ids = "pubmed:"+"|pubmed:".join(publication_ids_l)

        edge_dict = {
            'interaction_detection_method': "",
            'first_author': "",
            'publication_ids': publication_ids,
            'interaction_types': interaction_types,
            'source_db': "arn",
            'interaction_identifiers': "",
            'confidence_scores': linearr[22],
            'layer': "0"
        }

        db_api.insert_edge(nodes[source_name], nodes[target_name], edge_dict)

print("Finished parsing file, saving db.")

db_api.save_db_to_file(args.outfile)

print("Database is saved to "+args.outfile)