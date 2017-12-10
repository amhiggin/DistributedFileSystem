#
# A cache class, for a cache to be created for each client currently running.
# The cache should clear itself after the client has exited.
# This cache should store file information
#
import sys, os, json, shutil

class ClientCache():

    MAX_SIZE = 10 # TODO update
    client_id = ""

    # entry[i] = {file, version, timestamp, contents}
    num_entries = 0


    def print_to_console(self, message):
        print "Cache{0}: {1}".format(self.client_id, message)


    def __init__(self):
        self.print_to_console("Setting up the cache")


    def setup_cache(self, client_id):
            self.client_id = client_id
            self.cache = {}


    def add_cache_entry(self, key, contents, version):
        self.print_to_console("Adding cache entry for {0}".format(key))

        # FIXME first check if the cache is full, evict least recently used if so
        if not self.cache.has_key(key):
            # adding entry to cache for first time
            self.print_to_console("Adding new cache entry")
            self.cache[key] = {contents, 0}
            self.num_entries += 1
        else:
            self.print_to_console("There is an existing entry: will update")
            self.update_cache_entry(key, contents, version)


    def remove_cache_entry(self, key):
        self.print_to_console("Removing cache entry for {0}".format(key))
        del self.cache[key]
        self.num_entries -= 1
        self.print_to_console("Removed cache entry successfully")


    def fetch_cache_entry(self, key):
        return self.cache[key]


    def update_cache_entry(self, key, contents, version):
        self.print_to_console("Updating cache entry for {0}".format(key))

        if self.cache[key][1] != version:
            self.print_to_console("Cache version is {0}, incoming version is {1}".format(self.cache[key][1], version))
            self.cache[key][0] = contents
            self.cache[key][1] = version
        else:
            self.print_to_console("Version of the file in the cache ({0}) hasn't changed".format(version))


    def clear_cache(self):
        self.print_to_console("Clearing client-side cache for client {0}".format(self.client_id))
        self.cache = {}


    def is_entry_cached_and_up_to_date(self, key, file_version):
        self.print_to_console("In find_entry cache method")
        if self.cache.has_key(key):
            self.print_to_console('File {0} is cached'.format(key))
            if self.cache[key][1] == file_version:
                self.print_to_console('File {0} is up-to-date with remote copy'.format(key))
                return True
            else:
                self.print_to_console('File {0} is NOT up-to-date with remote copy'.format(key))
                return False
        else:
            self.print_to_console('File {0} is not cached'.format(key))
            return False

    # TODO should be scheduled as some sort of threadpool task in the client, since the cache should be periodically updated
    def refresh_cache_from_filesystem(self):
        if not self.cache:
            return
        else:
            for key in self.cache:
                prev_contents = self.cache[key]
                read_file = open(str(key), "r")
                curr_contents = read_file.read()
                if curr_contents == prev_contents:
                    pass
                else:
                    self.cache[key] = curr_contents
                read_file.close()



if __name__ == "__main__":
    pass
