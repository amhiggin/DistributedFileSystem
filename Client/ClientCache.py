#
# A cache class, for a cache to be created for each client currently running.
# The cache should clear itself after the client has exited.
# This cache should store file information
#
import sys, os, json, shutil

class ClientCache():

    MAX_SIZE = 1000
    client_id = ""
    cache_dir = ""

    # entry[i] = {file, version, timestamp, contents}
    cache = {}
    num_entries = 0

    def __init__(self, cache_path, client_id):
        print("Setting up the cache")
        if not os._exists(cache_path):
            os.mkdir(cache_path)
            self.cache_dir = cache_path
            self.client_id= client_id


    def print_to_console(self, message):
        print message


    def add_to_cache(self, key, contents, version):
        print("Adding cache entry for {0}".format(key))

        if not self.cache[key]:
            # this is the first time this entry has been in the cache
            self.cache[key] = {contents, version}
            self.num_entries += 1
            print("Added new cache entry")
        else:
            print("There is an existing entry: will update")
            self.update_entry_in_cache(key, contents, version)


    def remove_from_cache(self, key):
        print("Removing cache entry for {0}".format(key))
        del self.cache[key]
        self.num_entries -= 1
        print("Removed cache entry successfully")


    def update_entry_in_cache(self, key, contents, version):
        print("Updating cache entry for {0}".format(key))


    def clear_cache(self):
        print("Clearing client-side cache for client {0}".format(self.client_id))
        if os._exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)


    def test_if_file_has_cache_entry(self, key):
        print("In find_entry cache method")
        if key in self.cache:
            return True
        else:
            return False

    def fetch_cache_entry(self, key):
        return self.cache[key]



if __name__ == "__main__":
    pass
