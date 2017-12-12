# DistributedFileSystem
<b>Amber Higgins, M.A.I. Computer Engineering, 13327954</b>

A distributed Network File System (NFS) implementation with:
1.	Distributed transparent file access
2.	Directory service
3.	Locking service
4.	Client-side caching

Implemented in Python using the Flask Restful framework. Communication is through HTTP in JSON format.


## Distributed Transparent File Access
The system operates according to the Network File System (NFS) model. It can support multiple connected clients, and multiple fileservers. It deals exclusively with .txt files.

### Client Library
All file accesses are made through a client library called <i>ClientApi.py</i>. This library is the interface exposed to the client-side application for manipulation of the local and remote file-systems. By using the library, the under-the-hood implementation details of the distributed file-system are hidden from the user.

Clients can:
* Access remote copies of files stored on file-servers through the <i>read</i> and <i>write</i> function calls. They can also create new files, and open existing files locally.
* Interact with file contents through the system editor, which is launched before every remote write and after every remote read.

A subtle point here is that <i>in order to 'open' a file in read-only mode, the contents of the file are displayed in the console window.</i> Opening the file in the text editor would give an individual the option to edit the file when they should really just be able to view the contents - an undesirable behaviour that is resolved by this approach.

### Client application
This application provides a simple interface to a user, offering options to manipulate files. This includes reading, writing, opening and creating text files. When a text file is created for the first time, the specified directory is automatically created if it doesn’t already exist.

All files on the local filesystem are visible to every client. However, each client implements its own cache.

In the background, the user's choices when interacting with the system are routed through the client library to the appropriate services (e.g. cache, locking server, directory server, file server), providing abstraction from the underlying technical implementation.


## Directory Service
A directory service has the function of converting human-readable file names displayed to a client, into non-verbose file identifiers on remote file servers. It acts as a namespace for the system that maps a unique filename (from which the client can be identified) to a unique file identifier (from which the remote file server can be identified) – an intermediary between the client and the remote file servers.

### Directory Server
There is one directory server located at a known address of <b>http://127.0.0.1:5000/</b>. This server acts as a management application for the distributed file-system.  The directory server maintains a record of the mappings of full client-side file names to enumerated file identifier mappings on the remote servers.

Amongst other responsibilities, it:
* Provides a registration mechanism for -
  * Client applications, at URL endpoint <b>http://127.0.0.1:5000/register_client</b>
  * File servers, at URL endpoint <b>http://127.0.0.1:5000/register_fileserver</b>
  
  including the assignment of unique ids to each;
* Records connection details for clients and file servers;
* Load-balances connected file-servers, such that at any time the least-loaded server will be given any new loading;
* Maintains records of client-fileserver file-directory mappings, where clients provide a full file path (e.g. ../Client0/hello.txt) and this is mapped to a unique server-side identifier in the server’s root directory (e.g. ../Server10/18.txt).
* Maintains versioning of the files as an integer value, according to the number of times they have been updated by clients. This is a crucial element of the client-side caching.



### Remote File Server
It is possible to have as many file servers as desired in this distributed file-system, since each file server registers with the directory server when it is launched.

The file-servers are implemented as a flat-file system, with each storing files in a single directory. This directory uses the naming pattern <b>ServerX</b>, where X is an id assigned to the server when it registers with the directory server. All files stored on a file server follow a simple numerical naming system: for example, <i>0.txt</i> for the first file created on the server.

Each server accepts <i>get()</i> and <i>post()</i> requests from clients. It can be reached at any available host address and port specified by the user, which are provided as <b>sys.argv[1]</b> and <b>sys.argv[2]</b>. <i>Each file-server should be started on a different port number.</i>

* A client wishing to <b>read</b> a remote copy of a file will send a <i>get()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_server_id': server_id
* A client wishing to <b>write</b> to a remote copy of a file will send a <i>post()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_contents': file_contents

<b>Note:</b> The fileserver does not hold any versioning information about its files: it is the directory server which handles this.

## Locking Service
A locking service provides concurrency control for multiple clients requiring access to the same files. It allows clients exclusive access to files under particular conditions.

A client must request and successfully acquire a single lock for a file in order to perform a restricted-access operation (such as a write). This means that for all writes in the distributed file-system, the request must first be routed through a <b>locking server</b> before access to the remote copy is granted.

### Locking Server
There is one locking server in the distributed file-system. It manages the operation of locking and unlocking files as requested by clients. It is accessible at URL endpoint http://127.0.0.1:5001/. Any requests for a read or write on a remote file copy must first be routed through this service for approval.

Each file which exists on a remote file-server will have a corresponding record with the locking server. This record exists as a lookup-table, where each entry is a [file_id, is_locked] pair.
* Any client wishing to write to a file must request the lock for that file. They will not be granted the lock until the file is no longer locked.
  * <b>However</b>, a safety mechanism in the form of a timeout (<b>60 seconds</b>) is used to guard against infinite waiting for a lock to be released. After the timeout has elapsed, if the file is still locked, it will be assumed that the client has died and the lock is removed.
* Any client wishing to read a file, will not be able to read it until it is unlocked.

<i><b>Assumption</b>: the implementation assumes that when a remote copy is created for the first time on a file-server, it doesn't need to be locked (nobody will try to concurrently access the file until after it has been created).</i>


## Client-side Caching
A caching solution in a system allows for quicker access time to files if used effectively. It involves the local storage of up-to-date copies of files, so that if the remote copy of a file hasn’t changed since the last time it was accessed, it can be read locally rather than requiring a request over the network. By using caching, the performance of a system can be enhanced since the servers are likely to have less loading at a given time. However, if not implemented appropriately on the client-side it can introduce unnecessary runtime overheads.

In general, it is most efficient to use caching on the client-side to reduce the number of relatively-slow additional calls required over the network, in particular reducing the network access required for a file read. Concerns such as cache invalidation for out-of-date copies of cached files, and an eviction policy in order to keep the contents of the cache relevant and small in number, are important to consider.

### Cache
The cache is custom-implemented, and an individual cache is created for each client when it launches in order to simplify dealing with conflicts. This cache is a look-up table with a maximum number of entries, whose contents are managed using <b>file versioning</b> and a <b>Least-Recently-Used (LRU) cache eviction policy</b>.

Operations on the cache include: adding entries, updating entries, finding entries, evicting entries, and clearing the cache upon exit.
The cache is used by the Client API in order to reduce the amount of traffic going over the network. As an NFS implementation, the benefits of this are most clearly seen when performing read operations.
1.	<b>Read</b>: the cache is checked for an entry corresponding to the file to be read, and if there exists an entry then the version is checked against that recorded with the fileserver. If the client-side copy has an outdated version, then the call is made to the fileserver to fetch the most up-to-date copy of the file. Otherwise, the copy from the cache is used.
2.	<b>Write</b>:
3.	<b>Open</b>: since the file-system is implemented to replicate the NFS model, there are no calls across the network for the open operation, and the file as it exists in the cache is simply displayed in read-only mode.

<b>TODO finish this</b>.


## Dependencies
* Python 2.7.9
* flask, flask_restful
* requests
*

## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server. However I realised after some time that the Restful approach was a lot simpler, abstracting away the low-level implementation details and allowing me to get on with the feature implementation.