def print_to_console(message):
    print ("DirectoryServer: %s" % message)


def get_server_file_details(file_name, file_names_on_record, connected_fileservers_by_id):
    if file_name in file_names_on_record.keys():
        print_to_console("{0} on record".format(file_name))
        file_id, server_id, file_version = file_names_on_record[str(file_name)]
        server_address = connected_fileservers_by_id[server_id]
        print_to_console("The file {0} is stored on server {1}. The corresponding server address is {2}:{3}".format(file_id, server_id, server_address[0], server_address[1]))
        return server_address, server_id, file_id, file_version
    else:
        print_to_console("File {0} isn't recorded in the directory server.".format(file_name))
        return None, None, None, None


def find_least_loaded_file_server(connected_fileservers_by_id, file_server_load_by_id):
    server_id = min(file_server_load_by_id, key=file_server_load_by_id.get)
    print_to_console("The least loaded file server is {0}".format(server_id))
    return server_id