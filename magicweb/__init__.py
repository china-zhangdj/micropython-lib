import json
import os
import socket
import time
import _thread

MIME_TYPES = {
    'css': 'text/css',
    'html': 'text/html',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'js': 'text/javascript',
    'json': 'application/json',
    'rtf': 'application/rtf',
    'svg': 'image/svg+xml',
    'ico': 'application/ico',
    'bin': "file/bin"
}

class request :
    def __init__(self):
        '''
        请求对象
        :param path: 请求路径
        :param method: 请求方法
        :param head: 请求头
        :param body: 请求体
        '''
        self.method = None
        self.path = None
        self.head = None
        self.body = None

    def procParams(self):
        '''
        处理请求参数 GET POST
        :return: 请求参数处理结果
        '''
        if self.method == "POST" :
            params = self.body.decode().split("&")
        elif self.method == "GET" :
            params = self.path.split("?")
        else:
            params = []
        params_res = {}
        for i in params:
            spl = i.split("=")
            if len(spl) == 2:
                params_res[spl[0]] = spl[1]
        return params_res

    @property
    def json(self):
        try :
            return json.dumps(self.body)
        except Exception as e :
            return None

class BaseResponse:
    def __init__(self,status_code:int=500,head:dict={},body:bytes=b''):
        self.status_code = status_code
        self.head = head
        self.body = body

class CodeResponse:
    def __init__(self,code:int,message=""):
        self.status_code = code
        self.head = {}
        self.body = '''<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>{}</title>
            </head>
            <body>
            <h1>Response Code : {}</h1>
            <h1>Message : {}</h1>
            </body>
            </html>'''.format(code,code,message).encode()


class FileResponse(BaseResponse):
    def __init__(self,status_code:int,fpath:str,head:dict={}):
        super(FileResponse, self).__init__()
        self.read_finish = False
        self.head = head
        self.status_code = status_code
        fname = fpath.split("/")[-1]
        fsplit = fname.split(".")
        fsplen = len(fsplit)
        if fsplen == 1:
            extension = "bin"
        else:
            extension = fsplit[-1]
        if extension in MIME_TYPES.keys():
            self.head['Content-Type'] = MIME_TYPES[extension]
        else:
            self.head['Content-Type'] = "application/file"

class MagicWEB:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    # 响应状态码
    OK = b"200 OK"
    NOT_FOUND = b"404 Not Found"
    FOUND = b"302 Found"
    FORBIDDEN = b"403 Forbidden"
    BAD_REQUEST = b"400 Bad Request"
    ERROR = b"500 Internal Server Error"

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.debug = False
        self.routes_dict = {}
        self.__client_dict = {}
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((address,port))
        self.sock.listen(10)
        self.control = False
        _thread.start_new_thread(self.__server,())


    #BACKEND SERVER METHODS
    def setRoutes(self, routes={}):
        '''
        设置路由表
        :param routes:
        :return:
        '''
        self.routes_dict = routes

    def addRouters(self,routers:dict={}):
        '''
        添加路由
        :param routers:
        :return:
        '''
        self.routes_dict.update(routers)

    def start(self):
        '''
        开启服务线程
        :return: None
        '''
        self.control = True
        print("MyltyWeb web server started...")
        print("version: v1.2.0")
        print("*"*20)

    def __server(self):
        while True :
            if self.control :
                cli,addr = self.sock.accept()
                _thread.start_new_thread(self.__router,(cli,))
            else:
                time.sleep(1)
        pass

    def __router(self,client):
        recv = client.recv(1024)
        req = self.__processRequest(recv,client)  # type:request
        print("[{}] : {}".format(req.method,req.path))
        # 有请求方法
        if req.method != None :
            # 已声明，执行请求方法
            reqpath = req.path.split("?")[0]
            if reqpath in self.routes_dict.keys():
                response = self.routes_dict[reqpath](req)
                self.__send_response(client,response)
            # 未声明,按文件取
            else:
                path = "./static/" + reqpath[1:]
                response = FileResponse(200,path)
                try :
                    f = open(path,"rb")
                    length = os.stat(path)[6]
                    response.head["Content-Length"] = "{}".format(length)
                    self.__sendStatus(client, status_code=response.status_code)
                    self.__sendHeaders(client, headers_dict=response.head)
                    # self.__sendBody(client, body_content=response.body)
                    client.send(b'\n')
                    while True :
                        buf = f.read(102400)
                        if buf :
                            client.send(buf)
                        else:
                            break
                    client.send(b'\n\n')
                    f.close()
                    self.__send_response(client,response)
                except Exception as e:
                    self.__send_response(client,CodeResponse(404,str(e)))
        # 没有请求方法
        else:
            self.__send_response(client,CodeResponse(500))
        pass

    def __processRequest(self,reqdata,client) -> request:
        '''
        处理请求
        :return: request对象
        '''
        try :
            request_line, rest_of_request = reqdata.split(b'\r\n', 1)
            request_line = request_line.decode().strip().split(' ')
        except ValueError :
            self.render(client,self.NOT_FOUND,status=self.NOT_FOUND)
            pass
        # 处理请求行
        req = request()
        if len(request_line) > 1:
            req.method = request_line[0]
            req.path = request_line[1]
            req.version = request_line[2]
        req.head = {}
        raw_headers, body = rest_of_request.split(b'\r\n\r\n', 1)
        raw_headers = raw_headers.split(b'\r\n')
        # 拆分请求头
        for header in raw_headers:
            split_header = header.decode().strip().split(': ')
            req.head[split_header[0]] = split_header[1]
        # 处理请求体
        req.body = body
        return req

    def __sendStatus(self,client,status_code:int):
        '''
        发送HTTP响应状态码
        :param status_code: 状态码
        :return:
        '''
        response_line = b"HTTP/1.1 "
        client.send(response_line + "{}".format(status_code).encode() + b'\n')

    def __sendHeaders(self,client,headers_dict:dict={}):
        '''
        发送HTTP响应头
        :param headers_dict: 响应头数组
        :return:
        '''
        for key, value in headers_dict.items():
            client.send(b"%s: %s\n" % (key.encode(), value.encode()))

    def __sendBody(self,client,body_content:bytes):
        '''
        发送HTTP响应体
        :param body_content:
        :return:
        '''
        client.send(b'\n' + body_content + b'\n\n')
        client.close()

    def __send_response(self,client,response:BaseResponse):
        '''
        发送响应对象
        :param client: client 套接字
        :param response: 响应对象
        :return:
        '''
        self.__sendStatus(client, status_code=response.status_code)
        self.__sendHeaders(client, headers_dict=response.head)
        self.__sendBody(client, body_content=response.body)

