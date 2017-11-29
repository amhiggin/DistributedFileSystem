import hashlib

def print_to_console(message):
    print ("DirectoryServer: %s%s" % (message, '\n'))

def get_lookup_value(file_name):
    hash_value = hash(file_name)
    return hash_value