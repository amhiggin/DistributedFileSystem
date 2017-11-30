import hashlib

def print_to_console(message):
    print ("DirectoryServer: %s%s" % (message, '\n'))

def get_lookup_value(file_name):
    hash_value = hash(file_name)
    return hash_value


def get_server_file_details(file_name, file_names_on_record, connected_fileservers_by_id):
    if file_name in file_names_on_record.keys():
        print "{0} on record - now will have to find where it is".format(file_name)
        file_id, server_id = file_names_on_record[str(file_name)]
        server_address = connected_fileservers_by_id[server_id]
        return server_address, server_id, file_id
    else:
        print "File {0} isn't recorded in the directory server".format(file_name)
        return None, None, None