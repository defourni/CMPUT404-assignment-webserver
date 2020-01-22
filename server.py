#  coding: utf-8 
import socketserver
import mimetypes
import sys

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

#----------------------------------------------------------------------

#Copyright 2020 Dexter Fournier
#
#  handleGet() and sendFile() methods:
#     -used for handling HTTP GET requests on localhost server.
#
#Licensed under the Apache License, Version 2.0 (the "License");   
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

    #http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

class MyWebServer(socketserver.BaseRequestHandler):
    def sendFile(self,f,mimetype):
        #method used to properly send html and css files with HTTP headers.
        data = bytearray(f.read(),'utf-8')
        length = len(data)
        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type:"+mimetype[0]+"\r\nContent-Length: " + str(length) +"\r\nConnection: Closed\r\n\r\n",'utf-8'))
        self.request.sendall(data)
    
    def handleGet(self):
        self.path = 'www' + self.reqType[1]
        #protection from accessing other dirs
        if("/../" in self.path):
            #this can be anything that is not a file in the root directory - as long as the open() will fail.
            self.path = "bad-path"
        try:
            f = open(self.path,'r')
            
        except IOError as e:
            
            if(e.args[0] == 2): #no such file
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\n404 Not Found",'utf-8'))
            elif(e.args[0] == 21): #is a directory
                #try and open index.html
                if(self.path[-1] == '/'):
                    try:
                        self.path_html = self.path + "index.html"
                        f = open(self.path_html)
                    except IOError:
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\n404 Not Found",'utf-8'))
                    else:
                        mimetype = mimetypes.guess_type(self.path_html.split("/")[-1])
                        self.sendFile(f,mimetype)
                else:
                    #url is a dir but does not have trailing /
                    try:
                        self.path = self.path + "/index.html"
                        f = open(self.path)
                    except IOError:
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\n404 Not Found",'utf-8'))
                    else:
                        #if index.html could be found, send a 301 with the location including the trailing /
                        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: "+self.path[3:-10]+"\r\n\r\n",'utf-8'))                    
            else:
                #saved for future exceptions
                print("other exception")
        else:
            mimetype = mimetypes.guess_type(self.path.split("/")[-1])
            self.sendFile(f,mimetype)            
        
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.lines = self.data.decode().split('\n')
        self.reqType = self.lines[0].split(" ")
        if(self.reqType[0] == 'GET'):
            #GET Request
            self.handleGet()
        else:
            #Any other Requests (POST,PUT,etc)
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n",'utf-8'))
        
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
