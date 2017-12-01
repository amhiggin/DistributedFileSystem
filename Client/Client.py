#
# This is the client application.
# It will use a client API to communicate with the server (the client library).
# Should be able to access the requested files by doing through the required servers.
#
import os, sys
import ClientAPI as client_api
import FileManipAPI as file_api
import shutil

NEWLINE_CHAR = "\n"
ROOT_DIR = "Client"
CLIENT_ID = ""
running = True


def print_to_console(message):
    print ("Client%s: %s%s" % (CLIENT_ID, message, NEWLINE_CHAR))


def get_filename_from_user():
    file_path = raw_input("\nEnter file path: ")
    file_name = raw_input("\nEnter file name at this path: ")
    return file_path, file_name


def format_file_path(file_path):
    return ROOT_DIR + "/" + file_path


def main():
    global running, ROOT_DIR, CLIENT_ID
    print_to_console("Hello world from client!")
    CLIENT_ID = str(client_api.request_client_id())
    ROOT_DIR = ROOT_DIR + CLIENT_ID
    file_api.create_root_dir_if_not_exists(ROOT_DIR);
    while running:
        try:
            user_input = raw_input(
                "Select option:\n1) Read a file from the server \n2) Open file from server \n3) Write file to server\n4) Close a file \n5) Create a new local directory \n6) Kill client\n\n")
            if user_input == "1":
                file_path, file_name = get_filename_from_user()
                client_api.read_file(format_file_path(file_path), file_name, CLIENT_ID)
            elif user_input == '2':
                file_path, file_name = get_filename_from_user()
                client_api.open_file(format_file_path(file_path), file_name, CLIENT_ID)
            elif user_input == '3':
                file_path, file_name = get_filename_from_user()
                client_api.write_file(format_file_path(file_path), file_name, CLIENT_ID)
            elif user_input == '4':
                file_path, file_name = get_filename_from_user()
                client_api.close_file(format_file_path(file_path), file_name, CLIENT_ID)
            elif user_input == '5':
                file_path = raw_input("\nEnter dir to create: ")
                full_file_path = format_file_path(file_path)
                if not client_api.mkdir(full_file_path):
                    print_to_console("Dir {0} already existed: didn't duplicate!".format(full_file_path))
            elif user_input == '6':
                running = False
            else:
                print_to_console("You said: " + user_input + ", which is invalid. Give it another go!" + NEWLINE_CHAR)
        except Exception as e:
            print_to_console('An error occurred with handling the connection request')
            print_to_console(e.message)
    print_to_console("Closing connection to server. Terminating the client.")
    shutil.rmtree(ROOT_DIR)
    exit(0)


main()
