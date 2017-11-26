#
# File server to perform operations on files in the local filesystem.
# Based on the Andrew File System (AFS) model.
# Operations are specified by a connecting client through a socket.
# - File lookups should be done by a different server eventually (directory service)
# - Caching should be done on the file contents (eventually)
# - Locking and threading should be done (eventually)
#
import FileManipulation
import MessageType
import os
import select
import socket
import sys
import ThreadingHelper

# Global constants
MAX_BYTES = 2048
HOST = ''
DEFAULT_PORT = 12345
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
BASE_SERVER_FILEPATH = 'ServerDir/' # server base dir
server_running = True
number_of_clients = 0
list_of_addresses_connected = []

# Named constants to replace literals
FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'


def print_console_message(message):
    print('FileServer:\t' + message)


def set_server_running(value):
    global server_running;
    server_running = value


def get_server_running():
    return server_running


# create a directory
def mkdir(received, connection):
    full_directory_path = BASE_SERVER_FILEPATH + received[1] + FORWARD_SLASH
    response = FileManipulation.mkdir(full_directory_path)
    connection.sendall(response.encode())


# Function to handle queries about the existence of files
def verify_dir_exists(message, conn):
    directory = BASE_SERVER_FILEPATH + message[1] + FORWARD_SLASH
    full_file_path = directory + message[2]
    filename = message[2]
    print_console_message('Client querying directory: ' + directory + ' for file: ' + filename)
    response = FileManipulation.verify_dir_exists(directory, full_file_path, filename)
    conn.sendall(response.encode())


# remove a directory
def rmdir(received, connection):
    full_directory_path = BASE_SERVER_FILEPATH + received[1] + FORWARD_SLASH
    response = FileManipulation.rmdir(full_directory_path)
    connection.sendall(response.encode())


# creates a file
def create_file(received, connection):
    full_directory_path = BASE_SERVER_FILEPATH + received[1] + FORWARD_SLASH
    print_console_message('Creating new file ' + received[2] + ' in dir ' + full_directory_path)
    response = FileManipulation.create_file(full_directory_path, received[2])
    print_console_message("Sending response to client to confirm file created: " + str(MessageType.MessageType.FILE_CREATED))
    connection.sendall(response.encode())


# opening file means sending the whole file to the client
# reads and writes then happen locally
def open_file(received, connection):
    directory = BASE_SERVER_FILEPATH + received[1] + FORWARD_SLASH
    full_file_path = directory + received[2]

    # check if the requested file exists on the server
    if os.path.isfile(full_file_path):
        print_console_message("Requested file to open exists on the server")
        response = str(MessageType.MessageType.FILE_EXISTS)
        print_console_message('File found - will send code ' + response + ' to client')
        connection.sendall(response)

        # open the file
        f = open(full_file_path)
        data = f.read(MAX_BYTES)
        while data != NULL_CONTENTS:
            connection.sendall(data)
            print_console_message('Sending ' + data + ' to client')
            data = f.read(MAX_BYTES)
        print_console_message('Whole file successfully transmitted. Closing file')
        f.close()
        print_console_message('Server file closed successfully.')
    else:
        print_console_message('File does not exist: ' + full_file_path)
        response = str(MessageType.MessageType.FILE_NOT_EXISTS)
        connection.sendall(response.encode())


# this is the same as closing the file
# closing happens when the client is finished with the file
# they want to send their updates to the server
def receive_file(received, connection):
    # Get the directory
    directory = BASE_SERVER_FILEPATH + received[1] + FORWARD_SLASH
    FileManipulation.make_dir_if_not_exists(directory)

    # Get the full target filepath
    full_file_path = directory + received[2]
    print_console_message('Client wants to update/write to file: ' + full_file_path)

    # open the file for writing
    f = open(full_file_path, 'w')
    print_console_message('File opened. Beginning download from client')
    open_connection = True
    while open_connection:
        data = connection.recv(MAX_BYTES)
        f.write(data)
        print_console_message("Writing " + str(data + " to file"))
        open_connection = len(data) == MAX_BYTES
    print_console_message('Write to file completed. Closing file.')
    f.close()


def assign_client_id(connection, address):
    if not(address in list_of_addresses_connected):
        response = str(MessageType.MessageType.CLIENT_ID_RESPONSE) + NEWLINE_CHAR + str(number_of_clients + 1)
        list_of_addresses_connected.append(address)
        print_console_message("Sending response " + response + " back to the client..")
        connection.sendall(response.encode())


def send_invalid_request_provided_message(received, connection):
    print_console_message("invalid message request received from client")
    connection.sendall(str(received).encode())


def handle_request(connection, address, data_received):
    if data_received == 'kill':
        print_console_message("Server shutdown initiated")
        set_server_running(False)
        return False
        # Check if request to read or write file
    else:
        received = data_received.split(NEWLINE_CHAR)
        request = received[0]
        print_console_message('Request received: ' + request)

        if request == str(MessageType.MessageType.CLIENT_ID_REQUEST):
            # assign an id to this client
            assign_client_id(connection, address)
        elif request == str(MessageType.MessageType.FILE_OPEN):
            # send the file to the client
            if received[1] == "" or received[2] == "":
                send_invalid_request_provided_message(received, connection)
            else:
                open_file(received, connection)
        elif request == str(MessageType.MessageType.FILE_WRITE):
            # we want to update our version of the file with the changes we have
            if received[2] == "":
                send_invalid_request_provided_message(received, connection)
            else:
                receive_file(received, connection)
        elif request == str(MessageType.MessageType.CREATE_FILE):
            # we want to create a new file
            if received[2] == "":
                send_invalid_request_provided_message(received, connection)
            else:
                create_file(received, connection)
        elif request == str(MessageType.MessageType.CHECK_DIR_EXISTS):
            # we want to send back a response that the dir exists
            verify_dir_exists(received, connection)
        elif request == str(MessageType.MessageType.MKDIR):
            # we want to make a new directory
            mkdir(received, connection)
        elif request == str(MessageType.MessageType.RMDIR):
            rmdir(received, connection)
        else:
            print_console_message('Invalid request sent by client: ' + request)
        return True


# Function to handle a connection received from a client
def accept_connection(connection, address):
    print_console_message('Received a connection from ' + str(address))

    connected = True

    while connected:
        data_received = connection.recv(MAX_BYTES).decode()
        # Check if any data received
        if not data_received:
            continue
        else:
            print_console_message("Received data: " + data_received)
            connected = handle_request(connection, address, data_received)
    print_console_message('Connection closed')


def main():
    global IP_ADDRESS, BASE_SERVER_FILEPATH

    try:
        print_console_message('Initialising server')
        if sys.argv.__sizeof__() < 2:
            port = int(sys.argv[0])
        else:
            port = DEFAULT_PORT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port))
        print_console_message('Server running at:\nIP ADDRESS: ' + IP_ADDRESS + '\nPORT: ' + str(port))
        if not os.path.exists(BASE_SERVER_FILEPATH):
            print_console_message('Creating base directory')
            os.makedirs(BASE_SERVER_FILEPATH)
        print_console_message('Initialising server thread pool')
        pool = ThreadingHelper.ThreadPool(20, 20)
        set_server_running(True)

        try:
            # Start listening
            s.listen(1)
            sockets_list = [s]
            print_console_message('Listening for requests...')

            # Run server until kill request received/exception thrown
            while get_server_running():
                read, _, _ = select.select(sockets_list, [], [], 0.1)
                for sock in read:
                    if sock is s:
                        connection, address = sock.accept()
                        pool.addTask(accept_connection, connection, address)
        except Exception as e:
            print_console_message('Exception thrown during server operation')
            print_console_message(e.message)
        finally:
            print_console_message("Server shutting down")
            s.close()
            pool.endThreads()
            sys.exit(0)
    except Exception as e:
        print_console_message('Exception thrown during server initialisation')
        print_console_message(e.message)


main()
