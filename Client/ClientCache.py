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


    def print_to_console(self, message):
        print message


    def __init__(self):
        print("Setting up the cache")


    def setup_cache(self, cache_path, client_id):
        if not os._exists(cache_path):
            os.mkdir(cache_path)
            self.cache_dir = cache_path
            self.client_id = client_id


    def add_cache_entry(self, key, contents, version):
        print("Adding cache entry for {0}".format(key))

        # FIXME first check if the cache is full, evict least recently used if so
        if not self.cache[key]:
            # adding entry to cache for first time
            self.cache[key] = {contents, version}
            self.num_entries += 1
            print("Added new cache entry")
        else:
            print("There is an existing entry: will update")
            self.update_cache_entry(key, contents, version)


    def remove_cache_entry(self, key):
        print("Removing cache entry for {0}".format(key))
        del self.cache[key]
        self.num_entries -= 1
        print("Removed cache entry successfully")


    def fetch_cache_entry(self, key):
        print('Fetching cache entry for key {0}'.format(key))
        return self.cache[key]


    def update_cache_entry(self, key, contents, version):
        print("Updating cache entry for {0}".format(key))


    def clear_cache(self):
        print("Clearing client-side cache for client {0}".format(self.client_id))
        self.cache = {}

    def cleanup_on_client_exit(self):
        if os._exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def is_entry_cached(self, key):
        print("In find_entry cache method")
        if key in self.cache:
            return True
        else:
            return False

    # should be scheduled as some sort of threadpool task in the client, since the cache should be periodically updated
    def refresh_cache_from_filesystem(self):
        if not self.cache:
            return
        else:
            for key in self.cache:
                prev_contents = self.cache[key]
                read_file = open(key, "r")
                curr_contents = read_file.read()
                if curr_contents == prev_contents:
                    pass
                else:
                    self.cache[key] = curr_contents
                read_file.close()



if __name__ == "__main__":
    pass
