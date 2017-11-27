#
# This is the client application.
# It will use a client API to communicate with the server (the client library).
# Should be able to access the requested files by doing through the required servers.
#

ROOT_DIR = "Client/"


def print_to_console(message):
    print("Client:  " + message)


def main():
    print_to_console("Hello world from client!")
    return 0


main()
