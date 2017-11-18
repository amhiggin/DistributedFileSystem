#
# Enum to specify the types of operation we want to perform on a file
# Used by the file server to determine what the legitimate requests are.
# Used by the client to be compliant with the request types the server expects.
# Each request type maps to an integer
#
CREATE_DIR, VALIDATE_DIR, FILE_OPEN, FILE_CLOSE, FILE_WRITE, FILE_EXISTS, FILE_NOT_EXISTS, DIR_NOT_FOUND = range(8)