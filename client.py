#
# Test client to demonstrate the implemented server features.
# Interaction through terminal session.
#

import MessageType
from socket import gethostbyname, SOCK_STREAM, getfqdn, socket, AF_INET, error, inet_aton

CLIENT_PATH = "ClientDir/"
DEFAULT_HOST = gethostbyname(getfqdn())
DEFAULT_PORT = 45678
MAX_BYTES = 2048

FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'


def print_message(message):
    print('Client::\t' + message + NEWLINE_CHAR)


def check_existence_on_server(path, name, specified_socket):
    # send request to server
    message = str(MessageType.VALIDATE_DIR) + NEWLINE_CHAR + path + NEWLINE_CHAR + name
    print_message('Checking server for file: ' + name + ' in path: ' + path)
    specified_socket.sendall(message)
    print_message('Sent request for server to check if file exists...')

    # get response from server
    response = specified_socket.recv(MAX_BYTES)
    print_message('Server says: ' + str(response))


def get_filename_and_filepath_from_user():
    file_path = raw_input("\nEnter file path to check: ")
    file_name = raw_input("\nEnter file name to check: ")
    return file_path, file_name


def connect_to_fileserver(host, port):
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
    print_message('Sent kill request to server')


def open_file(file_path, file_name, specified_socket):
    print_message("Will open file " + file_name)
    # send request to server for file requested
    message = str(MessageType.FILE_OPEN) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    specified_socket.sendall(message)
    print_message("Sending request to server for file as follows: " + message)

    # check if the file exists
    response = specified_socket.recv(MAX_BYTES)
    if response == str(MessageType.FILE_EXISTS):
        print_message("File exists on server!")
        full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

        # open file for writing
        print_message("Opening local file to be updated with server changes")
        f = open(full_file_path, 'w')
        print_message('Downloading file from server for reading latest version')
        maintain_connection = True
        while maintain_connection:
            data = socket.recv(MAX_BYTES)
            f.write(str(data))
            print_message('Received: ' + data)
            maintain_connection = len(data) == MAX_BYTES
        print_message('File downloaded. Will close local copy.')
        f.close()

    # inform user if the file didn't exist
    else:
        print_message('File ' + file_name + ' does not exist on the server.')


def write_file(file_path, file_name, specified_socket):
    message = str(MessageType.FILE_WRITE) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    specified_socket.sendall(message)
    full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

    # open file for reading
    f = open(full_file_path, 'r')
    print_message('Requested file found - will upload/write to server')
    data_available = True
    data = f.read(MAX_BYTES)
    while data_available:
        specified_socket.sendall(str(data))
        data = f.read(MAX_BYTES)
        data_available = data != ''
    print_message('Transmission complete, closing local copy')
    f.close()


def maintain_connection(host, port):
    sock = connect_to_fileserver(host, port)
    running = (sock != None)
    while running:
        try:
            user_input = raw_input(
            "Select option:\n1) Query server\n2) Open File\n3) Write file\n4) Kill server\nx) Close Connection\n\n")
            if user_input == "x" or user_input == "X":
                print_message('You requested to close the connection.')
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
                else:
                    if user_input == "4":
                        kill_server(sock)
                        running = False
                    else:
                        print "You said: ", user_input, NEWLINE_CHAR
        except Exception, e:
            print_message('An error occurred with handling the connection request')
            print e.message
    print "Closing connection to server. Terminating the client."
    sock.close()


def open_connection_to_server():
    user_input = raw_input("\nEnter the port number: ")

    # check that type is int
    if type(str(user_input)) == int:
        port = int(user_input)
        try:
            host = raw_input("\nEnter the IP address of the host: ")
            print_message('You provided host ' + str(host))
            inet_aton(host)
            maintain_connection(host, port)
        except error:
            print "Invalid IP address provided"
    else:
        print("\nPort number must be an integer")


def main():
    running = True
    # keep client alive for input from user continuously
    while running:
        user_action = raw_input("Select option:\n1) Open connection\n2) Default connection\nx) Exit Program\n")
        if user_action == "x" or user_action == "X":
            running = False
        else:
            # we want to do something else
            if user_action == "1":
                print_message("Opening connection to server as requested")
                open_connection_to_server()
            elif user_action == "2":
                maintain_connection(DEFAULT_HOST, DEFAULT_PORT)
            else:
                print "You said: ", get_filename_and_filepath_from_user, NEWLINE_CHAR


main()

