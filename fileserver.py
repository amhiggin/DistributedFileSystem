import socket, sys, Message, os

DEFAULT_PORT = 45678# server port
HOST = ''# localhost


def printMessage(message):
    print('Server::\t' + message + '\n')


def main():
    global DEFAULT_PORT

    port = DEFAULT_PORT
    if len(sys.argv) < 2 : # get port number
        port = int(sys.argv[0])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.close()
    printMessage("Server shutting down")


main()