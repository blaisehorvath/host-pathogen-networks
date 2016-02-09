import yaml
import subprocess

def run_python_script(script_location, arguments_list):
    """
    This function builds and runs a shell command
    :param script_location: The relative or absolute location of the db parser python script
    :type script_location: str
    :param arguments_list: The arguments that the script takes
    :type arguments_list: list
    :return:1
    """
    command = ' python ' + script_location + ' ' + ' '.join(arguments_list)
    subprocess.call(command, shell=True)

def main():
    with open("config.yml") as yml:
        content = yml.read()
        tasks = yaml.load(content)
        
    # parsing databases and creating PsimiSQLite files
    sql_db_api_location = tasks["parser"]["needed_packages"]["sqlite_db_api"]

    # looping through databases
    for database, settings in tasks["parser"]["databases"].iteritems():

        if database == "database1":

            arguments_dict = settings["arguments"]

            arguments_list = [
                arguments_dict["argument_1"],
                arguments_dict["argument_2"],
            ]

            run_python_script(settings["script"], arguments_list)

    # mapping the non uniprot accessions in the databases

    sqlite_db_api = tasks["mapper"]["sqlite_db_api"]
    dictionary_db_file = tasks["mapper"]["dictionary_db_file"]
    mapper_script = tasks["mapper"]["mapper_script"]

    for database, settings in tasks["mapper"]["databases"].iteritems():

        arguments_list = [
            dictionary_db_file,
            database,
            settings["source"],
            settings["destination"],
            sqlite_db_api
        ]

        run_python_script(mapper_script, arguments_list)

    # merging the layer

    arguments_list = [
        tasks["merger"]["sqlite_db_api"],
        tasks["merger"]["destination"],
        ' '.join(tasks["merger"]["source_files"])
    ]

    run_python_script(tasks["merger"]["merger_script"], arguments_list)


if __name__ == '__main__':
    main()