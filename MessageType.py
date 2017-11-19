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

    CREATE_DIR = 0
    VALIDATE_DIR = 1
    FILE_OPEN = 2
    FILE_CLOSE = 3
    FILE_WRITE = 4
    FILE_EXISTS = 5
    FILE_NOT_EXISTS = 6
    DIR_NOT_FOUND = 7
