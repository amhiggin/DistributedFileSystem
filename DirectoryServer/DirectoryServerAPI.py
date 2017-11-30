import hashlib


def print_to_console(message):
    print ("DirectoryServer: %s%s" % (message, '\n'))


def get_server_file_details(file_name, file_names_on_record, connected_fileservers_by_id):
    if file_name in file_names_on_record.keys():
        print "{0} on record - now will have to find where it is".format(file_name)
        file_id, server_id = file_names_on_record[str(file_name)]
        print_to_console("The file id is {0}, server id is {1}".format(file_id, server_id))
        server_address = connected_fileservers_by_id[server_id]
        print_to_console("The corresponding server address is {0}:{1}".format(server_address[0], server_address[1]))
        return server_address, server_id, file_id
    else:
        print "File {0} isn't recorded in the directory server. Sending back nulls.".format(file_name)
        return None, None, None


def find_least_loaded_file_server(connected_fileservers_by_id, file_server_load_by_id):
    print_to_console("Searching for the currently least-loaded file server..")
    server_id = min(file_server_load_by_id, key=file_server_load_by_id.get)
    print_to_console("The least loaded file server is {0}".format(server_id))
    return server_id