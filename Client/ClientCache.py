#
# A cache class, for a cache to be created for each client currently running.
# The cache should clear itself after the client has exited.
# This cache should store file information
#
import sys, os, json, shutil

MAX_SIZE = 1000
TABLE = {}
num_entries = 0;

class ClientCache(object):


    def print_to_console(self, message):
        print message


    def setup_cache(self, cache_path, client_id):
        print("Setting up the cache")
        if not os._exists(cache_path):
            os.mkdir(cache_path)
            self.cache_dir = cache_path
            self.client_id = client_id


    def add_to_cache(self, cache_entry):
        global num_entries, TABLE
        print("Adding cache entry for {0}".format(cache_entry))
        if TABLE.get(cache_entry)is None:#
            # this is the first time this entry has been in the cache
            TABLE[num_entries] = cache_entry
            num_entries += 1
            print("Added new cache entry")
        else:
            print("There is an existing entry: will update")
            self.update_entry_in_cache(TABLE.get(cache_entry))


    def remove_from_cache(self, cache_entry):
        print("Removing cache entry for {0}".format(cache_entry))
        global num_entries
        TABLE[num_entries] = None


    def update_entry_in_cache(self, cache_entry):
        print("Updating cache entry for {0}".format(cache_entry))


    def clear_cache(self):
        print("Clearing client-side cache for client {0}".format(self.client_id))
        if os._exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)


if __name__ == "__main__":
    pass


def setup_cache(client_id, cache_path):
    return None