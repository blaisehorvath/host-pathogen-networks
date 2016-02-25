# setting up imports
import sqlite3
import sys
import os
import re

# adding the psimi_to_sql module to sys
sys.path.append(sys.argv[5])
from sqlite_db_api import PsimiSQL

# declaring, and assigning "constants"
DICTIONARY_DB_LOCATION = sys.argv[1]
SOURCE_DB_TYPE = sys.argv[2]
SOURCE_DB_LOCATION = sys.argv[3]
DESTINATION_DB_LOCATION = sys.argv[4]

DICTIONARY_DB = sqlite3.connect(DICTIONARY_DB_LOCATION)
DICTIONARY_DB_CURSOR = DICTIONARY_DB.cursor()


def get_swiss_arr(arr):
    """
    This function extracts the SQL rows from a SQL table (that was received via the SQLite3 lib)
    :param arr: A list with the Psi-Mi-SQLite syntax that was fetched from a SQLite database
    :return: A Psi-Mi SQL formatted list that only contains swissprot nodes.
    """
    # creating an empty list, that will (hopefully) contain the results
    swissprots = []

    # looping through the array, and collecting swissprot nodes
    for line in arr:
        is_swissprot = line[2]
        if is_swissprot == 1:
            swissprots.append(line)

    # returning the swissprot nodes
    return swissprots


def get_aliases_string(trembl_list):
    """
    This function extracts the alias accessions from a list.
    :param trembl_list: A list that was the result of a SQLite query
    :type trembl_list: list
    :return:
    """
    aliases_list = []

    for row in trembl_list:
        psimi_trembl = "trembl:" + row[1]
        aliases_list.append(psimi_trembl)

    return "|".join(aliases_list)


def get_trembl_arr(arr):
    """
    This function extracts the SQL rows from a SQL table (that was received via the SQLite3 lib)
    :param arr: A list with the Psi-Mi-SQLite syntax that was fetched from a SQLite database
    :return: A Psi-Mi SQL formatted list that only contains trembl nodes.
    """
    # creating an empty list, that will (hopefully) contain the results
    trembls = []

    # looping through the array, and collecting trembl nodes
    for line in arr:
        is_swissprot = line[2]
        if is_swissprot == 0:
            trembls.append(line)

    # returning the trembl nodes
    return trembls

def add_node(old_node_dict, old_to_new_node_ids_dict, new_accession, new_db_api, aliases):
    """
    This function adds a node to the new SQLite db and appends it's new last_row_id to a dictionary
    :param old_node_dict: The node dict if the old node
    :type old_node_dict dict
    :param old_to_new_node_ids_dict: A dictionary that contains an old node id as key and new node ids as value
    :type old_to_new_node_ids_dict dict
    :param new_db_api: A PsimiSQL object
    :type PsimiSQL
    :param aliases: A string that contains the node's aliases separated by pipe
    :type aliases str
    :return:
    """

    # getting the old node id, and the old node's properties
    old_node_id = old_node_dict["id"]
    old_node_alt_accession = old_node_dict["alt_accession"]
    old_node_name = old_node_dict["name"]
    tax_id = old_node_dict["tax_id"]
    pathways = old_node_dict["pathways"]

    if aliases:
        aliases += "|" + old_node_dict["name"]
    else:
        aliases = old_node_dict["name"]

    if old_node_dict["aliases"]:
        aliases += "|" + old_node_dict["aliases"]

    new_node_dict = {
        "name" : new_accession,
        "alt_accession" : old_node_alt_accession,
        "tax_id" : tax_id,
        "pathways" : pathways,
        "aliases" : aliases,
        "topology": ""
    }

    # inserting the node to the PSI-MI SQLite
    new_db_api.insert_unique_node(new_node_dict)
    new_node_dict['id'] = new_db_api.last_row_id
    # getting the new last row id of the inserted node
    new_node_id = new_node_dict['id']

    # if the node maps to more than one swissprot uniprot id it will be inserted for every swissprot id and
    # this function will be called for every insertion
    if not old_to_new_node_ids_dict.has_key(old_node_id):
        old_to_new_node_ids_dict[old_node_id] = [new_node_id]
    else:
        old_to_new_node_ids_dict[old_node_id].append(new_node_id)

def add_uniprot(old_node_dict, old_to_new_node_ids_dict, new_db_api):
    """
    This function adds a node to the new SQLite db and appends it's new last_row_id to a dictionary
    :param old_node_dict: The node dict if the old node
    :type old_node_dict dict
    :param old_to_new_node_ids_dict: A dictionary that contains an old node id as key and new node ids as value
    :type old_to_new_node_ids_dict dict
    :param new_db_api: A PsimiSQL object
    :type PsimiSQL
    :param aliases: A string that contains the node's aliases separated by pipe
    :type aliases str
    :return:
    """

    # getting the old node id, and the old node's properties
    old_node_id = old_node_dict["id"]
    old_node_alt_accession = old_node_dict["alt_accession"]
    old_node_name = old_node_dict["name"]
    old_aliases = old_node_dict['aliases']
    tax_id = old_node_dict["tax_id"]
    pathways = old_node_dict["pathways"]

    new_node_dict = {
        "name" : old_node_name,
        "alt_accession" : old_node_alt_accession,
        "tax_id" : tax_id,
        "pathways" : pathways,
        "aliases" : old_aliases,
        "topology" : ""
    }

    # inserting the node to the PSI-MI SQLite
    new_db_api.insert_unique_node(new_node_dict)
    new_node_dict['id'] = new_db_api.last_row_id

    # getting the new last row id of the inserted node
    new_node_id = new_node_dict['id']

    # if the node maps to more than one swissprot uniprot id it will be inserted for every swissprot id and
    # this function will be called for every insertion
    if not old_to_new_node_ids_dict.has_key(old_node_id):
        old_to_new_node_ids_dict[old_node_id] = [new_node_id]
    else:
        old_to_new_node_ids_dict[old_node_id].append(new_node_id)

def main():

    # opening the old_db for mapping
    old_db = PsimiSQL()
    old_db.import_from_db_file(SOURCE_DB_LOCATION)

    # making the script more verbose
    counter = 0
    old_db.cursor.execute("SELECT count(*) FROM node")
    number_of_nodes = old_db.cursor.fetchone()[0]

    # iterating through the old_db's nodes
    old_db.cursor.execute("SELECT * FROM node")

    # mapping old node_ids to new node old ids
    old_node_ids_dict = {}

    # initiating an empty db the maped nodes are put
    new_db = PsimiSQL()

    # declaring a counter to count the nodes that does not match
    no_match_counter = 0
    invalid_node_counter = 0

    # looping through the old_db_s nodes
    while True:
        row = old_db.cursor.fetchone()

        # communicating with user
        sys.stdout.write("Querying %d. node from dictionary out of %d\r" % (counter, number_of_nodes))
        counter += 1

        # until the last row
        if row == None:
            break
        else:
            row_id, mitab_name, alt_accession, mitab_tax_id, pathways, aliases, topology = row

            tax_id = str(mitab_tax_id.split(':')[1])
            name = str(mitab_name.split(':')[1])

            old_node_dict = {
                "id" : row_id,
                "name" : mitab_name,
                "alt_accession" : alt_accession,
                "tax_id" : mitab_tax_id,
                "pathways" : pathways,
                "aliases" : aliases,
                "topology" : topology
            }

            # if the fetched node is already mapped, just it's copy will be inserted
            #  if "uniprot" in mitab_name:
            #      add_uniprot(old_node_dict,old_node_ids_dict,new_db)
            #  else:

            query = """
                SELECT DISTINCT foreign_ids.accession, uniprot.accession, uniprot.is_swissprot, uniprot.is_primary
                FROM foreign_ids JOIN uniprot ON foreign_ids.uniprot_id = uniprot.id
                WHERE foreign_ids.accession = ? AND uniprot.tax_id = ? AND uniprot.is_primary = 1
            """

            tup = (name, tax_id)

            DICTIONARY_DB_CURSOR.execute(query, tup)
            DICTIONARY_DB.commit()

            result = DICTIONARY_DB_CURSOR.fetchall()

            if len(result) == 0:
                # if there is no match in the map for the current node
                no_match_counter+=1
            else:
                # get a list with only the swissprot nodes from the result of the SQL query
                swiss_nodes = get_swiss_arr(result)

                # getting the trembl nodes arr
                trembl_nodes = get_trembl_arr(result)

                # getting the new aliases
                aliases = get_aliases_string(trembl_nodes)

                # best case scenario it's a 1 -> 1 map
                if len(swiss_nodes) == 1:
                    swiss_accession  = "uniprot:"+swiss_nodes[0][1]
                    add_node(old_node_dict, old_node_ids_dict, swiss_accession, new_db, aliases)
                # if it maps to more than one swissprot accession, all swissprot nodes will be added
                elif len(swiss_nodes)  > 1:
                    for node in swiss_nodes:
                        swiss_accession = "uniprot:"+node[1]
                        add_node(old_node_dict, old_node_ids_dict, swiss_accession, new_db, aliases)
                # adding trembl nodes if the old node does not match any swissprot accession
                else:
                    for node in trembl_nodes:
                        trembl_accession = "trembl:"+node[1]
                        add_node(old_node_dict, old_node_ids_dict, trembl_accession, new_db, aliases)

    print("Inserting to %s nodes done" % SOURCE_DB_TYPE)

    # setting up counters, to be able to give the user some information of the ongoing process
    old_db.cursor.execute("SELECT count(*) FROM edge")
    number_of_edges = old_db.cursor.fetchone()[0]
    edge_counter = 0


    query = "SELECT * from edge"
    old_db.cursor.execute(query)

    while True:
        # informing the user
        sys.stdout.write("Parsing edge # %d out of %d\r" % (edge_counter, number_of_edges))
        row = old_db.cursor.fetchone()

        if row == None:
            break
        else:
            edge_counter += 1

            # deconstructing the row (list)
            edge_id, old_interactor_a_node_id, old_interactor_b_node_id, interactor_a_node_name, interactor_b_node_name, interaction_detection_method , first_author, publication_ids, interaction_types, source_db, interaction_identifiers, confidence_scores, layer = row

            # since we get the old interactor id's from this query we can simply look up ther new id(s) in the old_node_ids dict
            # it both nodes mapped we add them as an edge to the new db
            if old_node_ids_dict.has_key(old_interactor_a_node_id) and old_node_ids_dict.has_key( old_interactor_b_node_id):

                # looping through every new 'A' node
                for new_node_id_a in old_node_ids_dict[old_interactor_a_node_id]:

                    new_node_a_dict = new_db.get_node_by_id(new_node_id_a)

                    # looping through every new 'B' node for every new 'A' node and inserting them as an edge
                    for new_node_id_b in old_node_ids_dict[old_interactor_b_node_id]:

                        new_node_b_dict = new_db.get_node_by_id(new_node_id_b)

                        # generating the new edge dict
                        new_edge_dict = {
                            'interactor_a_node_id' : new_node_id_a,
                            'interactor_b_node_id': new_node_id_b,
                            'interactor_a_node_name' : interactor_a_node_name,
                            'interactor_b_node_name': interactor_b_node_name,
                            'interaction_detection_method' : interaction_detection_method,
                            'first_author' : first_author,
                            'publication_ids' : publication_ids,
                            'source_db' : "source database:"+SOURCE_DB_TYPE,
                            'interaction_types' : interaction_types,
                            'interaction_identifiers' : interaction_identifiers,
                            'confidence_scores' : confidence_scores,
                            'layer' : layer
                        }

                        # inserting the new node
                        new_db.insert_edge(new_node_a_dict, new_node_b_dict, new_edge_dict)
            else:
                # countering the nodes that can't be inserted to the new db because one of their nodes haven't mapped
                invalid_node_counter += 1
    print("Inserting edges to %s.db finished!" % SOURCE_DB_TYPE)

    new_db.save_db_to_file(DESTINATION_DB_LOCATION)



if __name__ == '__main__':
    main()
