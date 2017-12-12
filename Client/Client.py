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
DISPLAY_USER_OPTIONS = "\n-------------------------------------------------\nSelect option:\n1 = Read a file \n2 = Open a file \n3 = Write to a file\n4 = Create a new, empty file \nx = Kill client\n\n"


def print_to_console(message):
	print ("Client%s: %s" % (CLIENT_ID, message))

# This method allows the user to input a file path and the name of a text file, when prompted.
def get_filename_from_user():
	file_path = raw_input("\nEnter file path: ")
	while True:
		file_name = raw_input("\nEnter file name at this path: ")
		if file_name.endswith(".txt"):
			break
		else:
			print_to_console("Invalid file-name entered: must be a .txt file.")
	return file_path, file_name

# This method cleans up the cache when the client is terminating.
def clean_up_after_client(cache):
	print_to_console("Cleaning up after client{0}'s cache")
	cache.clear_cache()

# This is the client's main method.
def run_client():
	global running, CLIENT_ID

	print_to_console("Hello world from client!")

	# Register this client with the directory and locking servers
	CLIENT_ID = str(client_api.request_client_id())
	client_api.register_with_locking_server(CLIENT_ID)

	# create a cache for this client
	cache = client_api.create_client_cache(CLIENT_ID)

	while running:
		# Display user options until they decide to exit
		try:
			user_input = raw_input(DISPLAY_USER_OPTIONS)
			if user_input == "1":
				# Read the specified file from the remote copy, if exists
				file_path, file_name = get_filename_from_user()
				client_api.read_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '2':
				# Open the local copy of the file, if exists
				file_path, file_name = get_filename_from_user()
				client_api.open_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '3':
				# Write to the specified remote copy of the file, if exists
				file_path, file_name = get_filename_from_user()
				client_api.write_file(file_path, file_name, CLIENT_ID, cache)
			elif user_input == '4':
				# Create the specified file at the specified path, if valid.
				file_path, file_name = get_filename_from_user()
				client_api.create_new_empty_file(file_path, file_name, CLIENT_ID)
			elif user_input == 'x' or user_input == 'X':
				# Terminate the client
				running = False
			else:
				print_to_console("You said: " + user_input + ", which is invalid. Give it another go!\n")
		except Exception as e:
			print_to_console('An error occurred during client operation')
			print_to_console(e.message)

	print "----------------TERMINATING----------------"
	print_to_console("Closing connection to server. Terminating the client. \n Goodbye world!")
	clean_up_after_client(cache)
	exit(0)


if __name__ == "__main__":
	run_client()