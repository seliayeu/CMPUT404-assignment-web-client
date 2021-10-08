#!/usr/bin/env python3
# coding: utf-8
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
from urllib.parse import urlparse, unquote

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
        status_line = data.split("\n")[0]
        return status_line.split(" ")[1]

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]
    
    # generate an HTTP request with the given method, adding args to body
    # in the case of a POST
    def generate_request(self, method, args=None):
        if method == "GET":
            out = "GET " + str(self.path) + " HTTP/1.1\r\n"
            out += "Host: " + str(self.url) + "\r\n"
            out += "Connection: close\r\n"
            out += "\r\n"
            return out
        elif method == "POST":
            body = ""
            # if there are args then format them as required by the Content-Type
            if args:
                for field, value in args.items():
                    body += unquote(field) + "=" + unquote(value) + "&"
            body = body[0:-1] if body else ""
            out = "POST " + str(self.path) + " HTTP/1.1\r\n"
            out += "Host: " + str(self.url) + "\r\n"
            out += "Content-Type: application/x-www-form-urlencoded\r\n"
            out += "Content-Length: " + str(len(body)) + "\r\n"
            out += "Connection: close\r\n"
            out += "Accept-Charset: UTF-8\r\n"
            out += "\r\n"
            out += body
            out += "\r\n\r\n"
            return out
        else:
            return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
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

    # call send_request with GET and do printing and set up object to return
    def GET(self, url, args=None):
        print("\nGETting content at " + url + " with arguments " + str(args) + "...")
        response = self.send_request(url, args, "GET")
        code = int(self.get_code(response))
        body = self.get_body(response)
        print(response)
        return HTTPResponse(code, body)

    # call send_request with POST and do printing and set up object to return
    def POST(self, url, args=None):
        print("\nPOSTing to " + url + " with arguments " + str(args) + "...")
        response = self.send_request(url, args, "POST")
        code = int(self.get_code(response))
        body = self.get_body(response)
        print(response)
        return HTTPResponse(code, body)

    # send the GET or POST request
    def send_request(self, url, args, method):
        self.parse_url(url)
        self.connect(self.host, self.port)
        self.sendall(self.generate_request(method, args))
        response = self.recvall(self.socket)
        self.close()
        return response

    # parse the specified url and save the various components as 
    # objecet variables
    def parse_url(self, url):
        parsed = urlparse(unquote(url))
        print(parsed)
        self.url = parsed.netloc
        self.path = parsed.path if parsed.path else "/"
        split = self.url.split(":")
        if len(split) == 2:
            self.url = self.host = split[0]
            self.port = int(split[1])
        else:
            self.host = socket.gethostbyname(self.url)
            self.port = 80
        return None

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
