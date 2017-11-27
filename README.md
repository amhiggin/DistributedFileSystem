# DistributedFileSystem
NFS filesystem implementation with distributed transparent file access, locking, caching and directory mapping.
Requests are sent in JSON format through HTTP get, post, put, delete requests as appropriate.
Will eventually be capable of supporting multiple fileservers and multiple clients, with a single locking server and directory server to tie them together.

## Dependencies
* Flask
* Flask_Restful
* TODO add the rest

## Notes
* Originally, I had implemented the fileserver communications with the client application using sockets. I was also starting to work on a locking server.
* However I realised after some time that the Restful approach was a lot simpler.
