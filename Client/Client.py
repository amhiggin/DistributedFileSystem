#
# This is the client application.
# It will use a client API to communicate with the server (the client library).
# Should be able to access the requested files by doing through the required servers.
#
import ClientAPI as client_api
import FileManipAPI as file_api
import shutil

CLIENT_ID = ""
running = True


def print_to_console(message):
	print ("Client%s: %s" % (CLIENT_ID, message))

def get_filename_from_user():
	file_path = raw_input("\nEnter file path: ")
	file_name = raw_input("\nEnter file name at this path: ")
	return file_path, file_name

def clean_up_after_client(cache):
	print_to_console("Cleaning up after client{0} - removing cache")
	cache.clear_cache()


def run_client():
	global running, CLIENT_ID

	print_to_console("Hello world from client!")
	CLIENT_ID = str(client_api.request_client_id())
	client_api.register_with_locking_server(CLIENT_ID)

	# create client cache directory
	cache = client_api.create_client_cache(CLIENT_ID)

	while running:

		try:
			user_input = raw_input(
				"\n-------------------------------------------------\nSelect option:\n1 = Read a file from the server \n2 = Open file locally \n3 = Write file to server\n4 = Create a new, empty local file \nx = Kill client\n\n")
			if user_input == "1":
				file_path, file_name = get_filename_from_user()
				client_api.read_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '2':
				file_path, file_name = get_filename_from_user()
				client_api.open_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '3':
				file_path, file_name = get_filename_from_user()
				client_api.write_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '4':
				file_path, file_name = get_filename_from_user()
				client_api.create_new_empty_file(file_path, file_name)
			elif user_input == 'x':
				running = False
			else:
				print_to_console("You said: " + user_input + ", which is invalid. Give it another go!\n")
		except Exception as e:
			print_to_console('An error occurred with handling the connection request')
			print_to_console(e.message)

	print "*-*-*-*-*-*-*-TERMINATING-*-*-*-*-*-*-*"
	print_to_console("Closing connection to server. Terminating the client.")
	clean_up_after_client(cache)
	exit(0)


if __name__ == "__main__":
	run_client()