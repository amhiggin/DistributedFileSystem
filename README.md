# DistributedFileSystem
Network File System (NFS) distributed file management system implementation with:
1. Distributed transparent file access
2. Locking
3. Caching
4. Directory mapping

Implemented in Python using the Flask Restful framework. 
Requests are sent in JSON format through HTTP get, post, put, delete requests as appropriate.


## Transparent File Access
The system is implemented to replicate the operation of the Network File System (NFS) model. It can support multiple connected clients, and multiple fileservers. 
* All file accesses are made through a client library called <i>ClientApi.py</i>. This library is the interface exposed to the client-side application for manipulation of the local and remote filesystems.
* Clients can connect to fileservers through methods read, write, open and close. They can also create new directories locally. 
* Clients can interact with file contents through the system editor, which is launched before every remote write and after every remote read.
* On the server side, there is a flat file-storage structure since every file is given a unique numerical name. 


## Directory Mapping
The directory server is located at a known address of <b>http://127.0.0.1:5000/</b>. This server acts as a management application for the distributed filesystem.
The functions of this server are to:
* Register new client instances once they are created, assigning a <i>client_id</i> property to each. Each client can register with the directory server at the url handle <b>http://127.0.0.1:5000/register_client</b>.
* Register new fileserver instances once they are created, assigning a <i>file_server_id</i> property to each. Each fileserver can register with the directory server at the url handle <b>http://127.0.0.1:5000/register_fileserver</b>.
* Load-balance all registered servers, such that at any time the least-loaded server will be given any new loading.
* Mapping of client-local filenames to remote server filenames, where the client provides the full path of the file (e.g. <i>../Client0/hello.txt</i>) and this is mapped to a unique server-side identifier (e.g. <i>../Server10/18.txt</i>).

## Locking Service
The locking server is located at a known address of <b>http://127.0.0.1:5001/</b>. Any requests for a read/write must first be routed through this service for approval.
* Any client wishing to write to a file, waits until the file is not locked before acquiring the lock. Note: the implementation assumes that when a remote copy is created on a server, that the remote file doesn't need to be locked (nobody will access until it has been created).
* Any client wishing to read a file, will not be able to read it until it is unlocked. 

A safety mechanism in the form of a timeout (50000) is used to guard against infinite waiting for a lock to be released. <b>FIXME: this really only works effectively for the reading, since we can't grab the lock for the case of writing.</b>

## Caching Mechanism
<b>TODO implement</b>

The caching mechanism is part of the client-side application, since this is the most effective strategy for caching in an NFS system.
The cache is a custom implementation (<b>TODO figure out what the persistence model is</b>), with operations to add to, remove from, update, and clear the cache. <b>TODO figure out if there are any more operations to be added</b>.
* <b>Read</b>: the cache is checked for an entry corresponding to the file to be read, and if there exists an entry then the version is checked against that recorded with the fileserver. If the client-side copy has an outdated version, then the call is made to the fileserver to fetch the most up-to-date copy of the file. Otherwise, the copy from the cache is used.
* <b>Write</b>: 
* <b>Open</b>: since the file-system is implemented to replicate the NFS model, there are no calls across the network for the open operation, and the file as it exists in the cache is simply displayed in read-only mode. <b>TODO implement the read-only part</b>


## Dependencies
* Python 2.7.9
* Flask
* Flask_Restful
* requests

## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server.
* However I realised after some time that the Restful approach was a lot simpler.
