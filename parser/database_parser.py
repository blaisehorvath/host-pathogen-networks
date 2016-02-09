__author__ = 'blaise'

# imports
import sys
import argparse


def main():
    # parsing the arguments
    arguments = parse_arguments()

    # importing the PsimiSQL clas
    sys.path.append(arguments.sqlite_db_api)
    from sqlite_db_api import PsimiSQL

    # the nodes and the edges will be stored in a dict
    nodes = {}
    edges = {}

    # Parsing the nodes first and merging pathways and storing this in the nodes dict created above
    # (querying node to check whether it has the same pathway and than updating it with sql queries would be slow)
    with open(arguments.source_file) as source_file:
        # skipping the header line if needed
        if arguments.skip_header:
            source_file.readline()

        # setting up variables for informing the user
        num_lines = float(sum([1 for line in source_file]))
        line_counter = float(0)
        source_file.seek(0)

        # looping through the file
        for line in source_file:
            # infroming the user
            line_counter += 1
            if line_counter % 50 == 0:
                done = (line_counter / num_lines) * 100
                sys.stdout.write("Parsing mitab file (%d%%)\r" % (done))

            # deconstructing the line
            source_acc, target_acc, source_alt_acc, target_alt_acc, source_alias, target_alias, int_det_method, author, pubmed_ids, source_tax_id, target_tax_id, int_type, source_db, confidence, pathway_ids, layer, source_topology, target_topology = line.strip().split("\t")

            source_dict = {
                "name": source_acc,
                "alt_accession": source_alt_acc,
                "tax_id": source_tax_id,
                "pathways": pathway_ids,
                "aliases": source_alias,
                "topology": source_topology
            }

            add_to_nodes(source_dict, nodes)

            target_dict = {
                "name": target_acc,
                "alt_accession": target_alt_acc,
                "tax_id": target_tax_id,
                "pathways": pathway_ids,
                "aliases": target_alias,
                "topology": target_topology
            }

            add_to_nodes(target_dict, nodes)

            # adding the edge to the edges dict
            edges["%s@%s" % (source_acc, target_acc)] = {
                'interaction_detection_method': int_det_method,
                'first_author': author,
                'publication_ids': pubmed_ids,
                'interaction_types': int_type,
                'source_db': source_db,
                'interaction_identifiers': '-',
                'confidence_scores': confidence,
                'layer': layer
            }

    # informing the user
    print("Parsing MiTAB file: Finished")

    # now that we have the unique nodes we can add them to the Psi-Mi-SQL database

    # initiating the memory Mitab database
    db_api = PsimiSQL()

    num_nodes = float(len(nodes))
    line_counter = float(1)

    # inserting the nodes to the memory db
    for node_name, node_dict in nodes.items():

        #informing the user
        if line_counter % 50 == 0:
            done = float((line_counter / num_nodes) * 100)
            sys.stdout.write("Inserting nodes to NetMiTabSQL (%s%%)" % (done))
        line_counter += 1

        # inserting node to the db file
        db_api.insert_node(node_dict)

        # updating (mutating) the node dict with the SQL row id in the nodes dictionary so it can be used later
        # (again, it is faster to store the row ids fot the rows than querying each rowid)
        nodes["id"] = db_api.last_row_id

    print("Inserting nodes to NetMiTabSQL: Done")

    num_edges = float(len(nodes))
    line_counter = float(1)

    # inserting the edges to the memory db
    for edge_id, edge_dict in edges.items():

        #informing the user
        if line_counter % 50 == 0:
            done = float((line_counter / num_edges) * 100)
            sys.stdout.write("Inserting nodes to NetMiTabSQL (%s%%)" % (done))
        line_counter += 1

        source_name, target_name = edge_id.split('@')

        source_dict = nodes[source_name]
        target_dict = nodes[target_name]

        db_api.insert_edge(source_dict, target_dict, edge_dict)

    print("Inserting edges to NetMiTabSQL: Done")


    print("Saving the database to filesystem")
    # the database is finished, saving
    db_api.save_db_to_file(arguments.output_file)

    print("Database saved")



def parse_arguments():
    """
    :return: namesapce object that containse the arguments.
    """
    parser = argparse.ArgumentParser(description='Convert Net-Mitab Files to Net-Mitab-SQL')
    parser.add_argument('s', '--source-file', required=True, metavar="SourceFile", type=str,
                        help="The location of the source Net-Mitab file")
    parser.add_argument('o', '--output-file', required=True, metavar="SourceFile", type=str,
                        help="The location where the Net-PsiMi-SQL db should be saved")
    parser.add_argument('--sqlite-db-api', required=True, metavar="SQLite db API", type=str,
                        help="The location of the PsimiSQL class")
    parser.add_argument('--skip-header', metavar="Header", type=bool, default=False,
                        help="If set to true, the first line will be skipped.")

    return parser.parse_args()

def merge_strings(string_1, string_2, separator="|"):
    """
    This function merges two stings, that elements separated by a string or character.
    :param string_1:
    :type string_1: str
    :param string_2:
    :param separator:
    :type string_2: str
    :return:
    """

    if string_1 is None:
        string_1 = ""

    if string_2 is None:
        string_2 = ""

    # converting the strings to lists
    list_1 = string_1.split(separator)
    list_2 = string_2.split(separator)

    list_1 = filter(lambda item: item != '-', list_1)
    list_2 = filter(lambda item: item != '-', list_2)

    # adding the lists
    sum_lists = list_1 + list_2

    # 1) converting the lists to sets 2) removing empty elements 3) getting the union of these sets 4) converting back to list
    merged_lists = list(set(filter(None, sum_lists)))

    #  joining the list to a string
    result_string = separator.join(merged_lists)

    return result_string


def add_to_nodes(node_dict, nodes):
    """
    This function merges two nodes.
    :param node_dict: A node dictionary
    :type node_dict: dict
    :param nodes: A dictionary that holds the dictionaries of all the nodes.
    :type nodes: dict
    :return:
    """
    name = node_dict["name"]
    tax_id = node_dict["tax_id"]

    if nodes.has_key(name):
        old_node_dict = nodes[node_dict["name"]]

        new_node_dict = {
            "name": name,
            "alt_accession": merge_strings(old_node_dict["alt_accession"], node_dict["alt_accession"]),
            "tax_id": tax_id,
            "pathways": merge_strings(old_node_dict["pathways"], node_dict["pathways"]),
            "aliases": merge_strings(old_node_dict["aliases"], node_dict["aliases"]),
            "topology": merge_strings(old_node_dict["topology"], node_dict["topology"])
        }

    else:
        nodes[name] = node_dict


if __name__ == '__main__':
    main()