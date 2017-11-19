#
# Test client to demonstrate the implemented server features.
# Interaction through terminal session.

import MessageType, sys, os
from socket import gethostbyname, SOCK_STREAM, getfqdn, socket, AF_INET, error, inet_aton

CLIENT_PATH = "ClientDir/"
DEFAULT_HOST = gethostbyname(getfqdn())
DEFAULT_PORT = 12345
MAX_BYTES = 2048

FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'


def print_console_message(message):
    print('Client::\t' + message + NEWLINE_CHAR)


def check_existence_on_server(file_path, file_name, sock):
    # send request to server
    message = str(MessageType.MessageType.CHECK_DIR_EXISTS) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    print_console_message('Checking server for file: ' + file_name + ' in path: ' + file_path)
    print_console_message('Sending message: ' + message)
    sock.sendall(message)
    print_console_message('Sent request for server to check if file exists...')

    # get response from server
    response = sock.recv(MAX_BYTES)
    print_console_message('Server responded: ' + MessageType.MessageType(response))


def get_filename_and_filepath_from_user():
    file_path = raw_input("\nEnter file path: ")
    file_name = raw_input("\nEnter file name: ")
    return file_path, file_name


def connect_to_file_server(host, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))

    if s.getpeername:
        print("Connection to server established")
    else:
        print("Could not connect to server")
        s = None
    return s


def kill_server(sock):
    # send 'kill' request
    sock.sendall("kill")
    print_console_message('Sent kill request to server')


def create_file(file_path, file_name, sock):
    print_console_message("Will create new file " + file_name + ' in dir ' + file_path)
    # send request to server for file requested
    message = str(MessageType.MessageType.CREATE_FILE) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    sock.sendall(message)
    print_console_message("Sending request to server for file as follows: " + message)

    # check if the file exists
    response = sock.recv(MAX_BYTES)
    if response == str(MessageType.MessageType.FILE_EXISTS.value):
        print_console_message("File created on server!")
        full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name
        f = open(full_file_path, 'w')
    else:
        print_console_message('Could not create file ' + file_name)


def open_file(file_path, file_name, specified_socket):
    print_console_message("Will open file " + file_name)
    # send request to server for file requested
    message = str(MessageType.MessageType.FILE_OPEN.value) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    specified_socket.sendall(message)
    print_console_message("Sending request to server for file as follows: " + message)

    # check if the file exists
    response = specified_socket.recv(MAX_BYTES)
    if response == str(MessageType.MessageType.FILE_EXISTS.value):
        print_console_message("File exists on server!")
        full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

        # open file for writing
        print_console_message("Opening local file to be updated with server changes")
        f = open(full_file_path, 'w')
        print_console_message('Downloading file from server for reading latest version')
        keep_connected = True
        while keep_connected:
            data = socket.recv(MAX_BYTES)
            f.write(str(data))
            print_console_message('Received payload: ' + str(data))
            keep_connected = len(data) == MAX_BYTES
        print_console_message('File downloaded. Will close local copy.')
        f.close()

    # inform user if the file didn't exist
    else:
        print_console_message('File ' + file_name + ' does not exist on the server.')


def write_file(file_path, file_name, specified_socket):
    message = str(MessageType.MessageType.FILE_WRITE) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    specified_socket.sendall(message)
    full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

    # open file for reading
    f = open(full_file_path, 'r')
    print_console_message('Requested file found - will upload/write to server')
    data_available = True
    data = f.read(MAX_BYTES)
    while data_available:
        specified_socket.sendall(str(data))
        data = f.read(MAX_BYTES)
        data_available = data != ''
    print_console_message('Transmission complete, closing local copy')
    f.close()


def maintain_connection(host, port):
    sock = connect_to_file_server(host, port)
    running = (sock != None)
    while running:
        try:
            user_input = raw_input("Select option:\n1) Verify file exists on server \n2) Open file from server \n3) Write file from server\n4) Create a file \n5)Kill server\nx) Close Connection to Server\n\n")
            if user_input == "x" or user_input == "X":
                print_console_message('You requested to close the connection.')
                running = False
            else:
                if user_input == "1":
                    filepath, filename = get_filename_and_filepath_from_user()
                    check_existence_on_server(filepath, filename, sock)
                elif user_input == '2':
                    filepath, filename = get_filename_and_filepath_from_user()
                    open_file(filepath, filename, sock)
                elif user_input == '3':
                    filepath, filename = get_filename_and_filepath_from_user()
                    write_file(filepath, filename, sock)
                elif user_input == '4':
                    filepath, filename = get_filename_and_filepath_from_user()
                    create_file(filepath, filename, sock)
                else:
                    if user_input == '5':
                        kill_server(sock)
                        running = False
                    else:
                        print_console_message("You said: " + user_input + ", which is invalid." + NEWLINE_CHAR)
        except Exception as e:
            print_console_message('An error occurred with handling the connection request')
            print_console_message(e.message)
    print_console_message("Closing connection to server. Terminating the client.")
    sock.close()


def open_connection_to_server():
    user_input = raw_input("\nEnter the port number: ")

    # check that type is int
    if type(user_input) == int:
        try:
            port = int(user_input)
        except error:
            print_console_message('Invalid port number provided')
        try:
            host = raw_input("\nEnter the IP address of the host: ")
            print_console_message('You provided host ' + str(host))
            inet_aton(host)
            maintain_connection(host, port)
        except error:
            print_console_message("Invalid IP address provided")
    else:
        print("\nPort number must be an integer")


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
                print_console_message("Opening connection to server as requested")
                maintain_connection(DEFAULT_HOST, DEFAULT_PORT)
            else:
                print_console_message('You said: ' + user_action + NEWLINE_CHAR)


main()

