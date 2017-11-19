

# Class used to lock a file on the locking server
# TODO figure out where this will be used
class LockingMechanism:
    locked_list = []

    def __init__(self):
        pass

    # lock a file
    def lock_file(self, file):
        self.locked_list.append(file)

    # unlock a file
    def unlock_file(self, file):
        self.locked_list.remove(file)

    # ascertain as to whether a file is locked
    def file_locked(self, file):
        if file in self.locked_list:
            return True
        else:
            return False
