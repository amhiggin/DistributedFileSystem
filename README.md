# DistributedFileSystem
<b>Amber Higgins, M.A.I. Computer Engineering, 13327954</b>

A distributed Network File System (NFS) implementation with:
1.	Distributed transparent file access
2.	Directory service
3.	Locking service
4.	Client-side caching

Implemented in Python 2.7 using the Flask-Restful framework. All servers are run on <i>localhost</i> (hostname <b>127.0.0.1</b>).


## Launch Instructions
A number of shell scripts are provided for running this file-system in a Linux environment. Each of these will need to be given <i>execute permissions</i>, which can be assigned using the shell command '<b>chmod +x <script_name></b>'. To launch the system in the least time possible, the launch order 1-5 below should be followed.
 
1. <b>install_dependencies.sh</b>

    This script should be run first, since it will install all project dependencies specified in the <i>requirements.txt</i> file.
2. <b>launch_directory_server.sh</b>

    This script launches a directory server on localhost, at URL <b>http://127.0.0.1:5000</b>.
3. <b>launch_locking_server.sh</b>

    This script launches a locking server on localhost, at URL <b>http://127.0.0.1:5001</b>.
4. <b>launch_file_servers.sh</b>

    This script launches a number of file-servers on localhost, which will connect to the directory server if available. The number of file-servers should be specified by the user as <b>$1</b>. Each file-server will then be launched on sequential ports, starting from port <b>45678</b>. This means that the first file-server to be launched will be available at <b>http://127.0.0.1:45678</b>.
5. <b>launch_client.sh</b>

    This script launches a client application, which will connect to the directory and locking servers if they are available. Since the client requires user input, each client should be launched individually in a separate session.





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
* Maintains versioning of the files using integer values, according to the number of times they have been updated by clients. This is a crucial enabling element of the client-side caching.


### Remote File Server
It is possible to have as many file servers as desired in this distributed file-system, since each file server registers with (and is subsequently managed by) the directory server when it is launched.

The file-servers are implemented as a flat-file system, with each storing files in a single directory. This directory uses the naming pattern <b>ServerX</b>, where X is an id assigned to the server when it registers with the directory server. All files stored on a file server follow a simple numerical naming system: for example, <i>0.txt</i> for the first file created on the server.

Each server accepts <i>get()</i> and <i>post()</i> requests from clients. It can be reached at any available host address and port specified by the user, which are provided as <b>sys.argv[1]</b> and <b>sys.argv[2]</b>. Each file-server should be started on a <i>different port number</i>, and this mechanism is provided in the accompanying launch scripts.

* A client wishing to <b>read</b> a remote copy of a file will send a <i>get()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_server_id': server_id
* A client wishing to <b>write</b> to a remote copy of a file will send a <i>post()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_contents': file_contents

<b>Notes:</b> 
* The fileserver does not hold any versioning information about the files that it stores: it is the directory server which handles this. Versioning is used as part of the caching mechanism.
* The client is able to identify the values of 'file_id' and 'file_server_id' by consulting the directory server for the file mapping it requires.




## Locking Service
A locking service provides concurrency control for multiple clients requiring access to the same files. It allows clients exclusive access to files under particular conditions.

A client must request and successfully acquire a single lock for a file in order to perform a restricted-access operation (such as a write). This means that for all writes in the distributed file-system, the request must first be routed through a <b>locking server</b> before access to the remote copy is granted.

### Locking Server
There is one locking server in this distributed file-system, called <b><i>LockingServer.py</i></b>. It manages the operation of locking and unlocking files as requested by clients. It is accessible at URL endpoint http://127.0.0.1:5001/. Any requests for a read or write on a remote file copy must first be routed through this service for approval.

Each file which exists on a remote file-server will have a corresponding record with the locking server. This record exists as a lookup-table, where each entry is a [file_id, is_locked] pair.
* Any client wishing to write to a file must request the lock for that file. They will not be granted the lock until the file is no longer locked. 
* Any client who is granted the lock for a file, will have their client_id stored with the locking server's records for that file. This prevents a client who didn't lock the file originally, from releasing the lock on the file.
  * <b>However</b>, a safety mechanism in the form of a timeout (<b>60 seconds</b>) is used to guard against infinite waiting for a lock to be released. After the timeout has elapsed, if the file is still locked, it will be assumed that the client who locked it has died and the lock is released by the server itself.
* Any client wishing to read a file, will not be able to read it until it is unlocked. However, in the client library there are no cases where a read request requires the acquisition of a lock - the file simply should not be readable until it is no longer locked by another client.

<b>Notes</b>:
* <i><b>Assumption</i></b>: when a remote copy is created for the first time on a file-server, it doesn't need to be locked (nobody will try to concurrently access the file until after it has been created).
* 




## Client-side Caching
A caching solution in a system allows for quicker access time to files if used effectively. It involves the local storage of up-to-date copies of files, so that if the remote copy of a file hasn’t changed since the last time it was accessed, it can be read locally rather than requiring a request over the network. By using caching, the performance of a system can be enhanced since the servers are likely to have less loading at a given time. However, if not implemented appropriately on the client-side it can introduce unnecessary runtime overheads.

In general, it is most efficient to use caching on the client-side to reduce the number of relatively-slow calls required over the network – particularly in the case of file reads. Concerns such as cache invalidation for out-of-date copies of cached files, and an eviction policy in order to keep the contents of the cache relevant and small in number, are important to consider.

### Cache
A custom-implemented cache called <b><i>ClientCache.py</i></b> is used to provide client-side caching in this distributed file-system. An individual cache is created for each client during initialisation: this allows each client to cache the files that they access most often close by and up-to-date. The cache uses a look-up table with a maximum number of entries, whose contents are managed using (i) file versioning, and (ii) a Least-Recently-Used (LRU) cache eviction policy.

Operations implemented in the cache include: adding entries, updating entries, finding entries, evicting entries, and clearing the cache upon exit. Each cache entry looks similar to:

  <b>{'file_contents': file_contents, 'file_version': file_version, 'file_name': file_name, 'timestamp' timestamp}</b>

The timestamp is used to determine the age of the file, and the version is used to determine whether the entry is up-to-date with the remote copy at any given time.

The benefit of the cache is the reduction in volume of traffic going over the network, as well as more instantaneous access to files in many cases. As an NFS implementation, the benefits of this are most clearly seen when performing read operations.

1.	<b>Read</b>: 
  The cache is checked for an entry corresponding to the file to be read.
  * If there exists a corresponding entry, then the version is checked against that recorded with the directory server.
  * If the cache copy is of an outdated version of the file, then a request is made to the file-server on which the remote copy is stored to provide the most up-to-date copy of the file. 
  * If the copy in the cache is up-to-date with the remote copy, the copy from the cache is used. This results in two fewer network accesses: one saving by not needing to request the file from the file-server, and another by the file-server not needing to service an extra request.
2.	<b>Write</b>:
3.	<b>Open</b>: since the file-system is implemented to replicate the NFS model, there are no calls across the network for the open operation, and the file as it exists in the cache is simply displayed in read-only mode.

<b>LRU Eviction Policy</b>: The Least-Recently Used cache eviction policy enforces a maximum number of cache entries at any particular time. This allows the cache to be indexed more quickly, and keeps the contents maximally relevant to the needs of the client it is associated with. 
* In this implementation, <b>a maximum of 10 entries</b> can be stored in the cache at any given time. This empirically selected value could easily be increased or decreased depending on the requirements of this cache in practise.
* Once the cache is full, the client will not be able to add another entry until the least-recently used entry has been evicted. The least-recently used entry is determined by the timestamp of the entry, which corresponds to the last time at which the cache entry was updated.



## Dependencies
* Python 2.7.9
* flask
* flask-restful
* requests
* werkzeug


## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server. However I realised after some time that the Restful approach was a lot simpler, abstracting away the low-level implementation details and allowing me to get on with the feature implementation.
