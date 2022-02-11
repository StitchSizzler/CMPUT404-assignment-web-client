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
        try:
            code = int(data.splitlines()[0].split()[1])
        except:
            code = None
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        try: 
            body = data.split("\r\n\r\n")[1]
        except:
            body = ""
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

    def get_host(self, urlParsed):
        try:
            if ":" in urlParsed.netloc:
                return urlParsed.netloc.split(":")[0]
            else:
                return socket.gethostbyname(urlParsed.netloc)
        except:
            return None

    def parse_url(self, url):
        urlParsed = urllib.parse.urlparse(url)
        urlParams = (url + "?").split("?")[1].split('#')
        urlQuery = urlParams[0]
        urlFragm = ""
        if (len(urlParams) > 1):
            urlFragm = urlParams[1]

        urlDetails = {
            "host": urlParsed.hostname,
            "path": urlParsed.path,
            "port": urlParsed.port,
            "query": urlQuery,
            "fragm": urlFragm
        }

        if urlDetails["path"] == "":
            urlDetails["path"] = "/"
        if not urlDetails["port"]:
            urlDetails["port"] = 80

        return urlDetails

    def GET(self, url, args=None):
        code = 500
        body = ""
        request = ""
        data = ""
        urlDetails = self.parse_url(url)
        host = urlDetails["host"]
        path = urlDetails["path"]
        port = urlDetails["port"]
        query = urlDetails["query"]
        fragm = urlDetails["fragm"]

        if query:
            path = path + "?" + query
        if fragm:
            path = path + "#" + fragm

        request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
        self.connect(host, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)

        sys.stdout.write(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        request = ""
        data = ""
        urlDetails = self.parse_url(url)
        host = urlDetails["host"]
        path = urlDetails["path"]
        port = urlDetails["port"]
        query = urlDetails["query"]
        fragm = urlDetails["fragm"]

        if fragm:
            path = path + "#" + fragm

        if args:
            for (key, value) in args.items():
                body += key + "=" + value + "&"
        if query:
            queryList = urlDetails.split("&")
            for item in queryList:
                key = item.split("=")[0]
                value = item.split("=")[1]
                body += key + "=" + value + "&"
        body = body[:-1]

        request = "POST " + path + " HTTP/1.1\r\nHost: " + host + "\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: " + str(len(body)) + " \r\nUser-Agent: Mozilla/5.0\r\n"
        request += "Connection: close\r\n\r\n" + body + "\r\n\r\n"

        self.connect(host, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)

        sys.stdout.write(body)
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
