#  coding: utf-8 
import socketserver
import mimetypes

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handleGet(self):
        self.path = 'www' + self.reqType[1]
        if("/../" in self.path):
            self.path = "bad-path"
        try:
            f = open(self.path,'r')
            print(self.path)
            
        except IOError as e:
            if(e.args[0] == 2): #no such file
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
            elif(e.args[0] == 21): #is a directory
                #try and open index.html
                if(self.path[-1] == '/'):
                    try:
                        self.path = self.path + "index.html"
                        f = open(self.path)
                    except IOError:
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
                    else:
                        mimetype = mimetypes.guess_type(self.path.split("/")[-1])
                        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type: "+mimetype[0]+"\r\n",'utf-8'))
                        self.request.sendall(f.read().encode('utf-8'))
                else:
                    try:
                        self.path = self.path + "/index.html"
                        f = open(self.path)
                    except IOError:
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
                    else:
                        mimetype = mimetypes.guess_type(self.path.split("/")[-1])
                        self.request.sendall(bytearray("HTTP/1.1 301 Redirect\r\nContent-Type: "+mimetype[0]+"\r\n",'utf-8'))
                        self.request.sendall(f.read().encode('utf-8'))                    
            else:
                #saved for future exceptions
                self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n\r\n",'utf-8'))
        else:
            mimetype = mimetypes.guess_type(self.path.split("/")[-1])
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type: "+mimetype[0]+"\r\n",'utf-8'))
            self.request.sendall(f.read().encode('utf-8'))            
            
            
        
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.lines = self.data.decode().split('\n')
        self.reqType = self.lines[0].split(" ")
        if(self.reqType[0] == 'GET'):
            self.handleGet()
        else:
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n",'utf-8'))
        
        #print (self.reqType)
        
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
