#
# A cache class, for a cache to be created for each client currently running.
# The cache should clear itself after the client has exited.
# This cache should store file information
#
import sys, os, json, shutil

class ClientCache():

    MAX_SIZE = 2 # TODO update
    client_id = ""

    # entry[i] = {file, version, timestamp, contents}
    num_entries = 0


    def print_to_console(self, message):
        print "Cache{0}: {1}".format(self.client_id, message)

    def get_hash(self, file_path):
        hash_value = abs(hash(file_path))% self.MAX_SIZE
        return hash_value

    def __init__(self):
        self.print_to_console("Setting up new cache.")


    def setup_cache(self, client_id):
        self.client_id = client_id
        self.cache = {}


    def add_cache_entry(self, file_path, contents, version):
        self.print_to_console("Adding cache entry for {0}".format(file_path))
        key = self.get_hash(file_path)

        # FIXME first check if the cache is full, evict least recently used if so
        if key not in self.cache:
            # adding entry to cache for first time
            self.cache[key] = {'file_contents': contents, 'file_version': version}
            self.num_entries += 1
            self.print_to_console('Added entry successfully')
        else:
            self.update_cache_entry(file_path, contents, version)

    def remove_cache_entry(self, file_path):
        self.print_to_console("Removing cache entry for {0}".format(file_path))
        key = self.get_hash(file_path)

        if key in self.cache:
            del self.cache[key]
            self.num_entries -= 1
            self.print_to_console("Removed cache entry successfully")
        else:
            self.print_to_console("File {0} wasn't cached: cannot remove".format(file_path))


    def fetch_cache_entry(self, file_path):
        self.print_to_console("Fetching entry from cache")
        key = self.get_hash(file_path)
        return self.cache[key]


    def update_cache_entry(self, file_path, contents, version):
        self.print_to_console("Updating cache entry for {0}".format(file_path))
        key = self.get_hash(file_path)

        if self.cache[key]['file_version'] != version:
            self.cache[key]['file_contents'] = contents
            self.cache[key]['file_version'] = version
            self.print_to_console("Updated entry successfully.")
        else:
            self.print_to_console("Version of the file in the cache ({0}) hasn't changed".format(version))


    def clear_cache(self):
        self.print_to_console("Clearing cache for client {0}".format(self.client_id))
        self.cache = {}


    def is_entry_cached_and_up_to_date(self, file_path, file_version):
        key = self.get_hash(file_path)

        if self.cache.has_key(key):
            self.print_to_console('File {0} is cached'.format(file_path))
            if self.cache[key]['file_version'] == file_version:
                self.print_to_console('File {0} is up-to-date with remote copy'.format(file_path))
                return True
            else:
                self.print_to_console('File {0} is NOT up-to-date with remote copy'.format(file_path))
                return False
        else:
            self.print_to_console('File {0} is not cached'.format(file_path))
            return False


if __name__ == "__main__":
    pass
