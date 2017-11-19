#
# File server to perform operations on files in the local filesystem.
# Operations are specified by a connecting client through a socket.
# - File lookups should be done by a different server eventually (directory service)
# - Caching should be done on the file contents (eventually)
# - Locking and threading should be done (eventually)
#
import MessageType
import os
import select
import socket
import sys

# Global constants
PORT_NUMBER = 45678
MAX_BYTES = 2048
HOST = ''
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_FILE_PATH = 'ServerDir/'

# Named constants to replace literals
FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'


def print_console_message(message):
    print('Server::\t' + message)


def open_file(path, received, connection):
    directory = path + received[1] + FORWARD_SLASH
    full_file_path = directory + received[2]

    if os.path.isfile(full_file_path):
        response = str(MessageType.FILE_EXISTS)
        print_console_message('File found - will send ' + response + 'to client')
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
        response = str(MessageType.FILE_NOT_EXISTS)
        connection.sendall(response)


def receive_file(path, received, connection):
    # Get the directory
    directory = path + received[1] + FORWARD_SLASH
    make_dir_if_not_exists(directory)

    # Get the full target filepath
    full_file_path = directory + received[2]
    print_console_message('Client wants to write to file: ' + full_file_path)

    # open the file for writing
    f = open(full_file_path, 'w')
    print_console_message('File found. Beginning download from client')
    open_connection = True
    while open_connection:
        data = connection.recv(MAX_BYTES)
        f.write(data)
        print_console_message("Writing " + str(data + " to file"))
        open_connection = len(data) == MAX_BYTES
    print_console_message('Write to file completed. Closing file.')
    f.close()

#Function to handle queries about the existence of files
def verify_dir_exists(path, message, conn):
    directory = path + message[1] + '/'
    full_file_path = directory + message[2]
    response = str(MessageType.FILE_EXISTS)
    print_console_message('Client querying directory: ' + directory + ' for file: ' + message[2])
    if os.path.exists(path):
        if not os.path.isfile(full_file_path):
            response = str(MessageType.FILE_NOT_EXISTS)
    else:
        response = str(MessageType.DIR_NOT_FOUND)
    print_console_message(response)
    conn.sendall(response)

def handle_client_connection(connection, address):
    print_console_message('Connection received from %s', str(address))
    connected = True

    while connected:
        data_received = connection.recv(MAX_BYTES)

        # Check if any data received
        if not data_received:
            continue
        else:
        # Check if request to kill fileserver
            if data_received == 'kill':
                print_console_message("Server shutdown initiated")
                connected = False
            # Check if request to read or write file
            else:
                info = data_received.split(NEWLINE_CHAR)
                request = data_received[0]
                print_console_message('Request received: ' + request)
                request = int(request)
                if request == MessageType.FILE_OPEN:
                    open_file(SERVER_FILE_PATH, info, connection)
                elif request == MessageType.FILE_WRITE:
                    receive_file(SERVER_FILE_PATH, info, connection)
                    receive_file(SERVER_FILE_PATH, info, connection)
                else:
                    verify_dir_exists(SERVER_FILE_PATH, info, connection)

    print_console_message('Connection closed')
    return connected


def make_dir_if_not_exists(requestedDirectory):
    if not os.path.exists(requestedDirectory):
        print_console_message('Directory does not exist')
        os.makedirs(requestedDirectory)
        print_console_message('Created directory')


def main():
    global PORT_NUMBER, IP_ADDRESS
    try:
        # Initialise the server
        port = PORT_NUMBER
        server_running = True
        if len(sys.argv) < 2:
            port = int(sys.argv[0])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port))
        print_console_message('Server running at:\nIP ADDRESS: ' + IP_ADDRESS + '\nPORT: ' + str(PORT_NUMBER))

        try:
            # Start listening
            s.listen(1)
            sockets_list = [s]
            print_console_message('Listening for connections...')

            # Run server until kill request received/exception thrown
            while server_running:
                read, _, _ = select.select(sockets_list, [], [], 0.1)
                for sock in read:
                    if sock is s:
                        connection, address = sock.accept()
                        print_console_message('Received a connection ')
                        server_running = handle_client_connection(connection, address)
            s.close()
            print_console_message("Server shutting down")
        except Exception as e:
            print_console_message('Exception thrown during server operation')
            print_console_message(e.message)
        finally:
            print_console_message('Closing socket')
            s.close()
    except Exception as e:
        print_console_message('Exception thrown during server initialisation')
        print_console_message(e.message)


main()
