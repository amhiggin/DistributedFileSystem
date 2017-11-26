import MessageType, sys, os
from socket import gethostbyname, SOCK_STREAM, getfqdn, socket, AF_INET, error, inet_aton
import FileManipulation as file_lib

MAX_BYTES = 2048
FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'
CLIENT_PATH = "Client"


def print_console_message(message):
    print('Client:\t' + message + NEWLINE_CHAR)


def get_filename_and_filepath_from_user():
    file_path = raw_input("\nEnter file path: ")
    file_name = raw_input("\nEnter file name: ")
    return file_path, file_name


def check_existence_on_server(file_path, file_name, sock):
    # send request to server
    message = str(MessageType.MessageType.CHECK_DIR_EXISTS) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    print_console_message('Checking server for file: ' + file_name + ' in path: ' + file_path)
    print_console_message('Sending message: ' + message)
    sock.sendall(message.encode())
    print_console_message('Sent request for server to check if file exists...')

    # get response from server
    response = sock.recv(MAX_BYTES).decode()
    print_console_message('Server responded: ' + response)


def connect_to_file_server(host, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))

    if s.getpeername:
        print("Connection to server established")
    else:
        print("Could not connect to server")
        s = None
    return s


def get_client_id_in_system(sock):
    global CLIENT_ID, CLIENT_PATH
    print_console_message("Requesting client id from server")
    request = str(MessageType.MessageType.CLIENT_ID_REQUEST)
    sock.sendall(request.encode())
    response = str(sock.recv(MAX_BYTES).decode())
    received = response.split(NEWLINE_CHAR)
    print_console_message("Received response " + received[0] + " from server")
    if received[0] == str(MessageType.MessageType.CLIENT_ID_RESPONSE):
        CLIENT_ID = received[1]
        CLIENT_PATH = CLIENT_PATH + CLIENT_ID
        file_lib.make_dir_if_not_exists(CLIENT_PATH)
        CLIENT_PATH = CLIENT_PATH + FORWARD_SLASH
    print_console_message("Client id is: " + CLIENT_ID + ". Root dir is now: " + CLIENT_PATH)


def kill_server(sock):
    # send 'kill' request
    sock.sendall("kill".encode())
    print_console_message('Sent kill request to server')


def create_file(file_path, file_name, sock):
    print_console_message("Will create new file " + file_name + ' in dir ' + file_path)
    # send request to server for file requested
    message = str(MessageType.MessageType.CREATE_FILE) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    sock.sendall(message.encode())
    print_console_message("Sending request to server for file as follows: " + message)

    # check if the file exists
    response = str(sock.recv(MAX_BYTES).decode())
    if response == str(MessageType.MessageType.FILE_CREATED):
        print_console_message("File created on server!")
        full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name
        f = open(full_file_path, 'w+')
        print_console_message("File created on client now too to mirror this!")
    else:
        print_console_message('Could not create file ' + file_name)


# same as a read - we want to download the whole file from the server
def open_file(file_path, file_name, sock):
    print_console_message("Will open file " + file_name)
    # send request to server for file requested
    message = str(MessageType.MessageType.FILE_OPEN) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    sock.sendall(message.encode())
    print_console_message("Sending request to server for file as follows: " + message)

    response = sock.recv(MAX_BYTES)
    # check if the file exists
    if response == str(MessageType.MessageType.FILE_EXISTS):
        print_console_message("File exists on server!")
        full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

        # open file for writing
        print_console_message("Opening local file " + full_file_path + " to be updated with server changes")
        f = open(full_file_path, 'w+')
        print_console_message('Downloading file from server for reading latest version')
        keep_connected = True
        while keep_connected:
            data = sock.recv(MAX_BYTES)
            f.write(data)
            print_console_message('Received payload: ' + str(data))
            keep_connected = len(data) == MAX_BYTES
        print_console_message('File downloaded. Will close local copy.')
        f.close()

    # inform user if the file didn't exist
    else:
        print_console_message('File ' + file_name + ' does not exist on the server.')


def write_file(file_path, file_name, sock):
    message = str(MessageType.MessageType.FILE_WRITE) + NEWLINE_CHAR + file_path + NEWLINE_CHAR + file_name
    sock.sendall(message.encode())
    full_file_path = CLIENT_PATH + file_path + FORWARD_SLASH + file_name

    # open file for reading
    print_console_message("Opening file " + full_file_path + " for writing to server")
    f = open(full_file_path, 'r')
    data_available = True
    data = f.read(MAX_BYTES)
    while data_available:
        sock.sendall(str(data))
        [print_console_message("Sending " + str(data) + " to server")]
        data = f.read(MAX_BYTES)
        data_available = data != ''
    print_console_message('Transmission complete, closing local copy')
    f.close()


def maintain_connection(host, port):
    sock = connect_to_file_server(host, port)
    running = sock is not None
    # assign a global id for this client
    get_client_id_in_system(sock)
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
        print(NEWLINE_CHAR + "Port number must be an integer")