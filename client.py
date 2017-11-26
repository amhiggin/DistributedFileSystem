#
# Test client to demonstrate the implemented server features.
# Interaction through terminal session.
from pip._vendor.distlib.compat import raw_input

import ClientAPI as lib
import MessageType, sys, os
from socket import gethostbyname, SOCK_STREAM, getfqdn, socket, AF_INET, error, inet_aton

DEFAULT_HOST = gethostbyname(getfqdn())
DEFAULT_PORT = 12345


def open_file_in_text_editor(full_file_path):
    os.system('gedit "{0}"'.format(full_file_path))


def main():
    running = True
    # keep client alive for input from user continuously
    while running:
        user_action = raw_input("Select option:\n1) Open connection to fileserver \nx) Exit Program\n")

        # check if want to exit
        if user_action == "x" or user_action == "X":
            running = False
        # want to connect to server
        else:
            # we want to do something else
            if user_action == "1":
                lib.print_console_message("Opening connection to server as requested")
                lib.maintain_connection(DEFAULT_HOST, DEFAULT_PORT)
            else:
                lib.print_console_message('You said: ' + user_action + lib.NEWLINE_CHAR)


main()

