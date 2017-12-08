# DistributedFileSystem
<b>Amber Higgins, M.A.I. Computer Engineering, 13327954</b>

Network File System (NFS) distributed file management system implementation with:
1. Distributed transparent file access
2. Locking
3. Caching
4. Directory mapping

Implemented in Python using the Flask Restful framework. Requests are sent in JSON format through HTTP get, post, put, delete requests.


## Distributed Transparent File Access
The system operates according to the Network File System (NFS) model. It can support multiple connected clients, and multiple fileservers. 

### Client Library
All file accesses are made through a client library called <i>ClientApi.py</i>. This library is the interface exposed to the client-side application for manipulation of the local and remote filesystems. By using the library, the under-the-hood implementation details of the distributed filesystem are hidden from the user.
Clients can
* Connect to fileservers through methods read, write, open and close. They can also create new directories locally. 
* Interact with file contents through the system editor, which is launched before every remote write and after every remote read.

### Client application
This application provides a simple interface to a user, offering options to manipulate files. This includes reading, writing, opening, and closing text files, as well as creating new directories.

In the background, the user's choices when interacting with the system are routed through the client library to the appropriate services in order to provide an optimal distributed file-system backend.


## Directory Service
A directory service has the function of converting human-readable file names displayed to a client, into non-verbose file identifiers on remote file servers. It acts as an intermediary between the client applications and the file servers, and can be thought of as a namespace for the network that maps a unique filename (from which the client can be identified) to a unique file identifier (from which the remote file server can be identified).

### Directory Server
The directory server is located at a known address of <b>http://127.0.0.1:5000/</b>. This server acts as a management application for the distributed filesystem.  The directory server to maintains a record of the mappings of full client-side file names to enumerated file identifier mappings on the remote servers.

Amongst other responsibilities, it
* Provides a registration mechanism for 
  * Client applications, at URL handle <b>http://127.0.0.1:5000/register_client</b>
  * File servers, at URL handle <b>http://127.0.0.1:5000/register_fileserver</b>.
  
  including the assignment of unique ids;
* Records connection details for clients and file servers;
* Load-balances connected file-servers, such that at any time the least-loaded server will be given any new loading;
* Maintains records of client-fileserver file mappings, where clients provide a full filepath (e.g. <i>../Client0/hello.txt</i>) and this is mapped to a unique server-side identifier (e.g. <i>../Server10/18.txt</i>).


### File Server
The file servers are implemented as a flat-file system, with each storing files in a single directory. This directory uses the naming pattern <b>ServerX</b>, where X is an id assigned to the server when it registers with the directory server.

All files stored on a file server follow a simple numerical naming system such as <i>0.txt</i> for the first file created on the server. 

The server accepts <i>get()</i> and <i>post()</i> requests from connecting clients. It can be reached at any available host address and port specified by the user, which are provided as sys.argv[0] and sys.argv[1].
* A client wishing to <b>read</b> a remote copy of a file will send a <i>get()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_server_id': server_id
* A client wishing to <b>write</b> to a remote copy of a file will send a <i>post()</i> request. The client must provide JSON parameters:
  * 'file_id': file_id
  * 'file_contents': file_contents

## Locking Service
The locking server is located at a known address of <b>http://127.0.0.1:5001/</b>. Any requests for a read/write must first be routed through this service for approval.
* Any client wishing to write to a file, waits until the file is not locked before acquiring the lock. Note: the implementation assumes that when a remote copy is created on a server, that the remote file doesn't need to be locked (nobody will access until it has been created).
* Any client wishing to read a file, will not be able to read it until it is unlocked. 

A safety mechanism in the form of a timeout (50000) is used to guard against infinite waiting for a lock to be released. <b>FIXME: this really only works effectively for the reading, since we can't grab the lock for the case of writing.</b>

## Caching Mechanism
<b>TODO implement</b>

The caching mechanism is part of the client-side application, since this is the most effective strategy for caching in an NFS system. A separate cache is created for each client, in order to simplify dealing with conflicts.
The cache is a custom implementation (<b>TODO figure out what the persistence model is</b>), with operations to add to, remove from, update, and clear the cache. <b>TODO figure out if there are any more operations to be added</b>.
* <b>Read</b>: the cache is checked for an entry corresponding to the file to be read, and if there exists an entry then the version is checked against that recorded with the fileserver. If the client-side copy has an outdated version, then the call is made to the fileserver to fetch the most up-to-date copy of the file. Otherwise, the copy from the cache is used.
* <b>Write</b>: 
* <b>Open</b>: since the file-system is implemented to replicate the NFS model, there are no calls across the network for the open operation, and the file as it exists in the cache is simply displayed in read-only mode. <b>TODO implement the read-only part</b>


## Dependencies
* Python 2.7.9
* flask, flask_restful
* requests
*

## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server.
* However I realised after some time that the Restful approach was a lot simpler.
