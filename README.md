# DistributedFileSystem
<b>Amber Higgins, M.A.I. Computer Engineering, 13327954</b>

A distributed Network File System (NFS) implementation with:
1.	Distributed transparent file access
2.	Directory service
3.	Locking service
4.	Client-side caching

Implemented in Python 2.7 using the Flask-Restful framework. All servers are run on <i>localhost</i> (hostname <b>127.0.0.1</b>). 


## Launch Instructions
The application can be run on either Windows or Linux environments. A number of shell scripts are provided for running this file-system in a <b>Linux environment</b>. Each of these will need to be given <i>execute permissions</i>, which can be assigned using the shell command '<i>chmod +x <script_name></i>'. For ease, just <b>copy and paste the following into a terminal session</b> to give execute permissions to all scripts in the repository:
 
<i>chmod +x install_dependencies.sh ; chmod +x launch_locking_server.sh ; chmod +x launch_directory_server.sh ; chmod +x launch_client.sh ; chmod +x launch_file_servers.sh </i>
 
To launch the entire distributed file-system in the least time possible, the launch order 1-5 below should be followed.
 
1. <b>install_dependencies.sh</b>

    This script should be run first, since it will install all project dependencies specified in the <i>requirements.txt</i> file.
2. <b>launch_directory_server.sh</b>

    This script launches a directory server on localhost, at URL <b>http://127.0.0.1:5000</b>.
3. <b>launch_locking_server.sh</b>

    This script launches a locking server on localhost, at URL <b>http://127.0.0.1:5001</b>.
4. <b>launch_file_servers.sh</b>

    This script launches a number of file-servers on localhost, which will connect to the directory server if available. The number of file-servers should be specified by the user as <b>$1</b>. Each file-server will then be launched on sequential ports, starting from port <b>45678</b>. This means that the first file-server to be launched will be available at <b>http://127.0.0.1:45678</b>.
       * <b>Note</b>: this script will also kill any existing processes running on these ports, before attempting to attach. This was deemed to be acceptable since this range of ports is not reserved for any specific application.
5. <b>launch_client.sh</b>

    This script launches a client application, which will connect to the directory and locking servers if they are available. Since the client requires user input, each client should be launched individually in a separate session.


## Dependencies
* Python 2.7.9
* flask
* flask-restful
* requests
* werkzeug


## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server. However I realised after some time that the Restful approach was a lot simpler, abstracting away the low-level implementation details and allowing me to get on with the feature implementation.
* The commit at which I scrapped working with sockets can be found [here](https://github.com/amhiggin/DistributedFileSystem/commit/104ee0e5f1b3785d61622c3673e9c9773e2a6969). 

# Documentation


## Distributed Transparent File Access
The system operates according to the Network File System (NFS) model. It can support multiple connected clients, and multiple fileservers. It deals <i>exclusively</i> with .txt files.

### Client Library
All file accesses are made through a client library called a client library called <b><i>ClientApi.py</i></b>. This library is the interface exposed to the client-side application for manipulation of the local and remote file-systems (also the cache: see later sections). By using the library, the under-the-hood implementation details of the distributed file-system are hidden from the client application.

Clients can:
*	Access remote copies of files stored on file-servers through the <i>read</i> and <i>write</i> function calls. They can also create new files, and open existing files locally to view the contents.
* Interact with file contents through the system editor, which is launched before every remote write and after every remote read. In Windows, this is <b>notepad.exe</b>, and in Linux it is <b>nano</b> which is used.

<b>Note on opening files:</b> in order to 'open' a file in read-only mode, the contents of the file are displayed in the console window.</i> Opening the file in the text editor (as is done with the <i>read</i> and <i>write</i> operations) would give an individual the option to edit the file when they should really just be able to view the contents - an undesirable behaviour that is resolved by this approach.


### Client application
This application, called <b><i>Client.py</i></b>, provides a simple console-based UI offering options to manipulate files. This includes reading, writing, opening and creating of text files. 

* In the background, the user's choices when interacting with the system are routed through the client library to the appropriate services (e.g. cache, locking server, directory server, file server), providing abstraction from the underlying technical implementation.
* When a text file is created for the first time, the specified directory is automatically created if it doesn’t already exist. Error handling is included to prevent overwriting of existing file contents.
* All files on the local filesystem are visible to every active client using the system, meaning that concurrent accesses to files can easily occur. However, each client implements its own cache, allowing them to keep their own most frequently accessed content close at hand.
* Upon termination of the client, the contents of the cache are erased: however, no changes are made to the files in the local file-system.




## Directory Service
A directory service in any distributed file-system has the function of converting human-readable file names displayed to a client, into non-verbose file identifiers on remote file-servers. It acts as a namespace for the system that maps a unique filename (from which the client can be identified) to a unique file identifier (from which the remote file server can be identified) – an intermediary between the client and the remote file-servers.

### Directory Server
The system has one directory server located at a known address of <b>http://127.0.0.1:5000/</b>, called <b><i>DirectoryServer.py</i></b>. This server acts as a management application for the distributed file-system.  It maintains a record of the mappings of full client-side filenames to enumerated file identifiers on the remote file-servers.

Amongst other responsibilities, it:
* Provides a registration mechanism for -
  * Client applications, at URL endpoint <b>http://127.0.0.1:5000/register_client</b>
  * File-servers, at URL endpoint <b>http://127.0.0.1:5000/register_fileserver</b>
  
  including the assignment of unique ids to each;
* Records connection details for clients and file-servers that have registered with it;
* Load-balances connected file-servers, such that at any time the least-loaded server will be given any new loading;
* Maintains records of client-fileserver file-directory mappings, where clients provide a full file path (e.g. ../Client0/hello.txt) and this is mapped to a unique server-side identifier in the server’s root directory (e.g. ../Server10/18.txt).
* Maintains versioning of the files using integer values, according to the number of times they have been updated by clients. This is a crucial enabling element of the client-side caching. After a client-fileserver write-update has occurred successfully, the client updates the record of the file with the directory server at URL endpoint <b>http://127.0.0.1:5000/update_file_version</b>.


### Remote File Server
It is possible to have as many file servers as desired in this distributed file-system, since each file server registers with (and is subsequently managed by) the directory server when it is launched.

The file-servers are implemented as a flat-file system, with each storing files in a single directory. This directory uses the naming pattern <b>ServerX</b>, where X is an id assigned to the server when it registers with the directory server. All files stored on a file server follow a simple numerical naming system: for example, <i>0.txt</i> for the first file created on the server.

Each server accepts <i>get()</i> and <i>post()</i> requests from clients. It can be reached at any available host address and port specified by the user, which are provided as <b>sys.argv[1]</b> and <b>sys.argv[2]</b>. Each fileserver should be started on a <i>different port number</i>, and this mechanism is provided in the accompanying launch scripts.

* A client wishing to <b>read</b> a remote copy of a file will send a <i>get()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_server_id': server_id
* A client wishing to <b>write</b> to a remote copy of a file will send a <i>post()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_contents': file_contents

<b>Notes:</b> 
* The fileserver does not hold any versioning information about the files that it stores: it is the directory server which handles this. Versioning is used as part of the caching mechanism.
* The client is able to identify the values of 'file_id' and 'file_server_id' by consulting the directory server for the file mapping it requires.
* The fileserver, upon startup, also erases any previous contents of a root directory under the same name, e.g. if a directory called 'Server0/' exists from a previous run of the application, when a new Server0 is launched it will erase the contents of this file.




## Locking Service
A locking service provides concurrency control for multiple clients requiring access to the same files. It allows clients exclusive access to files under particular conditions.

A client must request and successfully acquire a single lock for a file in order to perform a restricted-access operation (such as a write). This means that for all writes in the distributed file-system, the request must first be routed through a <b>locking server</b> before access to the remote copy is granted.

### Locking Server
There is one locking server in this distributed file-system, called <b><i>LockingServer.py</i></b>. It manages the operation of locking and unlocking files as requested by clients. It is accessible at URL endpoint <b>http://127.0.0.1:5001/</b>. Any requests for a read or write on a remote file copy must first be routed through this service for approval. However, <b>only write-locks may be acquired</b>: there is no concept of a read-lock in this file-system.

Each file which exists on a remote fileserver will have a corresponding record with the locking server. This record exists as a lookup-table, where each entry is a [file_id, is_locked] pair.

The locking server also maintains a record of the clients that have registered with it. Clients must register with the locking server when they start up, connecting to URL endpoint <b>http://127.0.0.1:5001/register_new_client</b>. By doing this, it is ensured that:
* Only validated clients may lock or unlock a file, and not just anyone who can access the locking server URL;
* Since any client who is granted a lock will have their client_id stored with the locking server's records for that file, we prevent a client who didn't lock the file originally, from releasing the lock on the file.

There are a number of other conditions that can occur in the locking and unlocking of a file in the distributed file-system. Some of these scenarios are as follows:
* A client wishing to write to a file must request the lock for that file. They will not be granted the lock until the file is no longer locked by another client. Until they are granted the lock, the requesting client essentially <b>polls</b> the locking server. 
* A client wishing to read a file, will not be able to read it until it is unlocked. However, no read operation requires the acquisition of a lock - the file simply should not be readable until it is no longer locked by another client.
* To guard against infinite waiting for a lock to be released by a client, a safety mechanism in the form of a timeout (<b>60 seconds</b>) is used. After the timeout has elapsed, if the file is still locked, it will be assumed that the client who locked it has died and the lock is released by the server itself.


<b>Notes</b>:
* <i><b>Assumption</i></b>: when a remote copy is created for the first time on a fileserver, it doesn't need to be locked (nobody will try to concurrently access the file until after it has been created).



## Client-side Caching
A caching solution in a system allows for quicker access time to files if used effectively. It involves the local storage of up-to-date copies of files, so that if the remote copy of a file hasn’t changed since the last time it was accessed, it can be read locally rather than requiring a request over the network. By using caching, the performance of a system can be enhanced since the servers are likely to have less loading at a given time. However, if not implemented appropriately on the client-side it can introduce unnecessary runtime overheads.

In general, it is most efficient to use caching on the client-side to reduce the number of relatively-slow calls required over the network – particularly in the case of file reads. Concerns such as cache invalidation for out-of-date copies of cached files, and an eviction policy in order to keep the contents of the cache relevant and small in number, are important to consider.

### Cache
A custom-implemented cache called <b><i>ClientCache.py</i></b> is used to provide client-side caching in this distributed file-system. An individual cache is created for each client during initialisation: this allows each client to cache the files that they access most often both close at hand and up-to-date. The cache uses a look-up table with a maximum number of entries, whose contents are managed using (i) file versioning, and (ii) a Least-Recently-Used (LRU) cache eviction policy.

Operations implemented in the cache include: adding entries, updating entries, finding entries, evicting entries, and clearing the cache upon exit. Each cache entry looks similar to:

  <b>cache[file_id] = {'file_contents': file_contents, 'file_version': file_version, 'file_name': file_name, 'timestamp' timestamp}</b>

The timestamp is used to determine the age of the file, and the version is used to determine whether the entry is up-to-date with the remote copy at any given time.

The benefit of the cache is the reduction in volume of traffic going over the network, as well as more instantaneous access to files in many cases. As an NFS implementation, the benefits of this are most clearly seen when performing read operations.


1.	<b>Read</b>: The cache is checked for an entry corresponding to the file to be read.
  	* If there exists a corresponding entry, then the version is checked against that recorded with the directory server.
  	* If the cache copy is of an outdated version of the file, then a request is made to the file-server on which the remote copy is stored to provide the most up-to-date copy of the file. 
  	* If the copy in the cache is up-to-date with the remote copy, the copy from the cache is used. This results in two fewer network accesses: one saving by not needing to request the file from the file-server, and another by the file-server not needing to service an extra request.
2.	<b>Write</b>:	The cache is updated after a successful write to a remote file copy.
  	* When a client writes to a file, the cache will not be updated until the remote copy has been updated. If it did, the cache copy and remote copy could easily become out of sync if the remote write failed.
  	* Once the remote write has occurred successfully, a cache copy is either (i) created, or (ii) updated for that file in the particular client's cache.
  	   	* If a cache copy is created, then an initial file-version, a timestamp and all of the specific file details are stored in a cache entry.
  	   	* If a cache copy already existed, this cache copy is simply updated. This involves updating the version (compared to that previously recorded on the directory server), updating the timestamp to the current time, and updating the file contents with the new contents.
  	* Thanks to the implementation of the <b>locking service</b> for remote write operations, concurrent updates to a remote file are sequenced such that any cache update will be correct at the time that its corresponding remote-write update occurs.
  	* The updating of the version of the file on the directory server occurs during the write operation, before the updating of the cache. This ensures that any references that the cache makes to the remote copy's version, will be based on the latest update of record for that file on the directory server.
3.	<b>Open</b>: since the file-system is implemented to replicate the NFS model, there are no calls across the network for the open operation, and the file as it exists in the cache is simply displayed in read-only mode.
<b>Note on opening files:</b> in order to 'open' a file in read-only mode, the contents of the file are displayed in the console window.</i> Opening the file in the text editor (as is done with the <i>read</i> and <i>write</i> operations) would give an individual the option to edit the file when they should really just be able to view the contents - an undesirable behaviour that is resolved by this approach. 

<b>LRU Eviction Policy</b>: The Least-Recently Used cache eviction policy enforces a maximum number of cache entries at any particular time. This allows the cache to be indexed more quickly, and keeps the contents maximally relevant to the needs of the client it is associated with. 
* In this implementation, <b>a maximum of 10 entries</b> can be stored in the cache at any given time. This empirically selected value could easily be increased or decreased depending on the requirements of this cache in practise - however, for this experimental design a small value is more than sufficient.
* Once the cache is full, the client will not be able to add another entry until the least-recently used entry has been evicted. The least-recently used entry is determined by the timestamp of the entry, which corresponds to the last time at which the cache entry was updated.

Upon termination of the client, the contents of the cache are erased. The copies of the corresponding files in the local file-system however, are persisted.

# Operation Examples
In order to best explain the operation of the distributed file-system, some sequences of screenshots corresponding to different scenarios are provided below with brief explanations.

### Launch and Registration of Directory Server, Locking Server, Multiple Clients, Multiple Fileservers
1. Client Output: Launching and registering two clients (Client0, Client1)
![launch_two_clients](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%202%20clients%20running%20at%20same%20time.PNG)

2. Fileserver Output: Launching and registering multiple fileservers
![launch_two_fileservers](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/file%20server%20-%20multiple%20fileservers%20launched.PNG)

3. Directory Server Output: Launching and registering multiple clients and fileservers 
![registered_two_clients_two_fileservers](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20multiple%20fileservers%20AND%20multiple%20clients.PNG)

4. Locking Server Output: Launching and registering multiple clients
![registered_two_clients](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/locking%20server%20-%20registration%20of%20two%20clients%20with%20locking%20server.PNG)

### Creating a New File Locally
1. Client creating a new file successfully
![create_new_empty_file](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20create%20new%20empty%20file%20successfully%20including%20new%20directory.PNG)

2. Incorrect attempt to create a non '.txt' file
![incorrect_txt_file_creation](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20handling%20non-txt%20file%20entered%20during%20file%20creation.PNG)

3. Incorrect attempt to re-create existing file
![incorrect_creation_file_already_exists](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20attempt%20to%20create%20file%20that%20already%20exists.PNG)


### Request Remote Read with No Fileservers Launched
1. Client error message when no fileservers exist
![client_no_fileservers_launched](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20no%20fileservers%20registered.PNG)

2. Directory server error message when no fileservers exist
![dir_server_no_fileservers_launched](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20no%20fileservers%20registered.PNG)

### Attempt to Read Non-Existent Remote Copy
1. Client application output

![client_read_non_existent_remote_copy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20trying%20to%20read%20non-existent%20remote%20copy.PNG)

2. Directory server response to request
![dir_server_non_existent_remote_copy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20no%20remote%20copy%20found%20after%20read%20request%20received.PNG)

### Create New Remote File Copy (First Write)
1. Client input for writing to a new remote copy of file <i>Hello/hello.txt</i>
![client_first_write_new_remote_copy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20writing%20to%20NEW%20remote%20copy.PNG)

2. Writing to <i>Hello/hello.txt</i> in Nano (Linux) and Notepad (Windows)
![open_file_nano](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20writing%20of%20a%20file%20in%20NANO.PNG)

![open_file_notepad](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20writing%20of%20a%20file%20in%20notepad.PNG)

3. Directory server output for creating new remote copy of file
![create_new_remote_copy_dir_server](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/creation%20of%20new%20remote%20copy%20of%20file%20-%20directory%20server.PNG)

4. File server output for creating new remote copy of file
![create_new_remote_copy_file_server](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/creating%20new%20remote%20copy%20of%20file%20-%20fileserver.PNG)

### Reading Up-to-Date Cached Copy of File
1. Client reading up-to-date cache copy of file <i>Hello/hello.txt</i>
![client_cache_read_up_to_date](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20reading%20up%20to%20date%20cache%20copy.PNG)

2. Directory Server response to request for version of file <i>Hello/hello.txt</i>
![dir_server_providing_file_version](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20providing%20version%20information%20on%20up-to-date%20cached%20file%20to%20client.PNG)

### Writing to Existing Remote Copy
1. Client output when writing to existing remote copy
![client_writing_to_remote_copy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20writing%20update%20to%20remote%20copy.PNG)

2. Directory server response to request for remote copy mapping
![provide_remote_copy_mapping_dir_server](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20write-update%20remote%20copy.PNG)

3. Locking server allowing lock of remote copy for writing
![lock_requested_remote_copy_locking_server](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/locking%20server%20-%20locking%20and%20unlocking%20a%20file.PNG)

4. Fileserver performing update on remote copy
![fileserver_update_remote_copy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/file%20server%20-%20write%20update%20to%20remote%20copy.PNG)

### Load-Balancing Multiple File Servers
1. Directory Server Output: Load-Balancing
![load_balancing](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/directory%20server%20-%20load%20balancing.PNG)

### Timeout of File Lock
1. Client2 places write-lock on file <i>Hello/hello.txt</i> and never releases it
![client2_never_releases_lock](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client2%20-%20never%20releases%20lock.PNG)

2. Client0 requests and obtains write-lock on file <i>Hello/hello.txt</i>
![client0_requests_already_locked_file](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client0%20-%20obtains%20lock%20after%20timeout.PNG)

3. Locking server releases lock on <i>Hello/hello.txt</i> after timeout elapses
![lock_timeout_release](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/locking%20server%20-%20timeout%20on%20lock.PNG)

### Invalidation of File's Cache Copy
1. Client1 performing a write-update on remote copy of <i>Hello/hello.txt</i> created by Client0
![client1_invalidating_client0_cachecopy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client1%20-%20invalidating%20client0s%20cache%20copy.PNG)

2. Client0 invalidating and updating it's cache copy of <i>Hello/hello.txt</i> on a read
![client0_updating_cachecopy](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client0%20-%20updating%20its%20invalidated%20cache%20copy.PNG)

### LRU Cache Eviction
1. Client console output for cache eviction
![cache_eviction](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20LRU%20eviction.PNG)

### Termination of Client
1. Console output showing the termination of a client
TODO!!!
![client_termination](https://github.com/amhiggin/DistributedFileSystem/blob/master/Screenshots/client%20-%20termination%20of%20client.PNG)

