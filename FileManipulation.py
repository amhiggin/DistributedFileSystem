import os

import MessageType


def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        print('Directory does not exist')
        os.makedirs(directory)
        print('Created directory ' + directory)


def verify_dir_exists(directory, full_file_path, filename):
    response = str(MessageType.MessageType.FILE_EXISTS)
    # if the dir exists
    if os.path.exists(directory):
        print('The dir exists: checking for the file')
        # if dir exists but not file
        if not os.path.isfile(full_file_path):
            print('The dir exists, but not the file')
            response = str(MessageType.MessageType.FILE_NOT_EXISTS)
        else:
            print('The file ' + filename + ' exists')
    else:
        print('The dir ' + directory + ' does not exist')
        response = str(MessageType.MessageType.DIR_NOT_FOUND)
    print("Server says it will send message code: " + response + " to the client..")
    return response


def create_file(full_directory_path, filename):
    response = MessageType.MessageType.FILE_NOT_CREATED

    # make the dir if it doesn't already exist
    make_dir_if_not_exists(full_directory_path)
    # make the file
    if not os.path.exists(filename):
        full_file_path = full_directory_path + filename
        f = open(full_file_path, 'w+')
        print('File ' + filename + ' created. ')
        f.close()
        response = str(MessageType.MessageType.FILE_CREATED)
    return response


def mkdir(dir_to_make):
    response = str(MessageType.MessageType.DIR_NOT_CREATED)
    if not os.path.exists(dir_to_make):
        print("Creating directory: " + dir_to_make + " as requested")
        os.makedirs(dir_to_make)
        response = str(MessageType.MessageType.DIR_CREATED)
    return response


def rmdir(full_directory_path):
    response = str(MessageType.MessageType.DIR_NOT_DELETED)
    if os.path.exists(full_directory_path):
        os.removedirs(full_directory_path)
        print("Deleted dir " + full_directory_path)
        response = str(MessageType.MessageType.DELETED_DIR)
    return response