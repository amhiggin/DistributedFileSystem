#
# File server to perform operations on files in the local filesystem.
# Operations are specified by a connecting client through a socket.
# - File lookups should be done by a different server eventually (directory service)
# - Caching should be done on the file contents (eventually)
# - Locking and threading should be done (eventually)
#

import sys

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

from threading import Thread
import MessageType
import os
import select
import socket

# Global constants
PORT_NUMBER = 45678
MAX_BYTES = 2048
HOST = ''
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
SERVER_FILE_PATH = 'ServerDir/'
server_running = True

# Named constants to replace literals
FORWARD_SLASH = '/'
NULL_CONTENTS = ''
NEWLINE_CHAR = '\n'


class Worker(Thread):
    def __init__(self, queue):
        self.tasks = queue
        self.on = True
        Thread.__init__(self)
        self.start()  # Start thread

    def run(self):
        while self.on:
            func, args, kargs = self.tasks.get()
            self.on = func(*args, **kargs)


class ThreadPool:
    def __init__(self, num_threads, queue_size):
        self.queue = queue.Queue(queue_size)
        self.num = num_threads
        self.threads = []
        for i in range(0, num_threads):  # Start each thread and add to the list
            self.threads.append(Worker(self.queue))

    def addTask(self, func, *args, **kargs):
        self.queue.put((func, args, kargs))

    def endThreads(self):
        for i in range(0, self.num):
            self.addTask(False)
        for i in range(0, self.num):
            self.threads[i].join()


def print_console_message(message):
    print('FileServer:\t' + message)


def set_server_running(value):
    server_running = value


def server_running():
    return server_running


def open_file(path, received, connection):
    directory = path + received[1] + FORWARD_SLASH
    full_file_path = directory + received[2]

    # check if the requested file exists on the server
    if os.path.isfile(full_file_path):
        print_console_message("Requested file to open exists on the server")
        response = str(MessageType.MessageType.FILE_EXISTS)
        print_console_message('File found - will send code ' + response + 'to client')
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
    print_console_message('File opened. Beginning download from client')
    open_connection = True
    while open_connection:
        data = connection.recv(MAX_BYTES)
        f.write(data)
        print_console_message("Writing " + str(data + " to file"))
        open_connection = len(data) == MAX_BYTES
    print_console_message('Write to file completed. Closing file.')
    f.close()


# Function to handle queries about the existence of files
def verify_dir_exists(path, message, conn):
    directory = path + message[1] + '/'
    full_file_path = directory + message[2]

    print_console_message('Client querying directory: ' + directory + ' for file: ' + message[2])
    # default value
    response = MessageType.MessageType.FILE_EXISTS
    # if the dir exists
    if os.path.exists(path):
        print_console_message('The dir exists: checking for the file')
        # if dir exists but not file
        if not os.path.isfile(full_file_path):
            print_console_message('The dir exists, but not the file')
            response = MessageType.MessageType.FILE_NOT_EXISTS
        else:
            print_console_message('The file exists within the dir - file found!')
    # if dir doesn't exist
    else:
        print_console_message('The dir does not exist')
        response = MessageType.MessageType.DIR_NOT_FOUND
    print_console_message('Server says it will send message code: ' + str(response) + " to the client..")
    conn.sendall(str(response))


# creates a file
def create_file(path, received):
    full_directory_path = path + received[1] + NEWLINE_CHAR
    print_console_message('Creating new file' + received[2] + ' in dir ' + full_directory_path)

    # make the dir if it doesn't already exist
    make_dir_if_not_exists(full_directory_path)
    # make the file
    full_file_path = full_directory_path + received[2]
    f = open(full_file_path, 'w')
    print_console_message('File ' + received[2] + 'created. ')
    f.close()


# Function to handle a connection received from a client
def accept_connection(connection, address):
    print_console_message('Received a connection from ' + str(address))
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
                server_running = False
            # Check if request to read or write file
            else:
                received = data_received.split(NEWLINE_CHAR)
                request = data_received[0]
                print_console_message('Request received: ' + str(request))
                if request == MessageType.MessageType.FILE_OPEN.value:
                    open_file(SERVER_FILE_PATH, received, connection)
                elif request == MessageType.MessageType.FILE_WRITE.value:
                    receive_file(SERVER_FILE_PATH, received, connection)
                elif request == MessageType.MessageType.CREATE_FILE.value:
                    create_file(SERVER_FILE_PATH, received)
                elif request == MessageType.MessageType.CHECK_DIR_EXISTS.value:
                    verify_dir_exists(SERVER_FILE_PATH, received, connection)
                else:
                    print_console_message('Invalid request sent by client: ' + request)

    print_console_message('Connection closed')
    return connected


# creates a directory if the required directory doesn't already exist
def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        print_console_message('Directory does not exist')
        os.makedirs(directory)
        print_console_message('Created directory' + directory)


def main():
    global IP_ADDRESS, SERVER_FILE_PATH

    try:
        print_console_message('Initialising server')
        if len(sys.argv) < 2:
            port = int(sys.argv[0])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, port))
        print_console_message('Server running at:\nIP ADDRESS: ' + IP_ADDRESS + '\nPORT: ' + str(PORT_NUMBER))
        if not os.path.exists(SERVER_FILE_PATH):
            print_console_message('Creating base directory')
            os.makedirs(SERVER_FILE_PATH)
        print_console_message('Initialising server threadpool')
        pool = ThreadPool(10, 10)
        set_server_running(True)

        try:
            # Start listening
            s.listen(1)
            sockets_list = [s]
            print_console_message('Listening for requests...')

            # Run server until kill request received/exception thrown
            while server_running():
                read, _, _ = select.select(sockets_list, [], [], 0.1)
                for sock in read:
                    if sock is s:
                        connection, address = sock.accept()
                        pool.addTask(accept_connection, connection, address)
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
