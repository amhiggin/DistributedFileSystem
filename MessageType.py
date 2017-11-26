#
# Enum to specify the types of operation we want to perform on a file
# Used by the file server to determine what the legitimate requests are.
# Used by the client to be compliant with the request types the server expects.
# Each request type maps to an integer
#

from enum import Enum


class MessageType(Enum):
    def __str__(self):
        return str(self.value)

    # ASSIGN CLIENT ID MESSAGES
    CLIENT_ID_REQUEST = 0
    CLIENT_ID_RESPONSE = 1

    # CHECK DIRECTORY EXISTS MESSAGES
    CHECK_DIR_EXISTS = 2
    DIR_FOUND = 3
    DIR_NOT_FOUND = 4

    # CREATE AND REMOVE DIR MESSAGES
    MKDIR = 5
    RMDIR = 6
    MADE_DIR = 7
    DELETED_DIR = 8

    # FILE OPEN
    FILE_OPEN = 9
    FILE_READ = 10
    FILE_WRITE = 11

    # CREATE AND DELETE FILE MESSAGES
    CREATE_FILE = 12  # implementing
    DELETE_FILE = 13  # not used yet
    FILE_CREATED = 14
    FILE_NOT_CREATED = 15
    FILE_DELETED = 16
    FILE_NOT_DELETED = 17

    # Server response messages
    FILE_EXISTS = 18
    FILE_NOT_EXISTS = 19

    # Locking service - TODO implement
    LOCk_FILE = 20
    UNLOCK_FILE = 21
    REQUEST_LOCK = 22
    FILE_LOCKED = 23
    FILE_UNLOCKED = 24
    REQUEST_LOCK_DENIED = 25

