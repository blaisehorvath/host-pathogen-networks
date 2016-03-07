"""
This script parses PsimiSQL files and maps the uniprot ids of nodes to swissprot id if possible
"""

#TODO: inform user (which file is being parsed)? what %? if too slow index the dictionary db!

__author__ = 'blaise'

import sqlite3
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Convert node ids to swissprot')
parser.add_argument('--source-files', required=True, metavar="SourceFiles", type=str, nargs='+',
                    help="The location of source files separated by spaces.")
parser.add_argument('--outdir', required=True, metavar="OutputFile", type=str,
                    help="The name and optionally location where the data should be saved.")
parser.add_argument('--psimisql', required=True, metavar="PsimiSQLLocation", type=str,
                    help="The location of the PsimiSQL class")
parser.add_argument('--dictionary', required=True, metavar="dict", type=str,
                    help="Location of the dictionary db file")

args = parser.parse_args()

sys.path.append(args.psimisql)
from sqlite_db_api import PsimiSQL

dictionary_db = sqlite3.connect(args.dictionary)
dictionary_db.text_factory = str
dictionary_db_cursor = dictionary_db.cursor()


def get_primary(uniprot_id):
    dictionary_db_cursor.execute("SELECT accession, is_primary, primary_id FROM uniprot WHERE accession = ?", (uniprot_id,))

    result = dictionary_db_cursor.fetchone()

    accession, is_primary, primary_id = result

    if is_primary:
        return uniprot_id
    else:
        dictionary_db_cursor.execute("SELECT accession FROM uniprot WHERE id = ?", (primary_id,))
        return dictionary_db_cursor.fetchone()[0]


def main():

    for db in args.source_files:

        # informing the user
        print("Parsing %s" % db)

        cursor = sqlite3.connect(db).cursor()

        mapped_nodes = {}
        nodemap = {}

        cursor.execute("SELECT * FROM node")
        result = cursor.fetchall()

        length = len(result)
        current = 1

        new_db = PsimiSQL()

        cursor.execute("SELECT count(*) FROM node")
        num_of_nodes = cursor.fetchone()[0]

        # mapping nodes

        print("Mapping nodes")

        for line in result:

            # informing user
            if (current % 50 == 0):
                print("Mapping nodes %d/%d" % (current, length))

            current += 1

            row_id, name, alt_accession, tax_id, pathways, aliases, topology = line

            old_uniprot = name

            new_uniprot = "uniprot:"+get_primary(old_uniprot.split(':')[1])

            # storing the new uniprot id for every old id
            nodemap[old_uniprot] = new_uniprot

            mapped_node = {
                'name': new_uniprot,
                'alt_accession': alt_accession,
                'tax_id': tax_id,
                'pathways': pathways,
                'aliases': aliases,
                'topology': topology
            }

            mapped_node['id'] = new_db.insert_node(mapped_node)

            mapped_nodes[new_uniprot] = mapped_node

        if len(nodemap) != num_of_nodes:
            print "Gebasz"

        # mapping edges

        cursor.execute("SELECT * FROM edge")
        result = cursor.fetchall()

        print("Mapping edges")
        length = len(result)
        current = 1
        shit_counter = 0

        for row in result:

            if (current % 10 == 0):
               print("Parsing edge %d/%d" % (current, length))
            current += 1

            old_source_uniprot = row[3]
            old_target_uniprot = row[4]


            edge_dict = {
                'interaction_detection_method': row[5],
                'first_author': row[6],
                'publication_ids': row[7],
                'interaction_types': row[8],
                'source_db': row[9],
                'interaction_identifiers': row[10],
                'confidence_scores': row[11],
                'layer': "0"
            }

            if (old_source_uniprot not in mapped_nodes or old_target_uniprot not in mapped_nodes):
                shit_counter +=1
            else:
                new_db.insert_edge(mapped_nodes[old_source_uniprot], mapped_nodes[old_target_uniprot], edge_dict)

        # saving the mapped db and informing user

        db_name = os.path.split(db)[1]

        print("Saving db to %s " % (args.outdir+"/mapped"+db_name))
        print("SHITCOUNTER %d" % shit_counter )

        new_db.save_db_to_file(args.outdir+"/mapped"+db_name)


if __name__ == '__main__':
    main()