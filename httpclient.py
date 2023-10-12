#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Shalomi Hron
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Note: just the code number, not the full status code message
        code = int(self.get_headers(data).split()[1])
        return code

    def get_headers(self,data):
        # Full message header
        headers = data.split("\r\n")[0]
        return headers

    def get_body(self, data):
        # Full message body. Note: may be empty.
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    # Note: new method
    def parseURL(self, url):
        # Obtain the host, port, and path.
        # Need path, host for the request itself. Need host, port to make the connection.
        pURL = urllib.parse.urlparse(url)

        print("pUrl: {}".format(pURL)) # TODO: remove

        hostAndPort = pURL.netloc.split(":")

        # Take care of unspecified ports
        if len(hostAndPort) < 2:
            host = hostAndPort[0]
            port = 80 # default port for TCP and HTTP
        else:
            host = pURL.netloc.split(":")[0]
            port = pURL.netloc.split(":")[1]
        
        # Get or correct path
        path = pURL.path
        if len(path) < 1:
            path = "/"

        # TODO: remove
        # try:
        #     host = pURL.netloc.split(":")[0]
        #     port = pURL.netloc.split(":")[1]
        #     path = pURL.path
        #     if len(path) < 1:
        #         path = "/"
        # except Exception as e:
        #     print("testInternetGets Error: {}\n".format(e))
        #     host = "127.0.0.1"
        #     port = 8080
        #     path = "/"

        return path, host, port


    def GET(self, url, args=None):
        # TODO: remove
        print("\nGET function ....")
        #print("url: {}".format(url))
        #print("args: {}".format(args))

        # Parse the url
        path, host, port = self.parseURL(url)

        # Connect to socket, send the request, and close
        self.connect(host, int(port))
        request = "GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        self.sendall(request) # Note: sendall doesn't need send and shutdown SHUT_WR
        received = self.recvall(self.socket)
        self.close()

        # Obtain the code and body
        code = 500
        body = ""
        code = self.get_code(received)
        body = self.get_body(received)
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        # TODO: remove
        print("\nPOST function ....")
        # print("url: {}".format(url))
        # print("args: {}".format(args))

        # Parse the url
        path, host, port = self.parseURL(url)
        
        # Connect to socket
        self.connect(host, int(port))

        # Format the request (note Connection: close), and encode the data to be posted
        if not args:
            args = ""
            data = urllib.parse.urlencode(args)
        else:
            data = urllib.parse.urlencode(args)
        length=str(len(data))

        request = "POST "+path+" HTTP/1.1\r\nHost: "+host+"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+length+"\r\nAccept: */*\r\nConnection: close\r\n\r\n"+data
        self.sendall(request) # Note: sendall doesn't need send and shutdown SHUT_WR
        received = self.recvall(self.socket)
        self.close()

        # Obtain the code and body
        code = 500
        body = ""
        code = self.get_code(received)
        body = self.get_body(received)
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
