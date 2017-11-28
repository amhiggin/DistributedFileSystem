import hashlib

def get_lookup_value(file_name):
    hash_value = hash(file_name)
    return hash_value