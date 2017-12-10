'''
 A custom implementation of a cache, one of which is created for each client.
 The cache stores the 10 most recent entries, using a Least-Recently Used (LRU) eviction policy.
'''
import datetime
import itertools


class ClientCache():

    cache_id = ""
    num_entries = 0

    def print_to_console(self, message):
        print "Cache{0}: {1}".format(self.cache_id, message)


    def __init__(self):
        self.print_to_console("Setting up new cache.")

    def setup_cache(self, client_id):
        self.cache_id = client_id
        self.cache = {}
        self.cache_size = 10
        self.cache = dict(itertools.izip(xrange(self.cache_size), itertools.repeat(None)))


    # Method to return the corresponding filename for a given cache index/key
    def get_filename_by_key(self, key):
        try:
            if self.cache[key]:
                return self.cache[key]['file_name']
            else:
                return None
        except Exception as e:
            self.print_to_console("Exception occurred when getting filename by key: {0}".format(e.message))

    # Method to return the corresponding index/key in the cache for a given filename
    def get_key_by_filename(self, file_name):
        try:
            if self.num_entries == 0 or len(self.cache) == 0:
                return None
            for i in range(0, self.cache_size):
                if self.cache[i] is not None:
                    if self.cache[i]['file_name'] == file_name:
                        return i
            return None
        except Exception as e:
            self.print_to_console("Exception occurred when getting key by filename: {0}".format(e.message))

    # Method used by the LRU eviction methods, to find the least-recently-used/oldest file in the cache.
    def get_key_of_oldest_file(self):
        try:
            oldest = None
            for key in self.cache.keys():
                file_name = self.cache[key]['file_name']
                timestamp = self.cache[key]['timestamp']
                if oldest is None:
                    oldest = {'key':key, 'timestamp': timestamp}
                else:
                    difference = timestamp - oldest['timestamp']
                    if difference < datetime.timedelta(seconds=0):
                        oldest = {'key':key, 'timestamp':timestamp}
            self.print_to_console("Oldest entry has key: {0}".format(oldest['key']))
            # send back the index/key of the oldest file in the cache
            return oldest['key']
        except Exception as e:
            self.print_to_console("Exception occurred when getting LRU entry: {0}".format(e.message))

    # This method adds/updates a new file entry to the cache as appropriate, evicting an existing entry if necessary.
    def add_cache_entry(self, file_path, contents, version):
        self.print_to_console("Adding/updating entry for {0}".format(file_path))
        try:
            key = self.get_key_by_filename(file_path)

            if key not in self.cache.keys():
                self.print_to_console('{0} does not exist in the cache. Adding to the cache.'.format(file_path))
                if self.num_entries == self.cache_size:
                    self.print_to_console("Cache is full. Will evict LRU file.")
                    key = self.evict_cache_entry()
                else:
                    key = self.num_entries
                self.cache[key] = {'file_name': file_path, 'file_contents': contents, 'file_version': version, 'timestamp': datetime.datetime.now()}
                self.num_entries += 1
                self.print_to_console('Added entry successfully at key {0}'.format(key))
            else:
                self.update_cache_entry(key, contents, version)
        except Exception as e:
            self.print_to_console("Exception occurred when evicting cache entry: {0}".format(e.message))

    # This method evicts a cache entry according to the Least-Recently-Used (LRU) cache eviction policy.
    def evict_cache_entry(self):
        try:
            key = self.get_key_of_oldest_file()
            entry_to_remove = self.cache[key]
            # clear the values
            entry_to_remove.pop('file_version', 0)
            entry_to_remove.pop('file_name', "")
            self.num_entries -= 1
            self.print_to_console("Evicted LRU file from cache successfully.")
            return key
        except Exception as e:
            self.print_to_console("Exception occurred when evicting cache entry: {0}".format(e.message))

    # This method fetches a file entry from the cache, if one exists.
    def fetch_cache_entry(self, file_path):
        try:
            self.print_to_console("Fetching cache entry.")
            key = self.get_key_by_filename(file_path)
            if key is not None:
                return self.cache[key]
            else:
                self.print_to_console("File {0} is not cached.".format(file_path))
                return None
        except Exception as e:
            self.print_to_console("Exception occurred when fetching cache entry: {0}".format(e.message))


    def update_cache_entry(self, key, contents, version):
        try:
            file_name = self.get_filename_by_key(key)

            if self.cache[key]['file_version'] != version:
                self.cache[key]['file_contents'] = contents
                self.cache[key]['file_version'] = version
                self.cache[key]['file_name'] = file_name
                self.cache[key]['timestamp'] = datetime.datetime.now()
                self.print_to_console("Updated entry for {0} successfully.".format(self.cache[key]['file_name']))
            else:
                self.print_to_console("Version of the file in the cache ({0}) hasn't changed".format(version))
        except Exception as e:
            self.print_to_console("Exception occurred when updating cache entry: {0}".format(e.message))


    def clear_cache(self):
        self.print_to_console("Clearing cache for client {0}".format(self.cache_id))
        self.cache = {}


    def is_entry_cached_and_up_to_date(self, file_path, file_version):
        try:
            key = self.get_key_by_filename(file_path)
            if key is None:
                self.print_to_console("{0} is not cached.".format(file_path))
                return False

            if key in self.cache.keys():
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
        except Exception as e:
            self.print_to_console("Exception occurred when checking cache entry exists: {0}".format(e.message))


if __name__ == "__main__":
    pass
