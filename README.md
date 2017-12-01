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
* Clients can connect to a fileserver through methods such as read, write, open and close. They can also create new directories locally. The default system text editor is also used to open the file before a write occurs, and after a read occurs.
* All file accesses are made through a client library called <i>ClientApi.py</i>. This library is the interface exposed to the client-side application for manipulation of the local and remote filesystems.
* On the server side, there is a flat file-storage structure since every file is given a unique numerical name. 


## Directory Mapping
The directory server is located at a known address of <b>http://127.0.0.1:5000/</b>. This server acts as a management application for the distributed filesystem.
The functions of this server are to:
* Register new client instances once they are created, assigning a <i>client_id</i> property to each. Each client can register with the directory server at the url handle <b>http://127.0.0.1:5000/register_client</b>.
* Register new fileserver instances once they are created, assigning a <i>file_server_id</i> property to each. Each fileserver can register with the directory server at the url handle <b>http://127.0.0.1:5000/register_fileserver</b>.
* Load-balance all registered servers, such that at any time the least-loaded server will be given any new loading.
* Mapping of client-local filenames to remote server filenames, where the client provides the full path of the file (e.g. <i>../Client0/hello.txt</i>) and this is mapped to a unique server-side identifier (e.g. <i>../Server10/18.txt</i>).

## Locking Service
* Any client wishing to write to a file, waits until the file is not locked before acquiring the lock. Note: the implementation assumes that when a remote copy is created on a server, that the remote file doesn't need to be locked (nobody will access until it has been created).
* Any client wishing to read a file, will not be able to read it until it is unlocked. <b>TODO review this.</b>

## Caching Mechanism
* <b>TODO implement</b>


## Dependencies
* Flask
* Flask_Restful
* TODO add the rest

## Additional Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server.
* However I realised after some time that the Restful approach was a lot simpler.
